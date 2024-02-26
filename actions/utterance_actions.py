from typing import Dict, Text, List
import spacy
from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from actions.dicts import profile_prompt
from actions.helpers import create_dict, get_response, get_conv_context_raw, similarity_bm25
from database import db
from utils import logger

nlp = spacy.load("en_core_web_md")


def get_user_profile(sender_id):
    name = ''
    age = ''
    daily_activity = ''
    years_of_pd = ''
    existing_symp = ''
    daily_challenges = ''
    prescribed_meds = ''
    prescribed_meds_purpose = ''
    profile = []

    try:
        val = db.voicebot.profiles.find_one({"sender_id": sender_id})
        name = val['data'][0]['name']
        age = val['data'][0]['age']
        daily_activity = val['data'][0]['daily_activity']
        years_of_pd = val['data'][0]['years_of_pd']
        existing_symp = val['data'][0]['existing_symptoms']
        daily_challenges = val['data'][0]['daily_challenges']
        prescribed_meds = val['data'][0]['prescribed_medications']
        prescribed_meds_purpose = val['data'][0]['prescribed_medications_purpose']
    except Exception as e:
        logger.error(str(e))

    profile.append(f'What is your preferred name? -> {name}')
    profile.append(f'What is your age? -> {age}')
    profile.append(f'What are your typical daily activities? -> {daily_activity}')
    profile.append(f'How many years did you have Parkinson\'s? -> {years_of_pd}')
    profile.append(f'What are your existing Parkinson\'s symptoms? -> {existing_symp}')
    profile.append(f'What challenges do you face on a regular basis? -> {daily_challenges}')
    profile.append(f'What are your prescribed medications? -> {prescribed_meds}')
    profile.append(f'For what purpose do you take each medication? -> {prescribed_meds_purpose}')

    return profile


def get_conversation_history(sender_id, ques):
    items = db.conversations.find({"sender_id": sender_id})
    events = items[0]['events']
    all_convs = []
    latest_bot_message = ''

    for event in events:
        if (event.get("event") == "bot") and (event.get("event") is not None):
            latest_bot_message = latest_bot_message + ' ' + event.get("text")
            latest_bot_message = latest_bot_message.strip()

        elif (event.get("event") == "user") and (event.get("event") is not None):
            latest_user_message = event.get("text")

            if len(latest_bot_message) != 0:
                msg_2_add = '{} -> {}'.format(latest_bot_message, latest_user_message)
                latest_bot_message = ''
                score = similarity_bm25(msg_2_add, ques)

                if score >= 0.5:
                    all_convs.append(msg_2_add)
    return all_convs


def sentence_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)


def generate_personalized_message(msg, history, profile, conv_context):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with an answer.'

    if len(history) > 0:
        prompt = 'Imagine you are a bot or a conversational agent and the following is the conversation between you and a user:\n' + \
                 f', '.join(
                     conv_context) + '\n Also you are given the following profile of the user who is a Parkinson\'s patient: ' + ', '.join(
            profile) + '. And the following conversation history between the user and the conversational agent: ' + ', '.join(
            history) + f' The latest utterance in the conversation by you is: {msg}.' + \
                 ' Now use relevant and appropriate content from the conversation, history, and the profile of the user, including their medication intake and time, daily activities, prior reported symptoms, and so on, to paraphrase and personalize the latest message. Also make the personalized utterance sound natural and coherent to the conversation. Don\'t say anything else.'
    else:
        prompt = 'Imagine you are a bot or a conversational agent and the following is the conversation between you and a user:\n' + \
                 f', '.join(
                     conv_context) + '\n Also you are given the following profile of the user who is a Parkinson\'s patient: ' + ', '.join(
            profile) + f' The latest utterance in the conversation by you is: {msg}.' + \
                 ' Now use relevant and appropriate content from the conversation and the profile of the user, including their medication intake and time, daily activities, prior reported symptoms, and so on, to paraphrase and personalize the latest message. Also make the personalized utterance sound natural and coherent to the conversation. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, 0.5)
    if similarity_bm25(out, msg) >= 0.5:
        return out
    return msg


def paraphrase_question(sender_id, ques, events):
    try:
        profile = get_user_profile(sender_id)
        history = get_conversation_history(sender_id, ques)
        conv_context = get_conv_context_raw(events, history=20)

        return generate_personalized_message(ques, history, profile, conv_context)
    except Exception as e:
        logger.error(str(e))
        return ques


class AskForMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # print(domain['responses']['utter_ask_medicinetype'][-1]['text'])
        text = 'Did you take your Parkinson\'s medication today?'
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        # dispatcher.utter_message(response="utter_ask_medicinetype")
        dispatcher.utter_message(text=question)
        return []


class AskForMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = 'When did you last take your Parkinson\'s medication?'
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        # dispatcher.utter_message(response="utter_ask_medicinetype")
        dispatcher.utter_message(text=question)
        return []


