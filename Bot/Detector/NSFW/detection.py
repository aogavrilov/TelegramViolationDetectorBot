import string
import joblib
from pymorphy2 import MorphAnalyzer
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stopwords = stopwords.words("russian")
model = joblib.load('Bot/Detector/NSFW/model/nbc_model.pkl')
morph = MorphAnalyzer()


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


def check_message_to_nsfw(message: str) -> bool:
    return model.predict(lemmatizer.transform(message)) == 0
