import logging
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
import time

logger = logging.getLogger(__name__)


class AlexaConnector(InputChannel):
    """A custom http input channel for Alexa.

    You can find more information on custom connectors in the 
    Rasa docs: https://rasa.com/docs/rasa/user-guide/connectors/custom-connectors/
    """

    @classmethod
    def name(cls):
        return "alexa_assistant"

    async def send_progressive_response(self, request_id: str, api_endpoint: str,
                                        api_access_token: str):

        logger.info('Sending a progressive response to Alexa')

        url = f"{api_endpoint}/v1/directives"
        headers = {
            "Authorization": f"Bearer {api_access_token}",
            "Content-Type": "application/json",
        }

        audio_url = 'https://gridstudies.s3.amazonaws.com/pencil-or-marker-converted--cleaned-2.mp3'
        ssml = f'<audio src=\'{audio_url}\'/>'

        payload = {
            "header": {
                "requestId": request_id
            },
            "directive": {
                "type": "VoicePlayer.Speak",
                "speech": f"<speak> {ssml} </speak>"
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 204:
                    logger.info("Progressive response sent successfully.")
                else:
                    logger.error("Failed to send progressive response.")

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        alexa_webhook = Blueprint("alexa_webhook", __name__)

        @alexa_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok"})

        @alexa_webhook.route("/webhook", methods=["POST"])
        async def receive(request):

            payload = request.json
            intenttype = payload["request"]["type"]

            request_id = payload["request"]["requestId"]
            api_endpoint = payload['context']['System']["apiEndpoint"]
            api_access_token = payload['context']['System']["apiAccessToken"]

            if intenttype == "LaunchRequest":
                message = "I am your Parkinson\'s journal. You can start by saying 'hi'."
                session = "false"
            else:

                try:
                    sender_id = payload['session']['user']['userId']
                    input_channel = self.name()
                    metadata = self.get_metadata(request)
                    intent = payload["request"]["intent"]["name"]

                    if intent == "AMAZON.StopIntent":
                        session = "true"
                        message = "Talk to you later"
                    elif intent == "AMAZON.FallbackIntent":
                        session = "false"
                        message = "I'm sorry I did not understand what you said"
                    else:
                        try:
                            logger.info(f'Intent type: {intenttype}')
                            if (intenttype != "LaunchRequest") and (intenttype != "SessionEndedRequest"):
                                await self.send_progressive_response(request_id, api_endpoint, api_access_token)
                        except Exception as e:
                            logger.error(f'Text is not ready yet, not sending a progressive message: {str(e)}')

                        payload = request.json

                        text = payload["request"]["intent"]["slots"]["text"]["value"]

                        out = CollectingOutputChannel()

                        await on_new_message(UserMessage(
                            text,
                            out,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata
                        ))

                        responses = [m["text"] for m in out.messages]
                        message = ' '.join(responses)
                        session = "false"
                except Exception as e:
                    message = 'I didn\'t catch that. Can you please repeat?'
                    session = "false"
                    logger.error(f'Error sending message to Alexa: {str(e)}, {payload["request"]}')

            # Resource: https://developer.amazon.com/en-US/docs/alexa/custom-skills/request-and-response-json-reference.html
            r = {
                "version": "1.0",
                "sessionAttributes": {
                    "status": "test"
                },
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
