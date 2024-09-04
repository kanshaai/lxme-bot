#!/bin/bash

# Set variables
RESOURCE_GROUP="kansha-prod-india"
APP_SERVICE_PLAN="prod1-bfsi"
CONTAINER_REGISTRY="bfsiregistry"
#STORAGE_ACCOUNT="kanshademostorage"

# Ensure environment variables are set
if [[ -z "${OPENAI_API_KEY}" || -z "${SERPER_API_KEY}" ]]; then
  echo "Error: Environment variables OPENAI_API_KEY and SERPER_API_KEY must be set."
  exit 1
fi

# Function to check the status of the last command and exit if it failed
check_status() {
  if [ $? -ne 0 ]; then
    echo "Error occurred in the previous step. Exiting."
    exit 1
  fi
}

# Read web app name
echo "Provide a new web app name.
Be specific, e.g. kansha-<client>-salesdemo
Use only alphanumeric characters and -
Input:"
read WEB_APP_NAME
echo "Starting process to create web app $WEB_APP_NAME"

# Log in to Azure
#echo "Logging in to Azure..."
#az login

# Push Docker Image to Azure Container Registry
echo "Pushing Docker image to Azure Container Registry..."
az acr build --registry $CONTAINER_REGISTRY --image $WEB_APP_NAME --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .

# Create Web App
#echo "Creating Web App $WEB_APP_NAME"
#az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEB_APP_NAME -i $CONTAINER_REGISTRY.azurecr.io/$WEB_APP_NAME:latest
#check_status

# Set up Web App connection to Azure Container Registry
echo "Setting up Web App connection to Azure Container Registry..."
az webapp config container set --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --container-image-name $CONTAINER_REGISTRY.azurecr.io/$WEB_APP_NAME:latest --container-registry-url https://$CONTAINER_REGISTRY.azurecr.io
check_status

# Set up Web App connection to Azure Storage
#echo "Setting up Web App connection to Azure Storage..."
#az webapp connection create storage-blob -g $RESOURCE_GROUP -n $WEB_APP_NAME --tg $RESOURCE_GROUP --account $STORAGE_ACCOUNT --system-identity
#check_status

# Restart Web App
echo "Restarting Web App..."
az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME
check_status

echo "All done! Web App $WEB_APP_NAME has been successfully created and deployed."