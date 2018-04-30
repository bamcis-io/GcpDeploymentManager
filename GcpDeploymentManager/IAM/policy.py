import sys
import random

def GenerateConfig(context):
	"""Generates the project policy config"""

	resources = []

	if (("policy" not in context.properties and "audit-config" not in context.properties) or
		("policy" in context.properties and context.properties["policy"] is None and "audit-config" in context.properties and context.properties["audit-config"] is None) or
		("policy" in context.properties and "audit-config" not in context.properties and context.properties["policy"] is None) or
		("policy" in context.properties and "audit-config" not in context.properties and not ValidatePolicy(context.properties["policy"])) or
		("audit-config" in context.properties and "policy" not in context.properties and context.properties["audit-config"] is None)):
		sys.exit('Invalid policy, must specify at least add or remove for a policy or an audit config.')

	resource_type = context.properties["type"]
	resource_id = ""
	path = ""
	dependsOn = []

	if "depends-on" in context.properties and context.properties["depends-on"] is not None and len(context.properties["depends-on"]) > 0:
		dependsOn.extend(context.properties["depends-on"])

	if resource_type == "organization":
		resource_id = "organizations/" + context.properties["id"]
		path = "organizations"
	elif resource_type == "folder":
		resource_id = "folders/" + context.properties["id"]
		path = "folders"
	else:
		resource_id = context.properties["id"]
		path = "projects"

	if "audit-config" in context.properties and context.properties["audit-config"] is not None:

		# This will make sure a new etag is created each time
		get_metadata = {
			"runtimePolicy": [
				"UPDATE_ALWAYS"
			]
		}

		if len(dependsOn) > 0:
			get_metadata["dependsOn"] = dependsOn

		resources.extend([			
			{
				"name": "get-iam-policy-audit-" + context.env["name"],
				"action": "gcp-types/cloudresourcemanager-v1:cloudresourcemanager." + path + ".getIamPolicy",
				"properties": {
					"resource": resource_id
				},
				"metadata": get_metadata
			},
			{
				"name": "set-iam-policy-audit-" + context.env["name"],
				"action": "gcp-types/cloudresourcemanager-v1:cloudresourcemanager." + path + ".setIamPolicy",
				"properties" : {
					"resource": resource_id,
					"policy": { 
						"etag" : "$(ref.get-iam-policy-audit-" + context.env["name"] + ".etag)",
						"auditConfigs": context.properties["audit-config"]
					},
					"updateMask": "auditConfigs,etag"
				}
			}
		])

		dependsOn.append("set-iam-policy-audit-" + context.env["name"])

	policyPatch = {}

	if "policy" in context.properties and context.properties["policy"] is not None:

		if "add" in context.properties["policy"] and context.properties["policy"]["add"] is not None and len(context.properties["policy"]["add"]) > 0:
			policyPatch["add"] = context.properties["policy"]["add"]

		if "remove" in context.properties["policy"] and context.properties["policy"]["remove"] is not None and len(context.properties["policy"]["remove"]) > 0:
			policyPatch["remove"] = context.properties["policy"]["remove"]
		
		policy_get_metadata = {
			# This will make sure a new etag is created each time
			"runtimePolicy": [
				"UPDATE_ALWAYS"
			]
		}

		if len(dependsOn) > 0:
			policy_get_metadata["dependsOn"] = dependsOn

		resources.extend(
			[
				{
					"name": "get-iam-policy-" + context.env["name"],
					"action": "gcp-types/cloudresourcemanager-v1:cloudresourcemanager." + path + ".getIamPolicy",
					"properties": {
						"resource": resource_id
					},
					"metadata": policy_get_metadata
				},
				{
					"name": "patch-iam-policy-" + context.env["name"],
					"action": "gcp-types/cloudresourcemanager-v1:cloudresourcemanager." + path + ".setIamPolicy",
					"properties": {
						"resource": resource_id,
						"policy": "$(ref.get-iam-policy-" + context.env["name"] + ")",
						"gcpIamPolicyPatch": policyPatch
					}
				}
			]
		)

	return {"resources": resources}

def ValidatePolicy(policies):
	if policies is not None:	
		# Neither are defined
		if "add" not in policies and "remove" not in policies or policies["add"] is None and policies["remove"] is None:
			return False
		# Only add is defined and it's empty
		elif "add" in policies and policies["add"] is not None and len(policies["add"]) == 0 and policies["remove"] is None:
			return False
		# Only remove is defined and it's empty
		elif "remove" in policies and policies["remove"] is not None and len(policies["remove"]) == 0 and policies["add"] is None:
			return False
		# Both are defined but empty
		elif len(policies["add"]) == 0 and len(policies["remove"]) == 0:
			return False
		# So at least 1 is defined and not empty
		else:
			return True
	else:
		return False