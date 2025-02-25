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
from rank_bm25 import BM25Okapi

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


def similarity_bm25(sent1, sent2):
    corpus = [sent2]
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = sent1.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)

    return abs(doc_scores[0])


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


def is_question_from_gpt(question):
    behavior = 'Answer in a single word. Don\'t say anything else'
    prompt = f'Imagine you are a journaling chatbot for assisting Parkinson\'s patients in recording their conditions. You are now talking to a Parkinson\'s patient. In the latest utterance, the user responded with {question}. Now, determine whether the latest user utterance is a question for you. Answer with only yes or no. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, temperature=0).lower()

    if 'yes' in out:
        return True
    return False


def check_medication_time(question, answer):
    behavior = 'Answer in a single word. Don\'t say anything else'
    prompt = f'Imagine you are a journaling chatbot for assisting Parkinson\'s patients in recording their conditions. You are now talking to a Parkinson\'s patient about their medication intake. In the latest utterance, the user responded with {answer} when asked, \'{question}\'. Now, determine whether this is sufficient to determine the medication intake time. For instance, if the user responds with \'yeah at noon\' when asked \'did you take your medication?\', then you should say yes. On the other hand, if the user responds with \'yes i took my meds\' when asked \'Did you take your levodopa medication?\', then you should say no. Again, if the user responds with \'yes\' when asked \'Did you take your meds at 8\', then you should say yes. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, temperature=0).lower()

    if 'yes' in out:
        return True
    return False


def get_latest_bot_message(events):
    latest_bot_message = ''
    for event in events:
        if (event.get("event") == "bot") and (event.get("event") is not None):
            latest_bot_message = event.get("text")
    if 'Let\'s go back to our conversation:' in latest_bot_message:
        latest_bot_message = latest_bot_message.replace('Let\'s go back to our conversation:', '')
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

def get_ack_init(previous_user_msg):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with a question.'
    prompt = f'Imagine you are a journaling agent for Parkinson\'s users. In the latest message the user responded with \'{previous_user_msg}\' when asked, \'What do you want to record?\'. Now, acknowledge the user empathetically. For instance, if the user says, \'I am not feeling well\' you should respond with, \'I am sorry to hear that you are feeling unwell\'. Again if the user says, \'i have a bad headache\', you should respond with, \'I am sorry to hear that you have a bad headache\'. If the user says, \'my tremor\', you should respond with, \'I am sorry to hear about your tremors\'. Again, if the user says, \'my leg stiffness is getting better\', you should respond with, \'I am glad to hear that your leg stiffness is getting better\'. And if the user says, \'the headache i previously mentioned is gone\', you should respond with, \'I am glad to hear that you no longer have headaches\'. Don\'t respond with a question for the user. Answer in a single line. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, 0.5)
    return out

def answer_user_query(previous_user_msg, latest_bot_message, history):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with a question.'
    prompt = 'Imagine you are a bot or a conversational agent who can help users journal their Parkinson\'s symptoms. The following is the conversation between you and a user:\n' + \
             f', '.join(
                 history) + f'The user is a Parkinson\'s patient and the latest utterance of the user is \'{previous_user_msg}\', when asked \'{latest_bot_message}\'. The latest user message was predicted as a question for the bot. Now, respond to the user in a single sentence. Don\'t respond with a question. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, 0.5)
    return out


def answer_user_confusion(previous_user_msg, latest_bot_message, history):
    behavior = 'Answer in a single line. Don\'t say anything else. And don\'t respond with a question.'
    prompt = 'Imagine you are a bot or a conversational agent who can help users journal their Parkinson\'s symptoms. The following is the conversation between you and a user:\n' + \
             f', '.join(
                 history) + f'The user is a Parkinson\'s patient and the latest utterance of the user is \'{previous_user_msg}\', when asked \'{latest_bot_message}\'. In the latest message the user expressed confusion. Now, clarify the user\'s confusion in a single sentence. For instance, if the user expresses confusion when asked, \'Did you take your medication?\', you should respond with something similar to \'I meant to ask whether you took your prescribed medications\'. Don\'t respond with a question. Don\'t say anything else.'

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


def get_personalized_greeting(sender_id):
    name = ''

    try:
        val = db.voicebot.profiles.find_one({"sender_id": sender_id})
        name = val['data'][0]['name']
    except Exception as e:
        logger.error(str(e))

    if len(name) == 0:
        return 'none'

    prompt = f'Imagine you are a Parkinson\'s journal that is talking to a user. Greet the user in a few words. Don\'t say anything else.'
    behavior = 'Answer in a single sentence. Don\'t say anything else.'

    context = [{'role': 'system', 'content': behavior},
               {'role': 'user', 'content': prompt}]

    out = get_response(context, temperature=0.4)

    return out + f" {name}"


@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def get_response(msg, temperature=0.4):
    API_KEY_1 = 'YOUR API KEY GOES HERE'
    numTries = 20
    for it in range(numTries):
        try:
            openai.api_key = API_KEY_1
            completion = completions_with_backoff(
                model="gpt-4-turbo-preview",
                messages=msg,
                temperature=temperature
            )
            response = str(completion.choices[0].message['content'])

            return response.strip()
        except Exception as e:
            print("ERR: ", str(e))
    return 'I\'m sorry, but I did not get that. Can you please repeat?'


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
                   prescribed_meds='paracetamols',
                   prescribed_meds_purpose='head ache'):
    timestamp = "{}".format(get_timestamp())

    if (len(name) == 0) or (len(age) == 0) or (len(daily_activity) == 0) or (len(years_of_pd) == 0) or (
            len(existing_symp) == 0) or (len(daily_challenges) == 0) or (len(prescribed_meds) == 0) or (
            len(prescribed_meds_purpose) == 0):
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
        "prescribed_medications_purpose": prescribed_meds_purpose,
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
