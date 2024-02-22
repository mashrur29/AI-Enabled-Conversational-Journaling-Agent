from datetime import datetime
from openai.error import RateLimitError
import backoff as backoff
import openai
from actions.API import API_KEY_1, API_KEY_2, API_KEY_3, API_KEY_4
from database import db
from actions.dicts import prompt_determine_sidetalk, prompt_sidetalk_response, prompt_form_ack, \
    prompt_determine_symptom, \
    prompt_symptom_fallback_ack, prompt_generic
from utils import logger
import pickle
import nltk

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


f = open('models/naive_classifier_ques.pickle', 'rb')
classifier = pickle.load(f)
f.close()
question_types = ["whQuestion", "ynQuestion"]

question_pattern = ["do i", "do you", "what", "who", "is it", "why", "would you", "how", "is there",
                    "are there", "is it so", "is this true", "to know", "is that true", "are we", "am i",
                    "question is", "tell me more", "can i", "can we", "tell me", "can you explain",
                    "question", "answer", "questions", "answers", "ask"]

helping_verbs = ["is", "am", "can", "are", "do", "does"]


def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features


def is_ques_using_nltk(ques):
    question_type = classifier.classify(dialogue_act_features(ques))
    return question_type in question_types


def is_question(question):
    question = question.lower().strip()
    if not is_ques_using_nltk(question):
        is_ques = False
        for pattern in question_pattern:
            is_ques = pattern in question
            if is_ques:
                break

        sentence_arr = question.split(".")
        for sentence in sentence_arr:
            if len(sentence.strip()):
                first_word = nltk.word_tokenize(sentence)[0]
                if sentence.endswith("?") or first_word in helping_verbs:
                    is_ques = True
                    break
        return is_ques
    else:
        return True

def is_question_from_pattern(question):
    question = question.lower().strip()
    question_pattern = ["do i", "do you", "what", "who", "is it", "why", "would you", "how", "is there",
                        "are there", "is it so", "is this true", "to know", "is that true", "are we", "am i",
                        "question is", "tell me more", "can i", "can we", "tell me", "can you explain",
                        "question", "answer", "questions", "answers", "ask"]
    helping_verbs = ["is", "am", "can", "are", "do", "does"]
    is_ques = False
    for pattern in question_pattern:
        is_ques = pattern in question
        if is_ques:
            break
    sentence_arr = question.split(".")
    for sentence in sentence_arr:
        if len(sentence.strip()):
            first_word = nltk.word_tokenize(sentence)[0]
            if sentence.endswith("?") or first_word in helping_verbs:
                is_ques = True
                break
    return is_ques

def get_latest_bot_message(events):
    latest_bot_message = ''
    for event in events:
        if (event.get("event") == "bot") and (event.get("event") is not None):
            latest_bot_message = event.get("text")
    if 'Let\'s gently circle back to our conversation:' in latest_bot_message:
        latest_bot_message = latest_bot_message.replace('Let\'s gently circle back to our conversation:', '')
    return latest_bot_message.strip()

def get_generic_ack(previous_user_msg, history):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with a question.'
    prompt = 'Imagine you are a bot or a conversational agent who can help users journal their Parkinson\'s symptoms. The following is the conversation between you and a user:\n' + \
             f', '.join(
                 history) + f'The user is a Parkinson\'s patient and the latest utterance of the user is {previous_user_msg}. Now, acknowledge the user\'s latest utterance in a single sentence. Include information from the conversation context in the acknowledgement, whenever necessary. Don\'t respond with a question. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, 0.5)
    return out


def answer_user_query(previous_user_msg, latest_bot_message, history):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with a question.'
    prompt = 'Imagine you are a bot or a conversational agent who can help users journal their Parkinson\'s symptoms. The following is the conversation between you and a user:\n' + \
             f', '.join(
                 history) + f'The user is a Parkinson\'s patient and the latest utterance of the user is \'{previous_user_msg}\', when asked \'{latest_bot_message}\'. The latest user message was predicted as a question for the bot. Now, respond to the user in a single sentence. Don\'t respond with a question for the user. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, 0.5)
    return out


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


def check_bulk_report(previous_user_msg):
    pass


@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def get_response(msg, temperature=0.4):
    API_KEY_1 = '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'
    numTries = 20
    for it in range(numTries):
        try:
            openai.api_key = API_KEY_1
            completion = completions_with_backoff(
                model="gpt-4",
                messages=msg,
                temperature=temperature
            )
            response = str(completion.choices[0].message['content'])

            return response.strip()
        except Exception as e:
            print("ERR: ", str(e))
    return 'none'


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
        logger.info(f'Profile created for {senderid}')
    except Exception as e:
        logger.error(f'Profile creation failed for {senderid}')


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


def get_conv_context_raw(events, history=4):
    conv_utter = []

    for event in reversed(events):
        if (event.get("event") == "bot") and (event.get("event") is not None):
            latest_bot_message = event.get("text")
            conv_utter.append(f'bot: {latest_bot_message}')
            history = history - 1
        elif (event.get("event") == "user") and (event.get("event") is not None):
            latest_user_message = event.get("text")
            conv_utter.append(f'user: {latest_user_message}')
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

    if (len(name) == 0) or (len(age) == 0) or (len(daily_activity) == 0) or (len(years_of_pd) == 0) or (
            len(existing_symp) == 0) or (len(daily_challenges) == 0) or (len(prescribed_meds) == 0):
        logger.error('Incomplete profile!')
        return

    data = {
        "sender_id": senderid,
        "name": name,
        "age": age,
        "daily_activity": daily_activity,
        "years_of_pd": years_of_pd,
        "existing_symptoms": existing_symp,
        "daily_challenges": daily_challenges,
        "prescribed_medications": prescribed_meds,
        "timestamp": timestamp
    }

    try:
        id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
    except Exception as e:
        logger.error("Profile doesn't exist")
        init_profile(senderid)
        id_ = db.voicebot.profiles.find_one({"sender_id": senderid})['_id']
    try:
        db.voicebot.profiles.update_one({"_id": id_}, {'$push': {"data": data}})
    except Exception as e:
        logger.error("Profile update failed for {}: {}".format(senderid, str(e)))
