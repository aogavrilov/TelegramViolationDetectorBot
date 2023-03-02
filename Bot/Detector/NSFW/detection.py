import string
import joblib
from pymorphy2 import MorphAnalyzer
import nltk
from nltk.corpus import stopwords
import torch
import math
from Bot.Detector.NSFW.model.bert.bert_classifier import BertClassifier

# Fast linear regression model
nltk.download('stopwords')
stopwords = stopwords.words("russian")
model = joblib.load('Bot/Detector/NSFW/model/nbc_model.pkl')
morph = MorphAnalyzer()
from transformers import logging
logging.set_verbosity_error()
# BERT Tiny model

bert_model = BertClassifier(
        model_path='cointegrated/rubert-tiny',
        tokenizer_path='cointegrated/rubert-tiny',
        n_classes=2,
        model_save_path='obscenity_bert.pt',
)
bert_model.model = torch.load('Bot/Detector/NSFW/model/bert/normal_bert.pt', map_location=torch.device('cpu'))


def document2tokenized_document(document):
    line = ""
    for ch in string.punctuation:
        document = document.replace(ch, "")
    for word in document.lower().split():
        if word not in stopwords:
            line += word + " "
    return line


def tokenized_document2lemmatized_document_fast(document_tokenized):
    line = ""
    for word in document_tokenized.split():
        line += morph.parse(word)[0].normal_form + " "
    return line


class DocumentsLemmatize:
    def __init__(self):
        self.X = None
        self.y = None

    def fit(self, X, y):
        return self

    @staticmethod
    def transform(x):
        x = document2tokenized_document(x)
        x = tokenized_document2lemmatized_document_fast(x)
        return [x]


lemmatizer = DocumentsLemmatize()

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def check_message_to_nsfw(message: str) -> bool:

    # Fast model with big recall
    if sigmoid(model.predict_log_proba(lemmatizer.transform(message))[0][0]) <= 0.01:
        return 0
    else:
        # BERT-tiny classifier
        return bert_model.predict(message) == 0