class AskForTremorDuration(Action):
    def name(self) -> Text:
        return "action_ask_tremorjournaling_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_tremorjournaling_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForTremorCooccurrence(Action):
    def name(self) -> Text:
        return "action_ask_tremorjournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_tremorjournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForTremorDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_tremorjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_tremorjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForTremorHistory(Action):
    def name(self) -> Text:
        return "action_ask_tremorjournaling_history"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_tremorjournaling_history'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBradykinesiaDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_bradykinesiajournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_bradykinesiajournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBradykinesiaCooccurrence(Action):
    def name(self) -> Text:
        return "action_ask_bradykinesiajournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_bradykinesiajournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDuration(Action):
    def name(self) -> Text:
        return "action_ask_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForTime(Action):
    def name(self) -> Text:
        return "action_ask_time"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_time'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForLocation(Action):
    def name(self) -> Text:
        return "action_ask_location"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_location'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForActivity(Action):
    def name(self) -> Text:
        return "action_ask_activity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_activity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDizzinessCooccurrence(Action):
    def name(self) -> Text:
        return "action_ask_dizzinessjournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dizzinessjournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDizzinessDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_dizzinessjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dizzinessjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDizzinessSeverity(Action):
    def name(self) -> Text:
        return "action_ask_dizzinessjournaling_severity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dizzinessjournaling_severity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDizzinessHistory(Action):
    def name(self) -> Text:
        return "action_ask_dizzinessjournaling_history"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dizzinessjournaling_history'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForFallingSeverity(Action):
    def name(self) -> Text:
        return "action_ask_fallingjournaling_severity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_fallingjournaling_severity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForMoodDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_moodjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_moodjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForMoodReason(Action):
    def name(self) -> Text:
        return "action_ask_moodjournaling_reason"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_moodjournaling_reason'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForInsomniaMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_insomniajournaling_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_insomniajournaling_medicinetype'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForInsomniaMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_insomniajournaling_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_insomniajournaling_medicinetime'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForInsomniaDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_insomniajournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_insomniajournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForInsomniaSeverity(Action):
    def name(self) -> Text:
        return "action_ask_insomniajournaling_severity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_insomniajournaling_severity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForInsomniaReason(Action):
    def name(self) -> Text:
        return "action_ask_insomniajournaling_reason"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_insomniajournaling_reason'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForStiffnessMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_stiffnessjournaling_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_stiffnessjournaling_medicinetype'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForStiffnessMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_stiffnessjournaling_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_stiffnessjournaling_medicinetime'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForStiffnessDescription(Action):
    def name(self) -> Text:
        return "action_ask_stiffnessjournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_stiffnessjournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForStiffnessDuration(Action):
    def name(self) -> Text:
        return "action_ask_stiffnessjournaling_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_stiffnessjournaling_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForStiffnessDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_stiffnessjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_stiffnessjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForFatigueTime(Action):
    def name(self) -> Text:
        return "action_ask_fatiguejournaling_time"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_fatiguejournaling_time'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForFatigueDescription(Action):
    def name(self) -> Text:
        return "action_ask_fatiguejournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_fatiguejournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForFatigueDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_fatiguejournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_fatiguejournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDyskinesiaMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_dyskinesiajournaling_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dyskinesiajournaling_medicinetype'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDyskinesiaMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_dyskinesiajournaling_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dyskinesiajournaling_medicinetime'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDyskinesiaDescription(Action):
    def name(self) -> Text:
        return "action_ask_dyskinesiajournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dyskinesiajournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDyskinesiaDuration(Action):
    def name(self) -> Text:
        return "action_ask_dyskinesiajournaling_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dyskinesiajournaling_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDyskinesiaDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_dyskinesiajournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dyskinesiajournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDystoniaMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_dystoniajournaling_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dystoniajournaling_medicinetype'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDystoniaMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_dystoniajournaling_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dystoniajournaling_medicinetime'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDystoniaCooccurence(Action):
    def name(self) -> Text:
        return "action_ask_dystoniajournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dystoniajournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForDystoniaTime(Action):
    def name(self) -> Text:
        return "action_ask_dystoniajournaling_time"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_dystoniajournaling_time'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBalanceDescription(Action):
    def name(self) -> Text:
        return "action_ask_balancejournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_balancejournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBalanceCooccurence(Action):
    def name(self) -> Text:
        return "action_ask_balancejournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_balancejournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBalanceDuration(Action):
    def name(self) -> Text:
        return "action_ask_balancejournaling_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_balancejournaling_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForBalanceDevices(Action):
    def name(self) -> Text:
        return "action_ask_balancejournaling_devices"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_balancejournaling_devices'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForPainMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_painjournaling_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_painjournaling_medicinetype'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForPainMedicinetime(Action):
    def name(self) -> Text:
        return "action_ask_painjournaling_medicinetime"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_painjournaling_medicinetime'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForPainDescription(Action):
    def name(self) -> Text:
        return "action_ask_painjournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_painjournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForPainDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_painjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_painjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForPainDuration(Action):
    def name(self) -> Text:
        return "action_ask_painjournaling_duration"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_painjournaling_duration'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForWeaknessDescription(Action):
    def name(self) -> Text:
        return "action_ask_weaknessjournaling_description"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_weaknessjournaling_description'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForWeaknessDailyactivity(Action):
    def name(self) -> Text:
        return "action_ask_weaknessjournaling_dailyactivity"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_weaknessjournaling_dailyactivity'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []


class AskForWeaknessCooccurence(Action):
    def name(self) -> Text:
        return "action_ask_weaknessjournaling_cooccurrence"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        text = domain['responses']['utter_ask_weaknessjournaling_cooccurrence'][-1]['text']
        sender_id = tracker.sender_id
        symptom = tracker.get_slot('symptom')
        question = paraphrase_question(sender_id, text, tracker.events)
        dispatcher.utter_message(text=question)
        return []
