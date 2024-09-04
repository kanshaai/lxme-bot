#!/bin/bash

# Warning message for deploy to production
echo "You are deploying current code to kansha-lxme-v0.4 web app, in production. Are you absolutely certain you want to push this code? You will overwrite previous code, so be mindful.
Do you wish to proceed? [y/n]:"
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "Exiting script."
  exit 0
fi

# Ensure environment variables are set
if [[ -z "${OPENAI_API_KEY}" || -z "${SERPER_API_KEY}" ]]; then
  echo "Error: Environment variables OPENAI_API_KEY and SERPER_API_KEY must be set."
  exit 1
fi

# Login to Azure
az login

# Build and deploy the Docker image with secret build arguments
az acr build --registry bfsiregistry --image kansha-lxme-v04 --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .

# Restart webapp to reflect latest container changes
az webapp restart --resource-group kansha-prod-india --name kansha-lxme-v04