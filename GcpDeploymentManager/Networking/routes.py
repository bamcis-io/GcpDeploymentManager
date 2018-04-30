import sys

def GenerateConfig(context):
	"""Generates the route config"""

	resources = []

	for route in context.properties["routes"]:	
		new_route_properties = {
			"destRange" = route["destination"],
			"network" = route["network"]
		}

		if hasattr(route, "priority"):
			new_route_properties["priority"] = route["priority"]

		if hasattr(route, "tags") and len(route["tags"]) > 0:
			new_route_properties["tags"] = route["tags"]

		if hasattr(route, "next-hop-gateway") and route["next-hop-gateway"] is not None and route["next-hop-gateway"] != "":
			new_route_properties["nextHopGateway"] = route["next-hop-gateway"]
		elif hasattr(route, "next-hop-instance") and route["next-hop-instance"] is not None and route["next-hop-instance"] != "":
			new_route_properties["nextHopInstance"] = route["next-hop-instance"]
		elif hasattr(route, "next-hop-ip") and route["next-hop-ip"] is not None and route["next-hop-ip"] != "":
			new_route_properties["nextHopIp"] = route["next-hop-ip"]
		elif hasattr(route, "next-hop-vpn") and route["next-hop-vpn"] is not None and route["next-hop-vpn"] != "":
			new_route_properties["nextHopVpnTunnel"] = route["next-hop-vpn"]
		else:
			sys.exit('Invalid route, must specify a next hop of [gateway, instance, ip, network, vpn].')

		new_route = {
			"name": route["name"],
			"type": "compute.v1.route",
			"properties": new_route_properties
		}

		if "depends-on" in context.properties and context.properties["depends-on"] is not None and len(context.properties["depends-on"]) > 0:
			new_route["metadata"] = {
				"dependsOn" = context.properties["depends-on"]
			}

		resources.append(new_route)

	return {"resources": resources}