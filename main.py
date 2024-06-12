#This program will take a sentence and measure the sentiment: happy, sad, or neutral.
#Uses a dictionary file to check through common words.
#File is read from MongoDB DataBase.
#Depending on use purposes can adjust program sensitivity.
#Includes negate list to reverse sentiment of following words.
#Includes intensifier list to increase score for words.
#Can proccess commas and dots.


#Init Global Variables
import pymongo
FILE_PATH = "my_dict.txt" #if using a dictionary
SENSITIVITY = "auto" #range (0-2), 0 for high sens (short sent) 2 for low sens (long sent)
NEGATE_WORDS = [ #negate words list
    "not",
    "nor",
    "neither",
    "never",
    "none"
]
INTENSIFIER_WORDS = [ #intensifier words list
    "very", 
    "extremely", 
    "incredibly", 
    "exceedingly", 
    "absolutely", 
    "totally", 
    "utterly", 
    "exceptionally"
]


# Connect to MongoDB
client = pymongo.MongoClient() #For local connection leave empty.
db = client["test"] #DB Name
collection = db["my_dict"] #Collection Name


#Load Dictionary from MongoDB
def load_dict():
    word_dict = {}
    cursor = collection.find({})
    
    for document in cursor:
        for word, score in document.items():
            word_dict[word] = score

    return word_dict


#Analyze the sentiment of the sentence
def analyze_sentence(sent, word_dict, negate, intensifiers, sens):
    score = 0
    words = sent.split(" ")
    words = [word.strip(".,") for word in words]
    length = len(words)

    if sens == "auto": #calculate sens if set to auto
        if length > 50:
            sens = 2
        elif length > 15:
            sens = 1
        else:
            sens = 0

    for i, word in enumerate(words): #calculate score
        if word in word_dict:
            if words[i - 1] in intensifiers: #intensifier words
                if words[i - 2] in negate:
                    score -= word_dict[word] / 1.5
                else:
                    score += word_dict[word] * 1.5
            elif words[i - 1] in negate:  #negate words
                score -= word_dict[word]
            else:
                score += word_dict[word]

    if score > sens:  #calculate sentiment
        return "happy"
    elif score < -sens:
        return "sad"
    else:
        return "neutral"
        

#Main
my_dict = load_dict()
my_dict.pop("_id")
print("Welcome to Sentence Sentiment Analyzer v1.0 (to quit application type 'exit')")

while 1:
    input_sent = input(
        "Enter sentence to evaluate sentiment: ").lower().strip()
    if input_sent == "exit":
        break
    else:
        result = analyze_sentence(input_sent, my_dict, NEGATE_WORDS, INTENSIFIER_WORDS, SENSITIVITY)
        print("Result: ", result)
