from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from actions.helpers import create_dict, get_response


class ValidateProfileForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_profilejournal"

    # async def extract_name(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #
    #     if len(text) > 0:
    #         return {"name": text}

    def validate_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")

        if text is None:
            text = 'none'


        return {"name": text}


    # async def extract_age(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"age": text}

    def validate_age(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"age": text}

    # async def extract_daily_activity(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"daily_activity": text}

    def validate_daily_activity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"daily_activity": text}

    # async def extract_years_of_pd(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"years_of_pd": text}

    def validate_years_of_pd(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"years_of_pd": text}

    # async def extract_existing_symp(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"existing_symp": text}

    def validate_existing_symp(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"existing_symp": text}

    # async def extract_daily_challenges(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"daily_challenges": text}

    def validate_daily_challenges(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"daily_challenges": text}

    # async def extract_prescribed_meds(
    #         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     msg = []
    #     text = tracker.latest_message.get("text")
    #     if len(text) > 0:
    #         return {"prescribed_meds": text}

    def validate_prescribed_meds(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"prescribed_meds": text}

    def validate_prescribed_meds_purpose(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"prescribed_meds_purpose": text}



class ValidateMoodForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_moodjournaling"

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_reason(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"reason": text}


class ValidateInsomniaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_insomniajournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_severity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"severity": text}

    def validate_reason(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"reason": text}

class ValidateDizzinessForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_dizzinessjournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

    def validate_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"time": text}

    def validate_location(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"location": text}

    def validate_activity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"activity": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_severity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"severity": text}

    def validate_history(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"history": text}


class ValidateBradykinesiaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bradykinesiajournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}


class ValidateTremorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_tremorjournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_history(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"history": text}

class ValidateFallingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fallingjournaling"

    def validate_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"time": text}

    def validate_location(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"location": text}

    def validate_activity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"activity": text}

    def validate_severity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"severity": text}


class ValidateStiffnessForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_stiffnessjournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

class ValidateFatigueForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fatiguejournaling"

    def validate_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"time": text}

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

class ValidateDyskinesiaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_dyskinesiajournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}


class ValidateDystoniaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_dystoniajournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}

    def validate_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"time": text}

class ValidateBalanceForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_balancejournaling"

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

    def validate_devices(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"devices": text}

class ValidatePainForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_painjournaling"

    def validate_medicinetype(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetype": text}

    def validate_medicinetime(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"medicinetime": text}

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_duration(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"duration": text}

class ValidateWeaknessForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_weaknessjournaling"

    def validate_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"description": text}

    def validate_dailyactivity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"dailyactivity": text}

    def validate_cooccurrence(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"cooccurrence": text}

class ValidateClosingLoop(FormValidationAction):
    def name(self) -> Text:
        return "validate_closingloop"

    def validate_additional_symptom(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        return {"additional_symptom": text}

# class ValidateQuestionLoop(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_questionloop"
#
#     def validate_did_that_help(
#             self,
#             slot_value: Any,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         text = tracker.latest_message.get("text")
#         return {"did_that_help": text}