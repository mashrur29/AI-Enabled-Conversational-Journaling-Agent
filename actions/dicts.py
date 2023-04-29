with open('actions/chatgpt_prompt', 'r') as file:
    data = file.read().replace('\n', '').strip()

chatbot_behavior = str(data)

# "And ask if the user wants to journal either of the following: \"tremor\", \"mood\", \"bradykinesia\", \"dizziness\", \"falling\", \"insomnia\"."

msg = [
    {"role": "system", "content": "Be empathetic."},
    {"role": "system", "content": "Answer in a single line and don't say anything else."}
]

msg_symptom = [
    {"role": "system", "content": "Answer in a single word and don't say anything else."}
]

msg_symptom_fallback = [
    {"role": "system", "content": "Answer in a short and empathetic manner. Don't say anything else."}
]

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

symptom2Slots = {
    "tremorjournaling": [
        "medicinetype",
        "medicinetime",
        "duration",
        "cooccurrence",
        "dailyactivity",
        "history"
    ]
}
