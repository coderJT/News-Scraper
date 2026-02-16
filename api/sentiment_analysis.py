import nltk
import asyncio
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure necessary data is downloaded to a writable location
def setup_nltk():
    nltk_data_path = "/tmp/nltk_data"
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.append(nltk_data_path)
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', download_dir=nltk_data_path)
    try:
        nltk.data.find('tokenizers/punkt.zip')
    except LookupError:
        nltk.download('punkt', download_dir=nltk_data_path)

setup_nltk()
sid = SentimentIntensityAnalyzer()

async def classify(data):
    sentiment_scores = sid.polarity_scores(data)
    
    return [{'label': 'POSITIVE' if sentiment_scores['compound'] >= 0 else 'NEGATIVE',
             'score': sentiment_scores['compound']}]

async def analyse_sentiment(data):
    if not data.get('content'):
        return {
            'weighted_sum': 0,
            'overall_sentiment': 'NEUTRAL'
        }
        
    paragraphs = [classify(sentence)
                  for sentence in data['content'].split(". ")]
    
    sentiment_result = await asyncio.gather(*paragraphs)
    sentiment_flattened = [sentiment for sentiment_list in sentiment_result
                                    for sentiment in sentiment_list]
    
    labels = [sentiment['label'] for sentiment in sentiment_flattened]
    scores = [sentiment['score'] for sentiment in sentiment_flattened]

    weighted_sum = sum(scores)

    overall_sentiment = ''
    if weighted_sum == 0:
        overall_sentiment = 'NEUTRAL'
    elif weighted_sum > 0:
        overall_sentiment = 'POSITIVE'
    else:
        overall_sentiment = 'NEGATIVE'

    return {
        'weighted_sum': weighted_sum,
        'overall_sentiment': overall_sentiment
    }
