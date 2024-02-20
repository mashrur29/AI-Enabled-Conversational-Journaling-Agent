from typing import Dict, Text, List
import spacy
from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from actions.dicts import profile_prompt
from actions.helpers import create_dict, get_response
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

    try:
        val = db.voicebot.profiles.find_one({"sender_id": sender_id})
        name = val['data'][0]['name']
        age = val['data'][0]['age']
        daily_activity = val['data'][0]['daily_activity']
        years_of_pd = val['data'][0]['years_of_pd']
        existing_symp = val['data'][0]['existing_symptoms']
        daily_challenges = val['data'][0]['daily_challenges']
        prescribed_meds = val['data'][0]['prescribed_medications']
    except Exception as e:
        logger.error(str(e))


    return name, age, daily_activity, years_of_pd, existing_symp, daily_challenges, prescribed_meds

def sentence_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

def paraphrase_question(sender_id, ques, symptom):
    try:
        name, age, daily_activity, years_of_pd, existing_symp, daily_challenges, prescribed_meds = get_user_profile(
            sender_id)
        msg_profile = []
        profile = profile_prompt.format(name, age, daily_activity, years_of_pd, existing_symp, daily_challenges,
                                        prescribed_meds)
        msg_profile.append(create_dict("system", profile))
        msg_profile.append(create_dict("user",
                                       f"Rewrite the question based on the user profile and don\'t say anything else. If it is impossible to rewrite the question, just say impossible. Question: {ques}"))

        response = get_response(msg_profile)
        if "impossible" in response.lower():
            return ques
        elif sentence_similarity(ques, response) >= 0.8:
            return response
        return ques
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
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
        question = paraphrase_question(sender_id, text, symptom)
        dispatcher.utter_message(text=question)
        return []