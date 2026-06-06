import requests

response = requests.get('https://query2.finance.yahoo.com/v1/finance/search', params={
    'q': 'apple',
    'quotesCount': 20,
    'newsCount': 0,
    'region': 'US',
    'lang': 'en-US'
})
print('Status:', response.status_code)
print('Text:', response.text[:500])