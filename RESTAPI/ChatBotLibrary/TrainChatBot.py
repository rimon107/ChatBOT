# things we need for NLP
import nltk
import pymssql
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import os


# import our chat-bot intents file

#conn = pymssql.connect(host='192.168.100.139', user='sa', password='dataport', database='Sentiment')

#cursor = conn.cursor()

#cursor.callproc('usp_SentimentBotData')
#cursor.nextset()
#results = cursor.fetchall()


#testt = json.dumps(str(results))
#print("testt")
#print(testt)

trainingDatafileName = 'intents.json'

path = os.getcwd() + '\\'

intentFile = path + trainingDatafileName

# with open(intentFile) as json_data:
#     intents = json.load(json_data)
#     print("intents")
#     print(intents)

with open(intentFile) as json_data:
    # intents = json.load(json_data)
    print("intents")
    # print(intents)
    conn = pymssql.connect(host='192.168.100.61', user='sa', password='dataport', database='ChatBot')
    cursor = conn.cursor()

    sql ="SELECT \
      tag \
      ,[patterns] \
      ,[responses] \
  FROM [ChatBot].[dbo].[xxx]"


    cursor.execute(sql)

    dataset = cursor.fetchall()

    columns = [col[0] for col in cursor.description]

    results = [
        dict(zip(columns, row))
        for row in dataset
    ]

    intnt = {
        'intents' : []
    }

    for res in results:
        intentDict = {
            "tag": res['tag'],
            "patterns": [res['patterns']],
            "responses": [res['responses']]
        }

        intnt["intents"].append(intentDict)


    intents = intnt



words = []
classes = []
documents = []
ignore_words = ['?']
# loop through each sentence in our intents patterns
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenize each word in the sentence
        w = nltk.word_tokenize(pattern)
        # add to our words list
        words.extend(w)
        # add to documents in our corpus
        documents.append((w, intent['tag']))
        # add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# remove duplicates
classes = sorted(list(set(classes)))
#
# print (len(documents), "documents")
# print (len(classes), "classes", classes)
# print (len(words), "unique stemmed words", words)





# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    # stem each word
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # create our bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

# shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training)

# create train and test lists
train_x = list(training[:,0])
train_y = list(training[:,1])





# reset underlying graph data
tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

modelFileName = 'tflearn_logs'

modelFile = path + modelFileName

tfModelFileName = 'model.tflearn'

tfModelFile = path + tfModelFileName



# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir=modelFile)
#model.load(tfModelFile)

# Start training (apply gradient descent algorithm)
model.fit(train_x, train_y, n_epoch=150, batch_size=8, show_metric=True)
model.save(tfModelFile)

trainingDatafileName = 'training_data'
trainingDatafile = path + trainingDatafileName


# save all of our data structures
import pickle
pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( trainingDatafile, "wb" ) )