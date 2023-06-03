from datetime import datetime

import openai
from actions.API import API_KEY_1, API_KEY_2
from database import db

symptom2form = {
    "tremor": "tremorjournaling",
    "bradykinesia": "bradykinesiajournaling",
    "dizziness": "dizzinessjournaling",
    "falling": "fallingjournaling",
    "insomnia": "insomniajournaling",
    "mood": "moodjournaling"
}

symptoms = [
    "tremor",
    "bradykinesia",
    "dizziness",
    "falling",
    "insomnia",
    "mood"
]


def create_dict(role, content):
    dict = {
        "role": role,
        "content": content
    }
    return dict


def get_symptom_fallback(previous_user_msg, prev_message):
    prompt_symptom_fallback = f"Acknowledge the latest user response empathetically and be smart. Don't say anything else or ask questions. User message: {prev_message}"

    previous_user_msg.append(create_dict("user", prompt_symptom_fallback))

    utterance = get_response(previous_user_msg)
    previous_user_msg.pop()
    return utterance.strip()


def get_symptom(prev_message):
    prompt = "Answer the following question, based on the data shown. " \
             "Answer in a single word and don't say anything else. " \
             "The answer should be one of the following: \"tremor\", \"mood\", \"bradykinesia\", \"dizziness\", \"falling\", \"insomnia\", \"none\"" \
             f"data: {prev_message}"

    from actions.dicts import msg
    msg.append(create_dict("user", prompt))
    return get_response(msg).strip()


def get_chitchat(msg, prev_message):
    prompt = f"Determine whether the user message contains a question for the assistant. " \
             "Respond only with a \"Yes\" or \"No\"." \
             f"user message: {prev_message}"

    msg.append(create_dict("user", prompt))
    utter = get_response(msg).strip()

    msg.pop()

    return utter


def get_chitchat_ack(msg, prev_message):
    prompt = "Acknowledge the previous user response empathetically. Don't say anything else or ask questions. " \
             f"previous user message: {prev_message}"

    msg.append(create_dict("user", prompt))
    utter = get_response(msg).strip()

    msg.pop()

    return utter


def get_chitchat_in_form(prev_message, symptom, requested_slot):
    prompt = f"In context of {symptom}-symptom for Parkinson a userv is asked about {requested_slot}. Acknowledge the user message empathetically. " \
             f"Don't say anything else or ask questions. " \
             f"user message: {prev_message}"

    from actions.dicts import msg
    det_chitchat = get_chitchat(msg, prev_message)

    if "no" in det_chitchat.lower():
        return "None"

    msg.append(create_dict("system", prompt))
    return get_response(msg).strip()


def get_response_in_form(prev_message, symptom):
    prompt = f"Acknowledge the user response below in context of {symptom}-symptom for Parkinson - {prev_message}. Don't say more than 1 sentence or ask a question."
    from actions.dicts import msg
    msg.append(create_dict("user", prompt))
    return get_response(msg).strip()


def get_response(msg, temperature=0.4):
    while True:
        try:
            openai.api_key = API_KEY_1
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=msg,
                temperature=temperature
            )
            response = str(completion.choices[0].message['content'])
            return response.strip()
        except Exception as e:
            try:
                openai.api_key = API_KEY_2
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=msg,
                    temperature=temperature
                )
                response = str(completion.choices[0].message['content'])
                return response.strip()
            except Exception as e1:
                return "I'm sorry, I didn't quite understand that. Could you rephrase?"
            pass


def get_timestamp():
    now = datetime.now()
    return "{}".format(now.strftime("%m/%d/%Y, %H:%M:%S"))


def check_profile(senderid):
    exists = False
    try:
        id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
        exists = True
    except Exception as e:
        exists = False
    return exists


def init_profile(senderid):
    db.voicebot.profiles.insert_one({"sender_id": senderid})


def update_profile(senderid,
                   name='John Doe',
                   age='65',
                   daily_activity='i like to cook',
                   years_of_pd='10 years',
                   existing_symp='tremors',
                   daily_challenges='difficulty moving arms',
                   prescribed_meds='paracetamols'):
    timestamp = "{}".format(get_timestamp())

    data = {
        "name": name,
        "age": age,
        "daily_activity": daily_activity,
        "years_of_pd": years_of_pd,
        "existing_symptoms": existing_symp,
        "daily_challenges": daily_challenges,
        "prescribed_medications": prescribed_meds
    }

    try:
        id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
    except Exception as e:
        print("Profile doesn't exist")
        # db.voicebot.profiles.insert_one({"sender_id": senderid})
        # id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
    try:
        db.voicebot.profiles.update_one({"_id": id_}, {'$push': {"data": data}})
    except Exception as e:
        print("[Profile update failed] {}".format(str(e)))
