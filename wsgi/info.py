from __future__ import division
from math import log, exp, e
from operator import mul
from collections import Counter
import os
import pickle
import logging

pos = {}
neg = {}
features = set()
totals = [0, 0]
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())

# CDATA_FILE = "countdata.pickle"
#FDATA_FILE = "reduceddata.pickle"
FDATA_FILE = "objs.pickle"


def negate_sequence(text):
    """
    Detects negations and transforms negated words into "not_" form.
    """
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    prev = None
    pprev = None
    for word in words:
        # stripped = word.strip(delchars)
        stripped = word.strip(delims).lower()
        negated = "not_" + stripped if negation else stripped
        result.append(negated)
        if prev:
            bigram = prev + " " + negated
            result.append(bigram)
            if pprev:
                trigram = pprev + " " + bigram
                result.append(trigram)
            pprev = prev
        prev = negated

        if any(neg in word for neg in ["not", "n't", "no"]):
            negation = not negation

        if any(c in word for c in delims):
            negation = False

    return result

def classify2(text):
    """
    For classification from pretrained data
    """
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): return True, 0
    # Probability that word occurs in pos documents
    pos_prob = sum(log((get_value_from_dict(pos, word) + 1) / (2 * totals[0])) for word in words)
    neg_prob = sum(log((get_value_from_dict(neg, word) + 1) / (2 * totals[1])) for word in words)
    return (pos_prob > neg_prob, abs(pos_prob - neg_prob))

def get_value_from_dict(dictionary, key):
    if key in dictionary:
        value = dictionary[key]
    else:
        value = 0
    return value

def classify_demo(text):
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): 
        print "No features to compare on"
        return True

    pprob, nprob = 0, 0
    for word in words:
        pp = log((pos[word] + 1) / (2 * totals[0]))
        np = log((neg[word] + 1) / (2 * totals[1]))
        print "%15s %.9f %.9f" % (word, exp(pp), exp(np))
        pprob += pp
        nprob += np

    print ("Positive" if pprob > nprob else "Negative"), "log-diff = %.9f" % abs(pprob - nprob)

def feature_selection_trials():
    """
    Select top k features. Vary k and plot data
    """
    global pos, neg, totals, features
    retrain = False
    if not retrain and os.path.isfile(os.path.join(os.path.dirname(__file__),FDATA_FILE)):
        pos, neg, totals = pickle.load(open(os.path.join(os.path.dirname(__file__),FDATA_FILE), "rb"))
        return

def percentage_confidence(conf):
    return 100.0 * e ** conf / (1 + e**conf)

def get_sentiment_info(text):
    flag, confidence = classify2(text)
    if confidence > 0.5:
        sentiment = "positive" if flag else "negative"
    else:
        sentiment = "neutral"
    conf = "%.4f" % percentage_confidence(confidence) 
    return (sentiment, conf)

if __name__ == '__main__':
    feature_selection_trials()

def setup():
    feature_selection_trials()