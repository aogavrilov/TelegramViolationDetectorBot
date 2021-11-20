import sys

import torch
#from torch import load, Tens
import json
import numpy as np
import re
import scipy.sparse
import pickle

'''
MODEL_PATH = 'Bot/Detector/NSFW/model/model_for_eval'
model = torch.load(MODEL_PATH, map_location='cpu')
model.eval()

VOCABULARY_PATH = 'Bot/Detector/NSFW/model/vocabulary.json'
word2id_ = None

with open(VOCABULARY_PATH, 'r', encoding='utf-8') as f:
    word2id_ = json.load(f)
    
FREQUENCIES_PATH = 'Bot/Detector/NSFW/model/frequencies.txt'
word2freq_ = np.loadtxt(FREQUENCIES_PATH)
'''

with open('Bot/Detector/NSFW/model/vocabulary.pkl', 'rb') as handle:
    word2id_ = pickle.load(handle)

MODEL_PATH = 'Bot/Detector/NSFW/model/current_best_model_macro85'
model = torch.load(MODEL_PATH, map_location='cpu')
model.eval()

FREQUENCIES_PATH = 'Bot/Detector/NSFW/model/frequencies_hard_model.txt'
word2freq_ = np.loadtxt(FREQUENCIES_PATH)


class Tokenizer:
    def __init__(self, ):
        self.TOKEN_RE = None

    def set_regex(self, regex_condition: str) -> None:
        self.TOKEN_RE = re.compile(regex_condition)
        return self

    def tokenize_document(self, document: str, min_token_size: int = 3) -> []:
        if self.TOKEN_RE is not None:
            tokens = self.TOKEN_RE.findall(document.lower())
            return [token for token in tokens if len(token) >= min_token_size]

    def tokenize_corpus(self, documents: []) -> []:
        return [self.tokenize_document(document) for document in documents]


def vectorize_documents(tokenized_documents,
                        word2id,
                        word2freq,
                        mode='tfidf',
                        scale=True):
    assert mode in {'tfidf', 'idf', 'tf', 'bin'}
    matrix = scipy.sparse.dok_matrix((len(tokenized_documents), len(word2id)), dtype='float32')
    for document_id, document in enumerate(tokenized_documents):
        for token in document:
            if token in word2id:
                matrix[document_id, word2id[token]] += 1

    if mode == 'bin':
        matrix = (matrix > 0).astype('float32')
    elif mode == 'tf':
        matrix = matrix.tocsr()
        matrix = matrix.multiply(1 / matrix.sum(1))
    elif mode == 'idf':
        matrix = (matrix > 0).astype('float32').multiply(1 / word2freq)
    elif mode == 'tfidf':
        matrix = matrix.tocsr()
        matrix = matrix.multiply(1 / matrix.sum(1))
        matrix = matrix.multiply(1 / word2freq)
    if scale:
        matrix = matrix.tocsc()
        matrix -= matrix.min()
        matrix /= (matrix.max() + 1e-6)
    return matrix.tocsr()


def sigmoid(x):
    x = torch.Tensor(x)
    return torch.ones_like(x)/(torch.ones_like(x) + torch.exp(-x))


def check_message_to_nsfw(message: str) -> bool:
    tokenized_message = Tokenizer().set_regex(r'[\w\d]+').tokenize_document(message)
    test_vector = vectorize_documents([tokenized_message], word2id_, word2freq_, scale=True)
    print(sigmoid(model.forward(torch.from_numpy(test_vector.toarray()).float())), test_vector.toarray())
    return sigmoid(model.forward(torch.from_numpy(test_vector.toarray()).float())) < 0.5
