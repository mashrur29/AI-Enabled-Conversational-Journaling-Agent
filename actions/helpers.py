import openai
from actions.API import API_KEY_1, API_KEY_2


def create_dict(role, content):
    dict = {
        "role": role,
        "content": content
    }
    return dict


def get_symptom_fallback(previous_user_msg, prev_message):
    prompt_symptom_fallback = f"Acknowledge the previous response empathetically and be smart. Don't say anything else: {prev_message}"

    previous_user_msg.append(create_dict("user", prompt_symptom_fallback))

    utterance = get_response(previous_user_msg)
    return utterance.strip()


def get_symptom(prev_message):
    prompt = "Answer the following question, based on the data shown. " \
             "Answer in a single word and don't say anything else." \
             "The answer should be one of the following: \"tremor\", \"mood\", \"bradykinesia\", \"dizziness\", \"falling\", \"insomnia\", \"none\"" \
             f"data: {prev_message}"

    from actions.dicts import msg
    msg.append(create_dict("user", prompt))
    return get_response(msg).strip()


def get_chitchat_in_form(prev_message, symptom, requested_slot):
    prompt = f"Determine whether the user message is a chitchat. The user is journaling {symptom} for Parkinsons and was asked about {requested_slot}." \
             "If yes, acknowledge empathetically." \
             "Else respond with \"None\"" \
             f"user message: {prev_message}"

    from actions.dicts import msg
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
