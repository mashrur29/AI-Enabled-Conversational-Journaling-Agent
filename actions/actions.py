import random
from datetime import datetime
from typing import Any, Text, Dict, List
from rasa.core.actions.forms import FormAction
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from actions.dicts import intent2Symptom, symptom2form
from rasa_sdk.events import SlotSet, ActionReverted, AllSlotsReset, FollowupAction
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.types import DomainDict
from actions.helpers import create_dict, get_response, get_symptom, get_symptom_fallback, get_response_in_form, \
    get_chitchat_in_form, determine_chitchat, get_chitchat_ack, check_profile, update_profile, init_profile, \
    symptom2form, \
    symptoms, get_conv_context, get_response_generic, is_question, get_conv_context_raw, answer_user_query, \
    get_generic_ack, get_latest_bot_message, is_question_from_gpt, get_personalized_greeting, check_medication_time, \
    get_ack_init, answer_user_confusion
from utils import logger


class ActionPersonalizedGreeting(Action):

    def name(self) -> Text:
        return "action_personalized_greeting"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            sender_id = tracker.sender_id
            logger.info(f'Generating greeting for: {sender_id}')
            greet = get_personalized_greeting(sender_id)

            if greet == 'none':
                return []

            dispatcher.utter_message(greet)

        except Exception as e:
            logger.error(f"User name doesn\'t exist: {str(e)}")

        return []


class ActionCreateUserProfile(Action):

    def name(self) -> Text:
        return "action_create_user_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            sender_id = tracker.sender_id

            name = tracker.get_slot('name')
            age = tracker.get_slot('age')
            daily_activity = tracker.get_slot('daily_activity')
            years_of_pd = tracker.get_slot('years_of_pd')
            existing_symp = tracker.get_slot('existing_symp')
            daily_challenges = tracker.get_slot('daily_challenges')
            prescribed_meds = tracker.get_slot('prescribed_meds')
            prescribed_meds_purpose = tracker.get_slot('prescribed_meds_purpose')

            if (len(name) == 0) or (len(age) == 0) or (len(daily_activity) == 0) or (len(years_of_pd) == 0) or (
                    len(existing_symp) == 0) or (len(daily_challenges) == 0) or (len(prescribed_meds) == 0) or (
                    len(prescribed_meds_purpose) == 0):
                logger.error('Incomplete profile')
                return []

            if check_profile(sender_id) == False:
                init_profile(sender_id)

            update_profile(sender_id, name, age, daily_activity, years_of_pd, existing_symp, daily_challenges,
                           prescribed_meds, prescribed_meds_purpose)
            logger.info(f'Profile updated for {sender_id}')
        except Exception as e:
            logger.error("Profile update failed for {}".format(tracker.sender_id))
        return []


class ActionUserCheckProfile(Action):

    def name(self) -> Text:
        return "action_check_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = tracker.sender_id

        logger.info(f'Checking profile for {sender_id}')

        try:
            if check_profile(sender_id):
                return [SlotSet("check_profile", "true")]
            else:

                # init_profile(sender_id)
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
        return [AllSlotsReset()]


class ActionGenericAcknowledge(Action):

    def name(self) -> Text:
        return "action_generic_acknowledge"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info('Inside generic acknowledge')
        previous_user_msg = tracker.latest_message["text"]
        bot_response = get_generic_ack(previous_user_msg, get_conv_context_raw(tracker.events, 20))
        dispatcher.utter_message(bot_response)

        return []


class ActionAnswerQuestion(Action):

    def name(self) -> Text:
        return "action_answer_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info('Predicted user message is a question outside fallback')
        previous_user_msg = tracker.latest_message["text"]
        latest_bot_message = get_latest_bot_message(tracker.events)
        bot_response = answer_user_query(previous_user_msg, latest_bot_message,
                                         get_conv_context_raw(tracker.events, 20))
        dispatcher.utter_message(bot_response)

        dispatcher.utter_message(f'Let\'s go back to our conversation: {latest_bot_message}')

        active_loop = tracker.active_loop.get("name")

        if active_loop is not None:
            return [UserUtteranceReverted()]

        return []


