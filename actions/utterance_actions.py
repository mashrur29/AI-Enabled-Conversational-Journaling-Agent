from typing import Dict, Text, List

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from actions.dicts import profile_prompt
from actions.helpers import create_dict, get_response
from database import db


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
        print(str(e))

    return name, age, daily_activity, years_of_pd, existing_symp, daily_challenges, prescribed_meds


def paraphrase_question(sender_id, ques, symptom):
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
    return response


class AskForMedicinetype(Action):
    def name(self) -> Text:
        return "action_ask_medicinetype"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # print(domain['responses']['utter_ask_medicinetype'][-1]['text'])
        text = 'Have you taken your Parkinson\'s medication today?'
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
