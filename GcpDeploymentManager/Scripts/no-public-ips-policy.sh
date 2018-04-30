#!/bin/bash

# $1 is the path to the policy.json file
# $2 is the project to set the policy on

gcloud beta resource-manager org-policies set-policy "$1" --project "$2"