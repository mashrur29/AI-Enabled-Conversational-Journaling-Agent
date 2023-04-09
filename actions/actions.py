from typing import Any, Text, Dict, List

from rasa.core.actions.forms import FormAction
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from actions.dicts import intent2Symptom, symptom2Slots
from rasa_sdk.events import SlotSet, ActionReverted, AllSlotsReset
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.types import DomainDict

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
        dispatcher.utter_message(response="utter_please_rephrase")

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
        user_intent = tracker.latest_message['intent'].get('name')
        next_slot = ''

        try:
            next_slot = tracker.get_slot("requested_slot")
            user_inp = 'None'
            if next_slot != None:
                user_inp = tracker.latest_message['text']

            return [SlotSet(next_slot, user_inp)]
        except Exception as e:
            return []
