#!/bin/bash

<<<<<<< HEAD
# Warning message for deploy to production
echo "You are deploying current code to kansha-lxme-v0.4 web app, in production. Are you absolutely certain you want to push this code? You will overwrite previous code, so be mindful.
Do you wish to proceed? [y/n]:"
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "Exiting script."
  exit 0
fi
=======
# Set variables
RESOURCE_GROUP="knowledge-bots-demos"
CONTAINER_REGISTRY="kanshakbregistry"
>>>>>>> 3e3285f1de124e1579d3b9023cde2e3000a11583

# Ensure environment variables are set
if [[ -z "${OPENAI_API_KEY}" || -z "${SERPER_API_KEY}" ]]; then
  echo "Error: Environment variables OPENAI_API_KEY and SERPER_API_KEY must be set."
  exit 1
fi

<<<<<<< HEAD
=======
# Input web app name
echo "Input a web app name to deploy. Ensure you are on the right branch and deploy appropriate code to a webapp. A deploy overwrites all previous code\n Input:"
read WEB_APP_NAME
echo "Starting deploy to $WEB_APP_NAME"

>>>>>>> 3e3285f1de124e1579d3b9023cde2e3000a11583
# Login to Azure
az login

# Build and deploy the Docker image with secret build arguments
<<<<<<< HEAD
az acr build --registry bfsiregistry --image kansha-lxme-v04 --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .

# Restart webapp to reflect latest container changes
az webapp restart --resource-group kansha-prod-india --name kansha-lxme-v04
=======
az acr build --registry $CONTAINER_REGISTRY --image $WEB_APP_NAME --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .

# Restart webapp to reflect latest container changes
az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME
>>>>>>> 3e3285f1de124e1579d3b9023cde2e3000a11583
