# AI-Enabled Conversational Journaling for Advancing Parkinson's Disease Symptom Tracking

This repository contains the codebase for the system presented in our CHI 2025 paper, **"AI-Enabled Conversational Journaling for Advancing Parkinson's Disease Symptom Tracking."** The system uses Rasa for conversational AI, integrates with Alexa via webhooks, and uses AWS and MongoDB for data management.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System on AWS](#running-the-system-on-aws)
- [Webhook Endpoints](#webhook-endpoints)
- [Connecting AWS to Local Storage](#connecting-aws-to-local-storage)
- [Additional Tutorials](#additional-tutorials)
- [Git Configuration](#git-configuration)

## Prerequisites

- **Python:** Ensure you have Python 3.10 installed.
- **Rasa:** Installation details and version requirements can be found in the [Rasa documentation](https://rasa.com/docs/).
- **AWS Access:** Ensure you have the appropriate SSH key and permissions for connecting to your AWS EC2 instance.
- **MongoDB:** Refer to the MongoDB tutorials below if you need to install or connect to MongoDB.

## Installation

1. **Python Dependencies:**  
   Install all required Python packages via pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the System on AWS

To get the system up and running on AWS, follow these steps:

1. **Start Rasa Server and Actions:**
   - Run the Rasa server on port 6000:
     ```bash
     rasa run -p 6000
     ```
   - Start the Rasa actions server:
     ```bash
     rasa run actions
     ```
2. **Expose the Local Server using ngrok:**  
   Start ngrok to tunnel port 6000:
   ```bash
   ngrok http 6000
   ```

## Webhook Endpoints

After starting ngrok, use the generated URLs to configure your webhooks:

- **Slack Webhook:**  
  ```
  https://<ngrok-id>.ngrok-free.app/webhooks/slack/webhook
  ```
- **Alexa Assistant Webhook:**  
  ```
  https://<ngrok-id>.ngrok-free.app/webhooks/alexa_assistant/webhook
  ```

> *Note: Replace `<ngrok-id>` with the actual ngrok subdomain provided when you start ngrok.*

## Connecting AWS to Local Storage

To securely forward AWS connections to your local MongoDB instance, run the following SSH tunneling command:

```bash
sudo ssh -i ~/voicebot-server.pem -N -f -L 8000:localhost:27017 ubuntu@ec2-54-210-24-116.compute-1.amazonaws.com
```

This command forwards your local port `8000` to MongoDB's default port (`27017`) on the AWS instance.

## Additional Tutorials

For further setup and configuration, please refer to the following tutorials:

- **Connecting MongoDB Compass with EC2:**  
  Follow the step-by-step guide [here](https://jasonwatmore.com/post/2020/02/05/connect-to-remote-mongodb-on-aws-ec2-simply-and-securely-via-ssh-tunnel).

- **Installing MongoDB on Ubuntu:**  
  Detailed instructions can be found in the [MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/).

- **Using Localtunnel (ngrok Alternative):**  
  For an alternative tunneling solution, check out [this guide](https://techmonger.github.io/13/localtunnel-ubuntu/).

## Git Configuration

To store your Git credentials and avoid repeated password prompts, configure Git globally with:

```bash
git config --global credential.helper store
```

After setting this, you can simply pull updates using:

```bash
git pull
```