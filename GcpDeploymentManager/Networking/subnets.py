

def GenerateConfig(context):
	"""Generates the subnet config"""

	resources = []

	for subnet in context.properties["subnets"]:	
		resources.append(
			{
			    "name" : subnet["name"],
				"type" : "compute.beta.subnetwork",
				"properties": {
					"ipCidrRange" : subnet["ipv4-cidr"],
					"name" : subnet["name"],
					"network" : "projects/" + context.env["project"] + "/global/networks/" + context.properties["network"],
					"description" : subnet["description"],
					"region" : subnet["region"],
					"privateIPGoogleAccess" : subnet["private-google-access"]
				}
			}
		)

	return {"resources": resources}