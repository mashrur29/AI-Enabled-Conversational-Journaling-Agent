# Personal
#   Name (What do you want to be called?)
#   Age
#   Daily activities
# Medical
#   How long have you had Parkinson's? (how does this help us with journaling?)
#   Existing symptoms (What symptoms do you experience?)
#   What challenges do you face on a daily basis?
#   Prescribed medications

questions = [
    'What is your name?',
    'What is your age?',
    'Are there any activities that you do on a daily basis?',
    'How long have you had Parkinson\'s?',
    'What are your existing Parkinson\'s symptom?',
    'What challenges do you face on a daily basis?',
    'What are your prescribed medications?'
]

if __name__ == '__main__':

    for x in questions:
        print(x)
        inp = input()