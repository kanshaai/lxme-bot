## Download logs

Currently, logs will be stored in azure blob storage 'kanshademostorage'. During a conversation, each time the chatbot answers, the last two messages will be appended to a local .txt file. (Please note this differs from before, where the whole conversation was stored every time, leading to a lot of redundancy). Once per day, the text file gets uploaded to azure blob storage and cleaned, to be filled again.
Downloading the text file can be done by typing 'give me the logs 420' into the chat. Currently, a local file download simply happens. We want to make a more secure solution for that asap.

## Azure Deployment Instructions

There are two scripts to automatically interact with our azure. 
```create_app.sh``` will initiates a new web app on our demo group (not production)
```deploy.sh``` will redeploy current code to an existing webapp

### Prerequisites
To run any of these scripts, ensure you have the following:
- An active Azure portal subscription, that is connected to the Kansha account. No need to insert credentials, authentication will happen straightforward through your web browser
- Installed azure command line interface. Run ```pip install azure-cli``` in your terminal, or download the package from [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Give the scripts executable permissions (macOS and Linux). Run ```chmod +x deploy.sh```
- Have the variables OPENAI_API_KEY and SERPER_API_KEY defined as environment variables

### Create new app
When ready to create a new app, execute the script ```create_app.sh```. This will do in order the following steps:
- Ask you to input a new web app name. Be specific, as this name needs to recognize the purpose of the app. Also, remember it must be globally unique (across the whole world and all organizations), so make a specific name.
- Login to azure, automatically opens a browser window for authentication
- Push all contents of current code directory to our Azure Container Registry 'kanshakbregistry', and build a docker image there from Dockerfile
- Initiate web app on our 'knowledge-bots-demos' group
- Connect web app instance to the associated docker container registry
- Connect to our Azure Storage account 'kanshademostorage', where we store the logs
- Reloads the web app to take these new connections into account
- Web app is ready. You can access it through Azure portal, to find the associated link

### Deploy to existing app
Execute the script ```deploy.sh```. Make sure you are on the right branch of the repository and upload to the correct web app. A deployment is final, and overwrites all previous data. Make sure to use correctly. It does the following steps:
- Input web app name and login to azure
- Push current code to container registry, and build a new docker image
- Reloads the web app to pull the newest docker image. Is ready within 5-8 minutes