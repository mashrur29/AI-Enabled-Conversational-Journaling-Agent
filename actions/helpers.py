import openai
from actions.API import API_KEY_1, API_KEY_2


def create_dict(role, content):
    dict = {
        "role": role,
        "content": content
    }
    return dict


def get_symptom_fallback(previous_user_msg, prev_message):
    prompt_symptom_fallback = f"Acknowledge the latest user response empathetically and be smart. Don't say anything else: {prev_message}"

    previous_user_msg.append(create_dict("user", prompt_symptom_fallback))

    utterance = get_response(previous_user_msg)
    previous_user_msg.pop()
    return utterance.strip()


def get_symptom(prev_message):
    prompt = "Answer the following question, based on the data shown. " \
             "Answer in a single word and don't say anything else." \
             "The answer should be one of the following: \"tremor\", \"mood\", \"bradykinesia\", \"dizziness\", \"falling\", \"insomnia\", \"none\"" \
             f"data: {prev_message}"

    from actions.dicts import msg
    msg.append(create_dict("user", prompt))
    return get_response(msg).strip()


def get_chitchat(msg, prev_message):
    prompt = f"Determine whether the previous user message contains a question for the assistant. " \
             "Respond with a \"Yes\" or \"No\"." \
             f"previous user message: {prev_message}"

    msg.append(create_dict("user", prompt))
    utter = get_response(msg).strip()

    msg.pop()

    return utter

def get_chitchat_ack(msg, prev_message):
    prompt = "Acknowledge the previous user response empathetically. Don't say anything else." \
             f"previous user message: {prev_message}"

    msg.append(create_dict("user", prompt))
    utter = get_response(msg).strip()

    msg.pop()

    return utter

def get_chitchat_in_form(prev_message, symptom, requested_slot):
    prompt = f"The user is journaling {symptom} for Parkinsons and was asked about {requested_slot}." \
             "Acknowledge the user message empathetically." \
             f"user message: {prev_message}"

    from actions.dicts import msg
    det_chitchat = get_chitchat(msg, prev_message)

    if "no" in det_chitchat.lower():
        return "None"

    msg.append(create_dict("user", prompt))
    return get_response(msg).strip()


def get_response_in_form(prev_message, symptom):
    prompt = f"Acknowledge the user response below based on the fact that you are journaling their {symptom} for Parkinsons - {prev_message}"
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
