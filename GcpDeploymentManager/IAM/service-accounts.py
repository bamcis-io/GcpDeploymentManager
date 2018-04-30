"""Creates the service accounts for a project"""

def GenerateConfig(context):
	"""Generates config."""

	project_id = context.env["project"] 

	if "project" in context.properties and context.properties["project"] is not None and len(context.properties["project"]) > 0:
		project_id = context.properties["project"]

	resources = []
	outputs = []

	if "service-accounts" in context.properties and context.properties["service-accounts"] is not None:
		for service_account in context.properties["service-accounts"]:
			
			name = service_account["name"]
			displayName = ""

			if "displayName" in service_account and service_account["displayName"] is not None and service_account["displayName"] != "":
				displayName = service_account["displayName"]
			else:
				displayName = name

			properties = {
				"accountId": name,
				"projectId": project_id,
				"displayName": displayName
			}
			
			resources.append({
				"name" : name,
				"type" : "iam.v1.serviceAccount",
				"metadata": {
					"dependsOn": [
						project_id
					]
				},
				"properties": properties
			})

			outputs.append({ 
				"name": name, 
				"value": "$(ref." + name + ".name)" 
			})

			if service_account.properties["createKey"]:
				resources.append(
					{
						"name": name + "-key",
						"type": "iam.v1.serviceAccounts.key",
						"properties": {
							"parent": "$(ref." + name + ".name)"
						},
						"metadata": {
							"dependsOn" :[
								name
							]
						}
					}
				)

				outputs.extend(
					[
						{
							"name": "keyName",
							"value": "$(ref." + name + "-key.name)"
						},
						{
							"name": "privateKey",
							"value": "$(ref." + name + "-key.privateKeyData)"
						}
					]
				)

	return {"resources": resources, "outputs": outputs}