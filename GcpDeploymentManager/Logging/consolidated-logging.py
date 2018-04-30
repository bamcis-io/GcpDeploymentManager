import copy

def GenerateConfig(context):
	"""Generates config."""

	parent_type = ''
	parent_id = ''
	includeChildren = False
	createSink = "sink" in context.properties and context.properties["sink"] is not None and context.properties["sink"] != ""
	pubsub_topic_name = context.properties["topic"]
	sa_name = context.properties["service-account"]
	sa_display_name = ""

	if "service-account-display-name" in context.properties and context.properties["service-account-display-name"] is not None and context.properties["service-account-display-name"] != "":
		sa_display_name = context.properties["service-account-display-name"]
	else:
		sa_display_name = sa_name

	resources = [ 
		{
			"name": sa_name,
			"type": "iam.v1.serviceAccount",
			"properties": {
				"accountId": sa_name,
				"displayName": sa_display_name,
				"projectId": context.env["project"]
			}
		},
		{
			"name": sa_name + "-key",
			"type": "iam.v1.serviceAccounts.key",
			"properties": {
				"parent": "$(ref." + sa_name + ".name)"
			},
			"metadata": {
				"dependsOn" :[
					sa_name
				]
			}
		},
		# The topic will always have a gcpIamPolicy property since we will always add the calling service account
		# as a pubsub admin
		{
			'name': pubsub_topic_name,
			'type': 'pubsub.v1.topic',
			'properties': {
				'topic': pubsub_topic_name
			},
			'accessControl': {
				'gcpIamPolicy': MergeServiceAccountWithRoleIntoBindings(context.env, context.properties, ('serviceAccount:{0}@cloudservices.gserviceaccount.com'.format(context.env['project_number'])), "roles/pubsub.admin", "pubsub-topic-iam-policy")
			}
		},
		# The subscription will always have a gcpIamPolicy property since we will always add the consumer account as a pubsub subscriber
		{
			"name": context.properties["subscription"],
			   "type": "pubsub.v1.subscription",
			"properties": {
				"subscription" : context.properties["subscription"],
				"topic": "$(ref." + pubsub_topic_name + ".name)"
			},
			"accessControl" : {
				"gcpIamPolicy": MergeServiceAccountWithRoleIntoBindings(context.env, context.properties, "serviceAccount:{0}@{1}.iam.gserviceaccount.com".format(sa_name, context.env["project"]), "roles/pubsub.subscriber", "pubsub-subscription-iam-policy")
			},
			"metadata": {
				"dependsOn": [
					pubsub_topic_name,
					sa_name
				]
			}
		},
		{
			"name": "project-pubsub-policy",
			"type": "policy.py",
			"properties": {
				"type": "project",
				"id": context.env["project"],
				"policy": { 
					"add": [
						{
							"role": "roles/pubsub.viewer",
							"members": [
								"serviceAccount:$(ref." + sa_name + ".email)"
							]
						}
					]
				}
			}
		}
	]

	outputs = [
		{
			"name": "keyName",
			"value": "$(ref." + sa_name + "-key.name)"
		},
		{
			"name": "privateKey",
			"value": "$(ref." + sa_name + "-key.privateKeyData)"
		}
	]

	# If a sink name was provided
	if createSink:
		if "organization-id" in context.properties and context.properties["organization-id"] is not None and context.properties["organization-id"] != "":
			parent_id = "organizations/" + context.properties["organization-id"]

			if "include-children" in context.properties and context.properties["include-children"] == True:
				includeChildren = True

		elif "folder-id" in context.properties and context.properties["folder-id"] is not None and context.properties["folder-id"] != "":
			parent_id = "folders/" + context.properties["folder-id"]

			if "include-children" in context.properties and context.properties["include-children"] == True:
				includeChildren = True

			createSink = False

		elif "billing-id" in context.properties and context.properties["billing-id"] is not None and context.properties["billing-id"] != "":
			parent_id = "billingAccounts/" + context["billing-id"]
		else:
			parent_id ="projects/" + context.env["project"]

		# If we're still creating the sink after evaluating the destination
		if createSink:
			resources.append({
				"name": context.properties["sink"],
				"type": "logging.v2.sink",
				"properties": {
					"sink": context.properties["sink"],
					"parent": parent_id,
					"filter": context.properties["log-filter"],
					"includeChildren": includeChildren,
					"destination": "pubsub.googleapis.com/$(ref." + pubsub_topic_name + ".name)"
				},
				"metadata" : {
					"dependsOn": [
						pubsub_topic_name
					]
				}
			})

			outputs.append({
				"name" : "writerIdentity",
				"value": "$(ref." + context.properties["sink"] + ".writerIdentity)"
			})

	return {"resources": resources, "outputs": outputs}

def MergeServiceAccountWithRoleIntoBindings(env, properties, serviceAccount, role, policy):
	"""
		A helper function that merges the provided account into the provided role in the policy name provided by the user
	"""

	binding = {
		'role': role,
		'members': [
			serviceAccount,
		]
	}

	if policy not in properties:
		return {
			'bindings': [
				binding,
			]
		}

	iam_policy = copy.deepcopy(properties[policy])
	bindings = []
  
	if 'bindings' in iam_policy and iam_policy["bindings"] is not None:
		bindings = iam_policy['bindings']
	else:
		iam_policy['bindings'] = bindings

	merged = False

	# Iterate each provided binding from the template
	for binding in bindings:

		# If the admin role is defined by the user in the template
		if binding['role'] == role:
			
			# Set merged to true since we don't need to add that role later
			merged = True		

			# If the project service account is not in the members of the admin role,
			# add it, then break out of the loop since we're done
			if serviceAccount not in binding['members']:
				binding['members'].append(serviceAccount)
				break

	# If the user provided IAM policy didn't include the pubsub.admin role, go ahead and 
	# add it in to the policy for the service account
	if not merged:
		bindings.append(binding)

	return iam_policy