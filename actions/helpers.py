from datetime import datetime

import openai
from actions.API import API_KEY_1, API_KEY_2
from database import db
from actions.dicts import prompt_determine_sidetalk, prompt_sidetalk_response, prompt_form_ack, \
    prompt_determine_symptom, \
    prompt_symptom_fallback_ack, prompt_generic

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


def get_symptom(conv_context):
    prompt_determine_symptom.extend(conv_context)
    prompt_determine_symptom.append(
        {'role': 'user',
         'content': 'Which symptom is the user talking about? The answer should be one of the following: tremor, mood, bradykinesia, dizziness, falling, insomnia, and none. Answer in a single word without punctuation.'}
    )
    res = get_response(prompt_determine_symptom, temperature=0).strip()
    res = res.replace('.', '').lower()
    return res


def determine_chitchat(conv_context):
    prompt_determine_sidetalk.extend(conv_context)
    prompt_determine_sidetalk.append(
        {"role": "user",
         "content": f"Is \'{conv_context[-1]['content']}\' a question for the assistant? Respond only with a yes or no. Don't say anything else."}
    )
    utter = get_response(prompt_determine_sidetalk, temperature=0).strip()
    utter = utter.replace('.', '').lower()
    return utter


def get_symptom_fallback(conv_context):
    prompt_symptom_fallback_ack.extend(conv_context)
    prompt_symptom_fallback_ack.append(
        {"role": "user",
         "content": f"Acknowledge \'{conv_context[-1]['content']}\'. Don't ask any questions. Also answer in a single sentence."}
    )
    utterance = get_response(prompt_symptom_fallback_ack)
    return utterance.strip()


def get_chitchat_ack(conv_context):
    prompt_sidetalk_response.extend(conv_context)
    prompt_sidetalk_response.append(
        {"role": "user",
         "content": f"Respond to \'{conv_context[-1]['content']}\'. Don\'t respond with a question."}
    )
    utter = get_response(prompt_sidetalk_response).strip()
    return utter


def get_chitchat_in_form(conv_context):
    prompt_sidetalk_response.extend(conv_context)
    prompt_sidetalk_response.append(
        {"role": "user",
         "content": f"Respond to \'{conv_context[-1]['content']}\'. Don\'t respond with a question."}
    )

    return get_response(prompt_sidetalk_response).strip()


def get_response_in_form(conv_context):
    prompt_form_ack.extend(conv_context)
    prompt_form_ack.append(
        {"role": "user", "content": f"Respond to \'{conv_context[-1]['content']}\' without asking any questions."}
    )
    return get_response(prompt_form_ack).strip()


def get_response_generic(conv_context):
    prompt_generic.extend(conv_context)
    return get_response(prompt_generic).strip()


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
    try:
        db.voicebot.profiles.insert_one({"sender_id": senderid})
        print(f'Profile created for {senderid}')
    except Exception as e:
        print(f'Profile creation failed for {senderid}')


def get_conv_context(events, history=4):
    conv_utter = []

    for event in reversed(events):
        if (event.get("event") == "bot") and (event.get("event") is not None):
            latest_bot_message = event.get("text")
            conv_utter.append(create_dict("assistant", latest_bot_message))
            history = history - 1
        elif (event.get("event") == "user") and (event.get("event") is not None):
            latest_user_message = event.get("text")
            conv_utter.append(create_dict("user", latest_user_message))
            history = history - 1
        if history == 0:
            break

    conv_utter.reverse()
    return conv_utter


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
        "sender identification": senderid,
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
        init_profile(senderid)
        id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
    try:
        db.voicebot.profiles.update_one({"_id": id_}, {'$push': {"data": data}})
    except Exception as e:
        print("Profile update failed for {}: {}".format(senderid, str(e)))
