from flask import Flask, render_template, request
import re
import string
import summarizer

from spacy.lang.hi import Hindi
nlp_hindi = Hindi()

app = Flask(__name__)

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div> """


def clean_domain(corpus):
    corpus = re.sub(r'[\S]+\.(net|com|org|info|edu|gov|uk|de|ca|jp|fr|au|us|ru|ch|it|nel|se|no|es|mil)[\S]*\s?', '',
                    corpus)
    return corpus


CLEANR = re.compile('''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([
^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def cleaning_picURL(text):
    text = re.sub(r'pic.twitter.com/[\w]*', "", text)
    return text


def remove_xml_tags(corpus):
    corpus = re.sub('<.*?>', ' ', corpus)
    return corpus


def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


string = string.punctuation.replace('.', '').replace('|', '')


def strip_all_entities(text):
    entity_prefixes = ['@', '#']
    for separator in string:
        if separator not in entity_prefixes:
            text = text.replace(separator, ' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)


def clean_text_summary(corpus):
    # corpus = corpus.lower()
    corpus = corpus.replace('\n', '')
    corpus = corpus.replace("\'", '')
    corpus = corpus.replace('।', '.')
    corpus = corpus.replace('|', '.')
    corpus = corpus.replace('\t', '')
    corpus = corpus.replace('—', '')
    corpus = corpus.replace('-', '')
    corpus = corpus.replace('\xa0', '')  # remove special encoding
    corpus = corpus.replace('\u200d', '')  # remove unicode char
    corpus = corpus.replace('’', '')
    corpus = corpus.replace('‘', '')
    corpus = corpus.replace('(\.\.\.)', '')  # remove . if it occors more than one time consecutively
    corpus = re.sub('\s\s+', ' ', corpus)
    corpus = re.sub('[\w\_]#+', '', corpus)
    corpus = re.sub('#[\w\_]+', '', corpus)
    corpus = re.sub('[\w\_]#[\w\_]+', '', corpus)
    corpus = re.sub('(\+\++)', '', corpus)  # remove + if it occors more than one time consecutively
    corpus = re.sub(r'\[\d+\]', '', corpus)
    corpus = re.sub(r'\[\w+\]', '', corpus)
    corpus = re.sub(r'\(\w+\)', '', corpus)

    return corpus


@app.route("/")
def msg():
    return render_template('index.html')


def analyze_text_hindi(text):
    return nlp_hindi(text)


@app.route("/summarize", methods=['POST', 'GET'])
def get_summary():
    body = request.form['data']
    body = clean_domain(body)
    body = cleanhtml(body)
    body = cleaning_picURL(body)
    body = remove_xml_tags(body)
    body = remove_emojis(body)
    body = clean_text_summary(body)
    body = strip_all_entities(body)
    docx_hindi = analyze_text_hindi(body)
    result = summarizer.nltk_summarizer(docx_hindi)
    return render_template('summary.html', rawtext=body, result=result)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
