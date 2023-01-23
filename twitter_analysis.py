import requests
from textblob import TextBlob

positive_tweet_ids = []
negative_tweet_ids = []
neutral_tweet_ids = []

def get_sentiment_data(query):
    positive_tweet_ids.clear()
    negative_tweet_ids.clear()
    neutral_tweet_ids.clear()

    bearer_token = 'AAAAAAAAAAAAAAAAAAAAALGrkgEAAAAAUK55c%2BATm9m%2B3WtopZylKlXOleI%3DXQwEKoMQ0EwDUT8I6GjCvXgMOxq7GbECZiJH6zfPK1ujoK7wHG'
    base_url = 'https://api.twitter.com/2/'


    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }

    params = {
        'query': query + " lang:en",
        'max_results': '100',
    }

    response = requests.get(f'{base_url}tweets/search/recent', headers=headers, params=params)

    json_data = response.json()

    cleaned_data = []
    for tweet in json_data['data']:
        parts = tweet['text'].split(' ')
        cleaned_tweet = ' '.join(parts[2:])
        cleaned_data.append({'id': tweet['id'], 'text': cleaned_tweet})

    sentiment_data = []

    for tweet in cleaned_data:
        sentiment = TextBlob(tweet['text']).sentiment.polarity
        if sentiment > 0:
            sentiment_data.append('positive')
            positive_tweet_ids.append(tweet['id'])
        elif sentiment == 0:
            sentiment_data.append('neutral')
            neutral_tweet_ids.append(tweet['id'])
        else:
            sentiment_data.append('negative')
            negative_tweet_ids.append(tweet['id'])

    return (sentiment_data)
    