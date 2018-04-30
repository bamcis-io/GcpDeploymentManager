import time

def GenerateConfig(context):
	"""Generates the route config"""

	# Sleep for 30 seconds to wait for pubsub topic to be created
	time.sleep(30)

	topic = context.properties["topic"]

	# If the topic wasn't provided as the full path, just the topic name, add it
	if not topic.startswith("projects/"):
		topic = "projects/" + context.env["project"] + "/topics/" + topic

	resource = {
		'name': context.env["name"],
		'type': 'pubsub.v1.subscription',
		'properties': {
			"subscription": context.env["name"],
			'topic': topic
		}
	}

	if "iam-policy" in context.properties and context.properties["iam-policy"] is not None:
		resource["accessControl"] = {
			'gcpIamPolicy': context.properties["iam-policy"]
		}

	resources = [
		resource
	]

	return {'resources': resources}