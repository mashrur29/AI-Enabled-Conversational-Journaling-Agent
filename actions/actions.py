import random
from datetime import datetime
from typing import Any, Text, Dict, List

from rasa.core.actions.forms import FormAction
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from actions.dicts import intent2Symptom, symptom2Slots
from rasa_sdk.events import SlotSet, ActionReverted, AllSlotsReset, FollowupAction
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.types import DomainDict
from actions.helpers import create_dict, get_response, get_symptom, get_symptom_fallback, get_response_in_form, \
    get_chitchat_in_form, determine_chitchat, get_chitchat_ack, check_profile, update_profile, init_profile, symptom2form, \
    symptoms, get_conv_context, get_response_generic


class ActionCreateUserProfile(Action):

    def name(self) -> Text:
        return "action_create_user_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            sender_id = tracker.sender_id
            if check_profile(sender_id) == False:
                init_profile(sender_id)

            name = tracker.get_slot('name')
            age = tracker.get_slot('age')
            daily_activity = tracker.get_slot('daily_activity')
            years_of_pd = tracker.get_slot('years_of_pd')
            existing_symp = tracker.get_slot('existing_symp')
            daily_challenges = tracker.get_slot('daily_challenges')
            prescribed_meds = tracker.get_slot('prescribed_meds')
            update_profile(sender_id, name, age, daily_activity, years_of_pd, existing_symp, daily_challenges,
                           prescribed_meds)
            print(f'Profile updated for {sender_id}')
        except Exception as e:
            print("Profile update failed for {}: {}".format(sender_id, str(e)))
        return []


class ActionUserCheckProfile(Action):

    def name(self) -> Text:
        return "action_check_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = tracker.sender_id

        try:
            if check_profile(sender_id):
                return [SlotSet("check_profile", "true")]
            else:
                init_profile(sender_id)
                return [SlotSet("check_profile", "false")]
        except Exception as e:
            return [SlotSet("check_profile", "false")]


class ActionRevertUserUtterance(Action):

    def name(self) -> Text:
        return "action_revert_user_utterance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [UserUtteranceReverted()]


class ActionResetAllSlot(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender_id = tracker.sender_id

        all_msg = []
        for event in tracker.events:
            if (event.get("event") == "bot") or (event.get("event") == "user"):
                latest_bot_message = event.get("text")
                all_msg.append('{}> {}'.format(event.get("event"), latest_bot_message))
        # print(all_msg)
        try:
            id_ = random.randint(0, 100000)
            with open('actions/convs/msg_{}.txt'.format(id_), 'w') as f:
                for x in all_msg:
                    f.write('{}\n'.format(x))

        except Exception as e:
            print(str(e))

        return [AllSlotsReset()]


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print('Inside fallback')

        try:
            symptom = tracker.get_slot('symptom')
            previous_user_msg = tracker.latest_message["text"]
        except Exception as e:
            symptom = ''
            previous_user_msg = ''
            print('Error retrieving symptom and previous user message')

        print(f'Current symptom: {symptom}')

        try:
            conv_context = get_conv_context(tracker.events)
        except Exception as e:
            conv_context = []
            print("Error in retrieving context: ", str(e))

        det_chitchat = determine_chitchat(conv_context)
        print(f'det_chitchat: {det_chitchat}')

        try:
            active_loop = tracker.active_loop.get("name")
            print(f'Active loop: {active_loop}')

            next_slot = tracker.get_slot("requested_slot")
            print(f'Requested slot {next_slot}')

            if 'profilejournal' in active_loop:
                return [SlotSet(next_slot, previous_user_msg), FollowupAction('profilejournal')]

            if active_loop is not None:

                if "no" in det_chitchat.lower():
                    utterance = get_response_in_form(conv_context)
                    dispatcher.utter_message(text=utterance)
                    return [SlotSet(next_slot, utterance), FollowupAction(active_loop)]
                else:
                    chitchat_response = get_chitchat_in_form(conv_context)
                    dispatcher.utter_message(text=chitchat_response)
                    dispatcher.utter_message(response="utter_return_journal")
                    return [UserUtteranceReverted()]
        except Exception as e:
            try:
                if symptom in symptoms:
                    form_name = symptom2form[symptom]
                    return [FollowupAction(form_name)]
            except Exception as e:
                print(str(e))

        print(f'user qna, no active form')

        #print(conv_context)

        if "no" not in det_chitchat.lower():
            chitchat_utter = get_chitchat_ack(conv_context)
            dispatcher.utter_message(text=chitchat_utter)
            return [UserUtteranceReverted()]

        if symptom == "None":
            nw_symptom = get_symptom(conv_context)
            nw_symptom = nw_symptom.replace('.', '').lower().strip()
            print(f'predicted symptom: {nw_symptom}')

            if "none" in nw_symptom:
                utterance = get_symptom_fallback(conv_context)
                dispatcher.utter_message(text=utterance)
                dispatcher.utter_message(response="utter_ask_to_add")
                return []
            else:
                if nw_symptom in symptoms:
                    dispatcher.utter_message(response="utter_start_journal")
                    form_name = symptom2form[nw_symptom]
                    print(f'Starting {form_name}')
                    return [SlotSet("symptom", nw_symptom), FollowupAction(form_name)]
                dispatcher.utter_message(response="utter_ask_to_conclude")
                return []

        print('Final recall!')
        utterance = get_response_generic(conv_context)
        dispatcher.utter_message(text=utterance)

        return [UserUtteranceReverted()]


class ActionRepeatQuestion(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_repeat_question"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_repeat_question")

        is_simplify = tracker.get_slot('is_simplify')
        if is_simplify:
            return []

        latest_bot_message = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                latest_bot_message = event.get("text")
        dispatcher.utter_message(text=latest_bot_message)

        return [UserUtteranceReverted()]


class ActionSetSimplify(Action):

    def name(self) -> Text:
        return "action_set_simplify"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("is_simplify", True)]


class ActionSetMedicineTime(Action):

    def name(self) -> Text:
        return "action_set_medicinetime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("medicinetime", "NA")]


class ActionResetSimplify(Action):

    def name(self) -> Text:
        return "action_reset_simplify"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("is_simplify", False)]


class ActionSetSymptom(Action):

    def name(self) -> Text:
        return "action_set_symptom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_name = tracker.latest_message['intent'].get('name')
        if slot_name in intent2Symptom:
            slot_name = intent2Symptom[slot_name]

        return [SlotSet("symptom", slot_name)]


class ActionSetSlot(Action):

    def name(self) -> Text:
        return "action_set_slot"

    def get_next_slot(self, tracker: Tracker):
        active_loop = tracker.active_loop_name
        for x in symptom2Slots[active_loop]:
            if tracker.get_slot(x) is None:
                return x

        return None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            active_loop = tracker.active_loop.get("name")
            if active_loop is not None:
                next_slot = tracker.get_slot("requested_slot")
                user_inp = 'None'
                if next_slot != None:
                    user_inp = tracker.latest_message['text']

                return [SlotSet(next_slot, user_inp)]
            return []
        except Exception as e:
            return []
