# "And ask if the user wants to journal either of the following: \"tremor\", \"mood\", \"bradykinesia\", \"dizziness\", \"falling\", \"insomnia\"."

prompt_determine_sidetalk = [
    {"role": "system",
     "content": "Answer in a single word and don\'t say anything else."}
]

prompt_sidetalk_response = [
    {"role": "system", "content": "Don't ask any questions and be empathetic. Also answer in a single sentence."}
]
prompt_form_ack = [
    {"role": "system", "content": "Don't ask any questions and be empathetic. Also answer in a single sentence."}
]
prompt_determine_symptom = [
    {"role": "system", "content": "Answer in a single word and don\'t say anything else."}
]
prompt_determine_topicswitch = [
    {"role": "system", "content": "Answer in a single word and don\'t say anything else."}
]
prompt_symptom_fallback_ack = [
    {"role": "system", "content": "Don't ask any questions and be empathetic. Also answer in a single sentence."}
]

prompt_generic = [
    {"role": "system", "content": "Don't ask any questions and be empathetic. Also answer in a single sentence."}
]

profile_prompt = "The following is a user\'s personal information. " \
                 "Age: {}, Daily activities: {}, " \
                 "Length the user had Parkinsons: {}, Existing parkinsons symptoms: {}, Daily challenges: {}, " \
                 "Prescribed medications: {}."

intent2Symptom = {
    "trigger_tremor_mild": "tremor",
    "trigger_tremor_severe": "tremor",
    "trigger_tremor_frequency": "tremor",
    "trigger_tremor_location": "tremor",
    "trigger_current_tremors": "tremor",
    "trigger_bradykinesia_1": "bradykinesia",
    "trigger_bradykinesia_2": "bradykinesia",
    "trigger_dizziness": "dizziness",
    "trigger_falling_1": "falling",
    "trigger_falling_2": "falling",
    "trigger_insomnia": "insomnia",
    "trigger_mood_1": "mood",
    "trigger_mood_2": "mood",
    "trigger_mood_3": "mood"
}

symptom2form = {
    "tremorjournaling": [
        "medicinetype",
        "medicinetime",
        "duration",
        "cooccurrence",
        "dailyactivity",
        "history"
    ]
}
