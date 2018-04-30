import sys

def GenerateConfig(context):
	"""Generates config."""

	name = ""

	if "name" in context.properties and context.properties["name"] is not None and context.properties["name"] != "":
		name = context.properties["name"]
	elif "name" in context.env and context.env["name"] is not None and context.env["name"] != "":
		name = context.env["name"]
	else:
		name = context.env["deployment"]	

	properties = {
		"destination": context.properties["destination"],
		"sink": name
	}

	# Sink is for organization
	if "organization-id" in context.properties and context.properties["organization-id"] is not None and context.properties["organization-id"] != "":
		properties["parent"] = "organizations/" + context.properties["organization-id"]

		if "include-children" in context.properties and context.properties["include-children"] == True:
			properties["includeChildren"] = True
	# Sink is for a folder
	elif "folder-id" in context.properties and context.properties["folder-id"] is not None and context.properties["folder-id"] != "":
		properties["parent"] = "folders/" + context.properties["folder-id"]

		if "include-children" in context.properties and context.properties["include-children"] == True:
			properties["includeChildren"] = True
	# Sink is for a billing account
	elif "billing-id" in context.properties and context.properties["billing-id"] is not None and context.properties["billing-id"] != "":
		properties["parent"] = "billingAccounts/" + context.properties["billing-id"]
	# Billing account is for a project, no need to do anything

	if "filter" in context.properties and context.properties["filter"] is not None and context.properties["filter"] != "":
		properties["filter"] = context.properties["filter"]

	if context.properties["cross-project"] == True:
		properties["uniqueWriterIdentity"] = True

	resources = [		
		{
			"name": context.env["name"],
			"type": 'logging.v2.sink',
			"properties": properties
		}
	]

	outputs = [
		{
			"name" : "writerIdentity",
			"value": "$(ref." + context.env["name"] + ".writerIdentity)"
		}
	]

	return {'resources': resources, "outputs" : outputs }