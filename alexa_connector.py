import logging
import asyncio
import aiohttp
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import asyncio
from rasa.shared.core.trackers import DialogueStateTracker
import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

logger = logging.getLogger(__name__)


class AlexaConnector(InputChannel):
    """A custom http input channel for Alexa.

    You can find more information on custom connectors in the 
    Rasa docs: https://rasa.com/docs/rasa/user-guide/connectors/custom-connectors/
    """

    @classmethod
    def name(cls):
        return "alexa_assistant"

    # Sanic blueprint for handling input. The on_new_message
    # function pass the received message to Rasa Core
    # after you have parsed it
    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        alexa_webhook = Blueprint("alexa_webhook", __name__)

        # required route: use to check if connector is live
        @alexa_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok"})

        async def send_progressive_response(request_id: str, message: str, api_endpoint: str,
                                            api_access_token: str):

            logger.info('Sending a progressive response to Alexa')

            url = f"{api_endpoint}/v1/directives"
            headers = {
                "Authorization": f"Bearer {api_access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "header": {
                    "requestId": request_id
                },
                "directive": {
                    "type": "VoicePlayer.Speak",
                    "speech": f"<speak> <audio src=\'{message}\'/> </speak>"
                }
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 204:
                        logger.info("Progressive response sent successfully.")
                    else:
                        logger.error("Failed to send progressive response.")

        # required route: defines
        @alexa_webhook.route("/webhook", methods=["POST"])
        async def receive(request):
            payload = request.json
            intenttype = payload["request"]["type"]

            request_id = payload["request"]["requestId"]
            api_endpoint = payload['context']['System']["apiEndpoint"]
            api_access_token = payload['context']['System']["apiAccessToken"]



            # if the user is starting the skill, let them know it worked & what to do next
            if intenttype == "LaunchRequest":
                message = "Hello! I am Patrika. You can start by saying 'hi'."
                session = "false"
            else:
                # get the Alexa-detected intent

                try:
                    sender_id = payload['session']['user']['userId']
                    input_channel = self.name()
                    metadata = self.get_metadata(request)
                    intent = payload["request"]["intent"]["name"]

                    # makes sure the user isn't trying to end the skill
                    if intent == "AMAZON.StopIntent":
                        session = "true"
                        message = "Talk to you later"
                    elif intent == "AMAZON.FallbackIntent":
                        session = "false"
                        message = "I'm sorry I did not understand what you said"
                    else:
                        # get the user-provided text from the slot named "text"
                        text = payload["request"]["intent"]["slots"]["text"]["value"]

                        # initialize output channel
                        out = CollectingOutputChannel()

                        if not (text == 'hi') or (text == 'exit'):
                            await send_progressive_response(request_id,
                                                            "https://gridstudy.s3.us-east-2.amazonaws.com/pencil-or-marker-converted-2.mp3",
                                                            api_endpoint,
                                                            api_access_token)

                        # send the user message to Rasa & wait for the
                        # response to be sent back
                        await on_new_message(UserMessage(
                            text,
                            out,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata
                        ))
                        # extract the text from Rasa's response
                        responses = [m["text"] for m in out.messages]
                        message = ''
                        for x in responses:
                            message = message + ' ' + x
                        # message = responses[0]
                        message = message.strip()
                        session = "false"
                except Exception as e:
                    message = ''
                    session = "false"
            # Send the response generated by Rasa back to Alexa to
            # pass on to the user. For more information, refer to the
            # Alexa Skills Kit Request and Response JSON Reference:
            # https://developer.amazon.com/en-US/docs/alexa/custom-skills/request-and-response-json-reference.html
            r = {
                "version": "1.0",
                "sessionAttributes": {"status": "test"},
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": message,
                        "playBehavior": "REPLACE_ENQUEUED",
                    },
                    "reprompt": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": message,
                            "playBehavior": "REPLACE_ENQUEUED",
                        }
                    },
                    "shouldEndSession": session,
                },
            }

            return response.json(r)

        return alexa_webhook
