from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd
import heapq

STOP_WORDS = pd.read_csv('stopwords.txt', header=None)
STOP_WORDS = STOP_WORDS[0].values.tolist()


def nltk_summarizer(raw_text):
    word_frequencies = {}
    for word in word_tokenize(str(raw_text)):
        if word not in STOP_WORDS:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)

    sentence_list = sent_tokenize(str(raw_text))
    sentence_scores = {}
    for sent in sentence_list:
        for word in word_tokenize(sent):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    select_length = int(len(sentence_list) * 0.4)
    summary_sentences = heapq.nlargest(select_length, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    return summary
