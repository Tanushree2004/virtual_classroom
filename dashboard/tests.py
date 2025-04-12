from django.test import TestCase

import requests

API_KEY = "AIzaSyDxHMc1TqkwP1U_I1UT06xQj0cIZ2uvko4"
query = "Python Programming"
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=5&key={API_KEY}"

response = requests.get(url).json()
print(response)
