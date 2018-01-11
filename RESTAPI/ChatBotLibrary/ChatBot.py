# things we need for NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
import json
# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import os
import pymssql


def dictfetchall(cur):
    dataset = cur.fetchall()
    columns = [col[0] for col in cur.description]
    return [
        dict(zip(columns, row))
        for row in dataset
        ]

trainingDatafileName = 'training_data'

path = os.getcwd() + '\\RESTAPI\\ChatBotLibrary\\'

file = path + trainingDatafileName

data = pickle.load(open(file, "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

logFolder = path + 'tflearn_logs'
# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_verbose=3, tensorboard_dir=logFolder)

# import our chat-bot intents file

jsonFileName = 'intents.json'
file = path + jsonFileName
with open(file) as json_data:
    # intents = json.load(json_data)
    # print("intents")
    # print(intents)
    conn = pymssql.connect(host='192.168.100.61', user='sa', password='dataport', database='ChatBot')
    cursor = conn.cursor()

    sql = "SELECT  \
          tag \
          ,[patterns] \
          ,[responses] \
      FROM [ChatBot].[dbo].[TrainChatBot]"

    cursor.execute(sql)

    dataset = cursor.fetchall()

    columns = [col[0] for col in cursor.description]

    results = [
        dict(zip(columns, row))
        for row in dataset
    ]

    intnt = {
        'intents': []
    }

    for res in results:
        # intentDict['patterns'].append(res['patterns'])
        # intentDict['responses'].append(res['responses'])

        intentDict = {
            "tag": res['tag'],
            "patterns": [res['patterns']],
            "responses": [res['responses']]
        }

        intnt["intents"].append(intentDict)

    intents = intnt

# load our saved model
file = path + 'model.tflearn'
model.load(file)


def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    flag = False
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1

                if show_details:
                    print("found in bag: %s" % w)
                # flag = True
                # break
        # if flag== True:
        #     break

    return (np.array(bag))


def GetResultFromDatabase(text):
    conn = pymssql.connect(host='192.168.100.61', user='sa', password='dataport', database='ChatBot')
    cursor = conn.cursor()
    sql = "SELECT  [responses] \
            FROM [dbo].[TrainChatBot] \
            WHERE patterns like '%%" + str(text) + "%%'"

    try:
        cursor.execute(sql)

        dataset = cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        results = [
            dict(zip(columns, row))
            for row in dataset
        ]


        response = results[0]['responses']
    except Exception:
        response = ""

    if response == "":
        return False, response
    else:
        return True, response


context = {}

# ERROR_THRESHOLD = 0.25

ERROR_THRESHOLD = 0.25

def classify(sentence):
    # generate probabilities from the model
    res = [bow(sentence, words)]
    resultList = model.predict(res)
    results = resultList[0]
    # filter out predictions below a threshold
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
    # results = [[i, r] for i, r in enumerate(results) ]
    # sort by strength of probability
    # results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list


def response(sentence, userID='123', show_details=False):
    status, response = GetResultFromDatabase(sentence)

    #status = False

    if status == False:
        results = classify(sentence)
        # if we have a classification then find the matching intent tag
        if results:
            # loop as long as there are matches to process
            while results:
                for i in intents['intents']:
                    # find a tag matching the first result

                    if i['tag'] == results[0][0]:
                        # set context for this intent if necessary
                        if 'context_set' in i:
                            if show_details: print('context:', i['context_set'])
                            context[userID] = i['context_set']

                        # check if this intent is contextual and applies to this user's conversation
                        if not 'context_filter' in i or \
                                (userID in context and 'context_filter' in i and i['context_filter'] == context[
                                    userID]):
                            if show_details:
                                print('tag:', i['tag'])
                            # a random response from the intent
                            return i['responses']

                results.pop(0)
    else:
        return response

# print(response('we want to rent a moped'))

# print(response('yesterday'))

# print(response("thanks, your great"))




