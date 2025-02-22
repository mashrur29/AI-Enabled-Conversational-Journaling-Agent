from __future__ import annotations

import asyncio
import json
from utils import logger
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.shared.nlu.training_data.message import Message
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.utils import io

import openai
import os
import numpy as np
from typing import Dict, Text, Any, List, Tuple


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=False
)
class llmIntentClassifier(IntentClassifier, GraphComponent):

    # @classmethod
    # def required_packages(cls) -> List[Text]:
    #     return ["openai"]

    def __init__(
            self,
            config: Dict[Text, Any],
            model_storage: ModelStorage,
            resource: Resource
    ) -> None:
        super().__init__(config, model_storage, resource)

    def process(self, messages: List[Message]) -> List[Message]:
        from openai.error import RateLimitError
        import backoff as backoff
        import nltk

        @backoff.on_exception(backoff.expo, RateLimitError)
        def _completions_with_backoff(**kwargs):
            return openai.ChatCompletion.create(**kwargs)

        def _get_response_gpt(msg, temperature=0.4):
            API_KEY_1 = 'YOUR API KEY GOES HERE'
            numTries = 20
            for it in range(numTries):
                try:
                    openai.api_key = API_KEY_1
                    completion = _completions_with_backoff(
                        model="gpt-4",
                        messages=msg,
                        temperature=temperature
                    )
                    response = str(completion.choices[0].message['content'])

                    return response.strip()
                except Exception as e:
                    print("ERR: ", str(e))
            return 'none'

        def _check_quit(msg):
            if msg == 'exit':
                return 'exit'

        def _check_early_quit(msg):
            behavior = 'Answer in a single word. Don\'t say anything else'
            prompt_early_quit = f'Imagine you are a journaling chatbot talking to a user who is a Parkinson\'s patient. In the latest utterance the user responded with {msg}. Now, determine if the latest utterance is an intent to quit journaling. For instance, if the user says, \'quit\', \'i don\'t want to talk anymore\', \'my head will blow off because of you\', then this is an intent to quit journaling. Say \'yes\' if the user wants to quit journaling; otherwise, say \'no\'. Don\'t say anything else.'
            context = [{'role': 'system', 'content': behavior},
                       {'role': 'user', 'content': prompt_early_quit}]
            out = _get_response_gpt(context, temperature=0).lower()
            if out == 'yes':
                return True
            return False

        def _is_question_from_gpt(question):
            behavior = 'Answer in a single word. Don\'t say anything else'
            prompt = f'Imagine you are a journaling chatbot for assisting Parkinson\'s patients in recording their conditions. You are now talking to a Parkinson\'s patient. In the latest utterance, the user responded with {question}. Now, determine whether the latest user utterance is a question for you. Answer with only yes or no. Don\'t say anything else.'

            context = [{'role': 'system', 'content': behavior},
                       {'role': 'user', 'content': prompt}]

            out = _get_response_gpt(context, temperature=0).lower()

            if 'yes' in out:
                return True
            return False

        def _is_confusion_from_gpt(question):
            behavior = 'Answer in a single word. Don\'t say anything else'
            prompt = f'Imagine you are a journaling chatbot for assisting Parkinson\'s patients in recording their conditions. You are now talking to a Parkinson\'s patient. In the latest utterance, the user responded with {question}. Now, determine whether the latest user utterance expresses a confusion. The user\'s latest utterance expresses confusion, only if the user responds with \'i don\'t understand\' or \'confused\' or \'huh!\', or similar. Answer with only yes or no. Only say yes if you can confidently say that the user is confused. In all other cases, say no. Don\'t say anything else.'


            context = [{'role': 'system', 'content': behavior},
                       {'role': 'user', 'content': prompt}]

            out = _get_response_gpt(context, temperature=0).lower()

            if 'yes' in out:
                return True
            return False

        def _check_greeting(msg):
            msg = msg.replace(',', '').replace('!', '').replace(',', '').replace('\'', '').strip()
            greetings = ['hi', 'hello', 'hey', 'hiiiiii', 'hi!', 'hii', 'hiii', 'high', 'hi patrika', 'hello patrika',
                         'patrika', 'high patrika', 'hey patrika', 'restart']
            if msg in greetings:
                return True
            return False

        def _is_affirm_deny(msg):
            msg = msg.replace(',', '').replace('!', '').replace(',', '').replace('\'', '').strip()
            affirm = ['yes', 'yeah', 'yup', 'yush', 'ya', 'yea']
            deny = ['no', 'nope', 'nah', 'na', 'nop']

            for x in affirm:
                if x == msg:
                    return 'affirm'
            for x in deny:
                if x == msg:
                    return 'deny'
            return 'none'

        def _predict_intent(msg):
            if _check_quit(msg.lower()):
                return 'quit'

            if _check_greeting(msg.lower()):
                return 'greet'

            if _check_early_quit(msg):
                return 'early_quit'

            xx = _is_affirm_deny(msg.lower())
            if xx != 'none':
                return xx

            if _is_question_from_gpt(msg) == True:
                return 'question'

            if _is_confusion_from_gpt(msg) == True:
                return 'confusion'

            temperature = 0

            behavior = 'Answer in a single word. Don\'t say anything else'

            # This prompt has no examples for each intent type
            prompt_s_no_history = f'Imagine you are a journaling chatbot who is talking to a Parkinson\'s patient. The user responded with: {msg}, when asked, \'What do you want to record?\' by the chatbot. Based on the above information, predict the Parkinson\'s symptoms that the user is experiencing. Answer with the following symptoms: \'tremor\', \'bradykinesia\', \'stiffness\', \'dizziness\', \'falling\', \'insomnia\', \'fatigue\', \'mood\', \'dyskinesia\', \'dystonia\', \'balance-issue\', \'pain\', \'weakness\'. If the user reports more than one symptom, say \'multiple\'. If the user message expresses desire to followup with the conversational agent, say \'followup-specify\'. If the user message contains an audio speech recognition error, for instance incomplete sentence and ambiguous words, say, \'asr\'. If the user did not mention any symptom or their response says that they are not experiencing anything, say \'none\'. Don\'t use quotes. Don\'t say anything else.'

            # This prompt has examples for each intent type
            prompt_l_no_history = f'Imagine you are a journaling chatbot who is talking to a Parkinson\'s patient. The user responded with: {msg}, when asked, \'What do you want to record?\' by the chatbot. Based on the above information, predict the Parkinson\'s symptoms that the user is experiencing. Answer with the following symptoms: \'tremor\', \'bradykinesia\', \'stiffness\', \'dizziness\', \'falling\', \'insomnia\', \'fatigue\', \'mood\', \'dyskinesia\', \'dystonia\', \'balance-issue\', \'pain\', \'weakness\'. Here are a few examples for each of the symptoms, use them as refernce -- \'tremor\': \'my hands have been shaking uncontrollably; my tremors\',  \'bradykinesia\': \'I\'m moving much slower than usual; slowness in movement\', \'stiffness\': \'my muscles feel really stiff; hard to move around freely\', \'dizziness\': \'feeling dizzy, especially when standing up quickly\', \'falling\': \'i fell down\', \'insomnia\': \'trouble sleeping at night; can\'t sleep despite being tired\', \'fatigue\': \'constantly feeling tired; i feel fatigued\', \'mood\': \'feeling really down and anxious; i feel depressed\', \'dyskinesia\': \'my dyskinesia; involuntary, jerky movements\', \'dystonia\': \'muscle contractions; my dystonia\', \'balance-issue\': \'hard time keeping my balance; balance problems while walking\', \'pain\': \'persistent pain in shoulders and neck; dealing with pain\', \'weakness\: \'arms and legs feeling very weak; muscle weakness\'. If the user reports more than one symptom, say \'multiple\'. If the user message expresses desire to followup with the conversational agent, say \'followup-specify\'. If the user message contains an audio speech recognition error, for instance incomplete sentence and ambiguous words, say, \'asr\'. If the user did not mention any symptom or their response says that they are not experiencing anything, say \'none\'. Don\'t use quotes. Don\'t say anything else.'

            prompt2 = 'In the previous response, you mentioned, \'multiple\', indicating that the user wants to report more than one symptom. Now which of the following symptoms is the user talking about: \'tremor\', \'bradykinesia\', \'stiffness\', \'dizziness\', \'falling\', \'insomnia\', \'fatigue\', \'mood\', \'dyskinesia\', \'dystonia\', \'balance-issue\', \'pain\', \'weakness\'? Mention the symptoms separated by a comma. For instance, say, \'tremor, insomnia\', if the user wants to record their tremors and sleep problems. Don\'t use quotes. Don\'t say anything else.'

            intents = ['tremor', 'bradykinesia', 'stiffness', 'dizziness', 'falling', 'insomnia', 'fatigue', 'mood',
                       'dyskinesia', 'dystonia', 'balance', 'pain', 'weakness', 'multiple', 'asr', 'none']

            context = [{'role': 'system', 'content': behavior},
                       {'role': 'user', 'content': prompt_l_no_history}]

            out = _get_response_gpt(context, temperature).lower()

            for x in intents:
                if x in out:
                    return x

            return 'none'

        for message in messages:
            text = message.data["text"]

            prediction = _predict_intent(text)
            confidence = 1.0
            logger.info(f'Predicted intent for \'{text}\' is {prediction}')

            intent = {"name": prediction, "confidence": confidence}

            message.set("intent", intent, add_to_output=True)

        return messages
