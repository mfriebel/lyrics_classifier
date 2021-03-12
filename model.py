
"""
Creates model for artist prediction 
"""
# Import statements
from numpy import empty
from extract_lyrics import get_labels_lyrics_lists, lyrics_all_preprocess
from get_lyrics import download_lyrics_html

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import cross_val_score, train_test_split
from wordcloud import WordCloud
from pyfiglet import Figlet

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import pickle
import os
import re


PATH = './artists/'

def vectorized_tfidf_df(corpus, labels, **kwargs):
    vc = TfidfVectorizer(**kwargs)
    vc_matrix = vc.fit_transform(corpus)
    df = pd.DataFrame(vc_matrix.todense(), index=labels, columns=vc.get_feature_names())
    return df

def vectorized_cv_df(corpus, labels, **kwargs):
    vc = CountVectorizer(**kwargs)
    vc_matrix = vc.fit_transform(corpus)
    df = pd.DataFrame(vc_matrix.todense(), index=labels, columns=vc.get_feature_names())
    return df


def generate_wordcloud(data, title):
    wc = WordCloud(width=400, height=330, max_words=100, colormap='Dark2').generate_from_frequencies(data)
    plt.figure(figsize=(10,8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.show()

def show_most_common_words(df):
    artists_common_words = df.groupby(df.index).sum()
    artists_common_words_tp = artists_common_words.transpose()

    for index, artist in enumerate(artists_common_words_tp):
        generate_wordcloud(artists_common_words_tp[artist].sort_values(ascending=False), artist)

def train_mnb(X, y, **kwargs):
    """
    This function transforms the text corpus with a TfidfVectorizer
    and trains a Naive Bayes model.
    
    Parameter
    ---------
    corpus : array_like
        List of song lyrics as strings.

    artists : array_like
        List of labels/artists as strings.

    **kwargs :  Arbitrary keyword arguments passes as hyperparameters for MultinominalNB.

    Returns
    -------
    A pipeline with Text-Preprocesser and the trained sklearn.naives_bayes.MultinominalNB classification model. 
    """
    tf = TfidfVectorizer()
    m = MultinomialNB(**kwargs)
    pipeline = make_pipeline(tf, m)
    pipeline.fit(X, y)
    print(f"\ntraining accuracy: {round(pipeline.score(X, y),3)}")
    cross_val = cross_val_score(pipeline, X, y, cv=5)
    print(f'\ncross-validation accuracy: {cross_val.round(3)}')
    return pipeline

def get_artists():
    banner = Figlet()
    print(banner.renderText('TRAIN NLP MODEL'))
    artists = []
    print('Please enter the artists to train your model with\n')
    artist = 'start value'
    while artist:
        artist = input(f'Please enter the artist: ')
        artist = re.sub('[\s]', '-', artist).lower()
        if (artist not in os.listdir(PATH)) and (artist):
            print(f'\nSongs of artist({artist}) need to be downloaded first')
            if input('\nDo you want to proceed with downloading? ["y/n"]: ') == 'y':
                download_lyrics_html(artist)
                artists.append(artist)
            else:
                print(f'\nArtist({artist}) will be exclude from model\n') 
        elif artist:
            artists.append(artist)
        else:
            None
    return artists

# TODO: Account for class imbalances

if __name__ == "__main__":
    artists = get_artists()
    labels, corpus = get_labels_lyrics_lists(artists)
    corpus_pre = lyrics_all_preprocess(corpus)
    X_train, X_test, y_train, y_test = train_test_split(corpus_pre, labels, test_size = 0.2, random_state=20)
    model = train_mnb(X_train, y_train, alpha=0.1)
    print(f'\ntest score: {round(model.score(X_test, y_test), 3)}\n')
    model.fit(corpus_pre, labels)
    pickle.dump(model, open('lyrics_model.pickle', 'wb'))
