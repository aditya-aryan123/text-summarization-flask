from urllib.request import urlopen

from summarizer import nltk_summarizer
import string
import re
import streamlit as st
from bs4 import BeautifulSoup
from spacy import displacy

from spacy.lang.hi import Hindi
from spacy.lang.en import English
nlp_hindi = Hindi()
nlp_english = English()


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


def get_text(raw_url):
    page = urlopen(raw_url)
    soup = BeautifulSoup(page)
    fetched_text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
    return fetched_text


def analyze_text_english(text):
    return nlp_english(text)


def analyze_text_hindi(text):
    return nlp_hindi(text)


def main():
    st.title("Text Summarizer")

    raw_url = st.text_area("Enter URL Here", "Paste Here")
    if st.button("Analyze"):
        result = get_text(raw_url)
        result = clean_domain(result)
        result = cleanhtml(result)
        result = cleaning_picURL(result)
        result = remove_xml_tags(result)
        result = remove_emojis(result)
        result = strip_all_entities(result)
        result = clean_text_summary(result)
        len_of_full_text = len(result)
        len_of_short_text = round(len(result) * 0.4)
        st.success("Length of Full Text::{}".format(len_of_full_text))
        st.success("Length of Short Text::{}".format(len_of_short_text))
        summarized_docx = nltk_summarizer(result)
        docx_hindi = analyze_text_hindi(summarized_docx)
        html_hi = displacy.render(docx_hindi, style="ent")
        st.write(HTML_WRAPPER.format(html_hi), unsafe_allow_html=True)

    raw_text = st.text_area("Enter Text Here", "Type Here")
    if st.button("Summarize"):
        raw_text = clean_domain(raw_text)
        raw_text = cleanhtml(raw_text)
        raw_text = cleaning_picURL(raw_text)
        raw_text = remove_xml_tags(raw_text)
        raw_text = remove_emojis(raw_text)
        raw_text = strip_all_entities(raw_text)
        len_of_full_text = len(raw_text)
        len_of_short_text = round(len(raw_text) * 0.4)
        st.success("Length of Full Text::{}".format(len_of_full_text))
        st.success("Length of Short Text::{}".format(len_of_short_text))
        summary_result = nltk_summarizer(raw_text)
        docx_hindi = analyze_text_hindi(summary_result)
        html_hi = displacy.render(docx_hindi, style="ent")
        st.write(HTML_WRAPPER.format(html_hi), unsafe_allow_html=True)


if __name__ == '__main__':
    main()
