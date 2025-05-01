# sentiment_analyzer.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Analyze Sentiment of a given text
def analyze_sentiment(text):
    sentiment_scores = analyzer.polarity_scores(text)
    sentiment = {
        "positive": sentiment_scores['pos'],
        "neutral": sentiment_scores['neu'],
        "negative": sentiment_scores['neg'],
        "compound": sentiment_scores['compound']
    }
    return sentiment
