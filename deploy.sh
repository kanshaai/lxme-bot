#!/bin/bash

# Set variables
RESOURCE_GROUP="kansha-prod-india"
CONTAINER_REGISTRY="bfsiregistry"

# Ensure environment variables are set
if [[ -z "${OPENAI_API_KEY}" || -z "${SERPER_API_KEY}" ]]; then
  echo "Error: Environment variables OPENAI_API_KEY and SERPER_API_KEY must be set."
  exit 1
fi

# Input web app name
echo "Input a web app name to deploy. Ensure you are on the right branch and deploy appropriate code to a webapp. A deploy overwrites all previous code\n Input:"
read WEB_APP_NAME
echo "Starting deploy to $WEB_APP_NAME"

# Login to Azure
az login

# Build and deploy the Docker image with secret build arguments
az acr build --registry $CONTAINER_REGISTRY --image $WEB_APP_NAME --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .

# Restart webapp to reflect latest container changes
az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME