#!/bin/bash

# Ensure environment variables are set
if [[ -z "${OPENAI_API_KEY}" || -z "${SERPER_API_KEY}" ]]; then
  echo "Error: Environment variables OPENAI_API_KEY and SERPER_API_KEY must be set."
  exit 1
fi

# Login to Azure
az login

# Build and deploy the Docker image with secret build arguments
az acr build --registry kanshakbregistry --image oona-sales-demo --secret-build-arg OPENAI_API_KEY="${OPENAI_API_KEY}" --secret-build-arg SERPER_API_KEY="${SERPER_API_KEY}" .