import copy

def GenerateConfig(context):
	"""Generates the route config"""

	resources = [		
		{
			'name': context.env["name"],
			'type': 'pubsub.v1.topic',
			'properties': {
				'topic': context.env["name"]
			},
			'accessControl': {
				'gcpIamPolicy': MergeCallingServiceAccountWithAdminPermissionsIntoBindings(context.env, context.properties)
			}
		}
	]

	return {'resources': resources}

def MergeCallingServiceAccountWithAdminPermissionsIntoBindings(env, properties):
	"""
		A helper function that merges the acting service account of the project
		creator as an admin of the pubsub topic being created
	"""

	service_account = ('serviceAccount:{0}@cloudservices.gserviceaccount.com'.format(env['project_number']))

	set_creator_sa_as_owner = {
		'role': 'roles/pubsub.admin',
		'members': [
			service_account,
		]
	}

	if 'iam-policy' not in properties:
		return {
			'bindings': [
				set_creator_sa_as_owner,
			]
		}

	iam_policy = copy.deepcopy(properties['iam-policy'])
	bindings = []
  
	if 'bindings' in iam_policy and iam_policy["bindings"] is not None:
		bindings = iam_policy['bindings']
	else:
		iam_policy['bindings'] = bindings

	merged = False

	# Iterate each provided binding from the template
	for binding in bindings:

		# If the admin role is defined by the user in the template
		if binding['role'] == 'roles/pubsub.admin':
			
			# Set merged to true since we don't need to add that role later
			merged = True		

			# If the project service account is not in the members of the admin role,
			# add it, then break out of the loop since we're done
			if service_account not in binding['members']:
				binding['members'].append(service_account)
				break

	# If the user provided IAM policy didn't include the pubsub.admin role, go ahead and 
	# add it in to the policy for the service account
	if not merged:
		bindings.append(set_creator_sa_as_owner)

	return iam_policy