import random
from typing import Any, Text, Dict, List

from rasa.core.actions.forms import FormAction
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from actions.dicts import intent2Symptom, symptom2Slots
from rasa_sdk.events import SlotSet, ActionReverted, AllSlotsReset
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.types import DomainDict

from actions.helpers import create_dict, get_response


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
        all_msg = []
        for event in tracker.events:
            if (event.get("event") == "bot") or (event.get("event") == "user"):
                latest_bot_message = event.get("text")
                all_msg.append('{}> {}'.format(event.get("event"), latest_bot_message))
        #print(all_msg)
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

        from actions.dicts import msg

        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                latest_bot_message = event.get("text")
                msg.append(create_dict("assistant", latest_bot_message))
            elif (event.get("event") == "user") and (event.get("event") is not None):
                latest_user_message = event.get("text")
                msg.append(create_dict("user", latest_user_message))

        utterance = get_response(msg)
        dispatcher.utter_message(text=utterance)
        # Revert user message which led to fallback.
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
            user_intent = tracker.latest_message['intent'].get('name')
            next_slot = ''
            next_slot = tracker.get_slot("requested_slot")
            user_inp = 'None'
            if next_slot != None:
                user_inp = tracker.latest_message['text']

            return [SlotSet(next_slot, user_inp)]
        except Exception as e:
            return []
