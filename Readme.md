First install the dependencies using pip: `pip install -r requirements.txt`

# Running Rasa on AWS

- `rasa run -p 6000`
- `rasa run actions`
- `ngrok http 6000`

# Alexa webhook format after starting ngrok

- `https://4bfa-54-224-59-177.ngrok-free.app/webhooks/slack/webhook`
- `https://4bfa-54-224-59-177.ngrok-free.app/webhooks/alexa_assistant/webhook`

# Connect AWS with local storage

- `sudo ssh -i ~/voicebot-server.pem -N -f -L 8000:localhost:27017 ubuntu@ec2-54-210-24-116.compute-1.amazonaws.com`

# Tutorial: Connect Mongodb Compass with EC2 (after previous step)

- Follow: `https://jasonwatmore.com/post/2020/02/05/connect-to-remote-mongodb-on-aws-ec2-simply-and-securely-via-ssh-tunnel`

# Tutorial: Install Mongodb

- Follow: `https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/`

# Tutorial: Localtunnel (ngrok alt)

- Follow: `https://techmonger.github.io/13/localtunnel-ubuntu/`

# Store Git Password

- `git config --global credential.helper store`
- `git pull`