class ActionAnswerConfusion(Action):

    def name(self) -> Text:
        return "action_answer_confusion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info('Predicted user message is a confusion outside fallback')
        previous_user_msg = tracker.latest_message["text"]
        latest_bot_message = get_latest_bot_message(tracker.events)
        bot_response = answer_user_confusion(previous_user_msg, latest_bot_message,
                                         get_conv_context_raw(tracker.events, 20))
        dispatcher.utter_message(bot_response)

        dispatcher.utter_message(f'Let\'s go back to our conversation: {latest_bot_message}')

        active_loop = tracker.active_loop.get("name")

        if active_loop is not None:
            return [UserUtteranceReverted()]

        return []


class ActionAckInit(Action):

    def name(self) -> Text:
        return "action_ack_init"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info('Acknowledging initial user input')
        previous_user_msg = tracker.latest_message["text"]
        acknowledgement = get_ack_init(previous_user_msg)

        dispatcher.utter_message(acknowledgement)

        return []


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

        logger.info('Inside fallback')

        active_loop = tracker.active_loop.get("name")

        if active_loop is not None:
            logger.info(f'Active Loop: {active_loop}')

            next_slot = tracker.get_slot("requested_slot")
            logger.info(f'Requested slot: {next_slot}')

            previous_user_msg = tracker.latest_message["text"]
            logger.info(f'Previous user message: {previous_user_msg}')

            latest_bot_message = get_latest_bot_message(tracker.events)
            logger.info(f'Latest bot message: {latest_bot_message}')

            try:
                if previous_user_msg[-1] == '.':
                    previous_user_msg = previous_user_msg[:-1]
            except Exception as e:
                logger.error(str(e))

            if (active_loop != 'closingloop'):
                dispatcher.utter_message(response='utter_acknowledge')

            try:
                if next_slot == 'medicinetype':
                    if check_medication_time(latest_bot_message, previous_user_msg):
                        return [SlotSet(next_slot, previous_user_msg), SlotSet('medicinetime', previous_user_msg),
                                FollowupAction(active_loop)]
            except Exception as e:
                logger.error(str(e))

            return [SlotSet(next_slot, previous_user_msg), FollowupAction(active_loop)]

        logger.info('No active loop in fallback, asking user to start')

        previous_user_msg = tracker.latest_message["text"]
        bot_response = get_generic_ack(previous_user_msg, get_conv_context_raw(tracker.events, 20))
        dispatcher.utter_message(bot_response)

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
        dispatcher.utter_message(response="utter_asr_repeat")

        latest_bot_message = get_latest_bot_message(tracker.events)
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

        previous_user_msg = tracker.latest_message["text"]
        slots_to_set = []
        slots_to_set.append(SlotSet("symptom", slot_name))
        # slots_to_set.append(SlotSet("bulk_report", False))

        return slots_to_set


class ActionSetSlot(Action):

    def name(self) -> Text:
        return "action_set_slot"

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

                logger.info(f'Setting slot {next_slot} for {active_loop}')

                return [SlotSet(next_slot, user_inp)]
            return []
        except Exception as e:
            return []


class ActionSetActiveloop(Action):

    def name(self) -> Text:
        return "action_set_activeloop"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        active_loop = tracker.active_loop.get("name")
        latest_bot_message = get_latest_bot_message(tracker.events)

        logger.info('Setting activeloop & prev_utter')

        if active_loop is not None:
            return [SlotSet('qna_prev_utterance', latest_bot_message), SlotSet('activeloop', active_loop)]

        return [SlotSet('qna_prev_utterance', latest_bot_message)]


class ActionReactivateForm(Action):

    def name(self) -> Text:
        return "action_reactivate_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        activeloop = tracker.get_slot("activeloop")

        prev_utterance = tracker.get_slot("qna_prev_utterance")
        dispatcher.utter_message(text=f'Let\'s go back to our conversation.')

        if activeloop != 'none':
            logger.info(f'Reactivating {activeloop}')
            return [SlotSet('did_that_help', None), SlotSet('activeloop', 'none'), FollowupAction(activeloop)]

        logger.info('No active forms to reactivate')

        if len(prev_utterance) != 0:
            dispatcher.utter_message(prev_utterance)
        else:
            dispatcher.utter_message(text='You can start by saying \'hi\'.')
        return [SlotSet('did_that_help', None), SlotSet('activeloop', 'none')]
