#!/bin/bash

# $1 is the subnet name 
# $2 is the project id of the XPN VPC
# $3 is the file location where the json is saved and read from

gcloud beta compute networks subnets get-iam-policy "$1" --project "$2" --format json > "$3"

# Save the output to a file
# Add a binding to grant a member the roles/compute.networkUser role or a custom role

gcloud beta compute networks subnets set-iam-policy "$1" "$3" --project "$2"