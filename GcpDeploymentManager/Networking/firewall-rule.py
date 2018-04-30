
def GenerateConfig(context):
	"""Generates config."""
	
	properties = {
		"allowed": context.properties["rules"],
		"priority": context.properties["priority"],
		"direction": context.properties["direction"]
	}

	if "network" in context.properties and context.properties["network"] is not None and context.properties["network"] != "":
		network = context.properties["network"]

		if network != "global/networks/default" and not network.startswith("projects/"):
			network = "projects/" + context.env["project"] + "/global/networks/" + network 

		properties["network"] = network
	

	if "source" in context.properties and context.properties["source"] is not None and len(context.properties["source"]) > 0:
		properties["sourceRanges"] = context.properties["source"]

	if "destination" in context.properties and context.properties["destination"] is not None and len(context.properties["destination"]) > 0:
		properties["destinationRanges"] = context.properties["destination"]

	if "description" in context.properties and context.properties["description"] is not None and context.properties["description"] != "":
		properties["description"] = context.properties["description"]

	if context.properties["direction"] == "INGRESS" and "source-service-accounts-filter" in context.properties and context.properties["source-service-accounts-filter"] is not None and len(context.properties["source-service-accounts-filter"]) > 0:
		properties["sourceServiceAccounts"] = context.properties["source-service-accounts-filter"]

	if "target-service-accounts" in context.properties and context.properties["target-service-accounts"] is not None and len(context.properties["target-service-accounts"]) > 0:
		properties["targetServiceAccounts"] = context.properties["target-service-accounts"]

	if "target-tags" in context.properties and context.properties["target-tags"] is not None and len(context.properties["target-tags"]) > 0:
		properties["targetTags"] = context.properties["target-tags"]

	if context.properties["direction"] == "INGRESS" and "source-tags-filter" in context.properties and context.properties["source-tags-filter"] is not None and len(context.properties["source-tags-filter"]) > 0:
		properties["sourceTags"] = context.properties["source-tags-filter"]

	rule = {
		"name": context.env["name"],
		"type": "compute.beta.firewall",
		"properties": properties
	}

	if "depends-on" in context.properties and context.properties["depends-on"] is not None and len(context.properties["depends-on"]) > 0:
		rule["metadata"] = {
			"dependsOn" : context.properties["depends-on"]
		}

	return { "resources": [ rule ] }