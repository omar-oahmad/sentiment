from mastodon import Mastodon
import sqlite3
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

mastodon = Mastodon(
    access_token="gT9H9Q6JexEx0FtGgt53tWBQR60Z3RqvZmQAYf2qJm4",
    api_base_url="https://mastodon.social"

)

with open ('terms.json', 'r') as file:
    data = json.load(file)
    search_terms = data['terms']

conn = sqlite3.connect("sentiment.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
               SID INTEGER PRIMARY KEY AUTOINCREMENT,
               Product TEXT,
               User TEXT,
               Date TEXT,
               Message TEXT,
               Sentiment TEXT
)
               
''')
conn.commit()

def clean_message(message):
    soup = BeautifulSoup(message, 'html.parser')
    text = soup.get_text()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


for term in search_terms:
    print (f"Searching for {term}")
    results = mastodon.timeline_hashtag(term, limit=50)

    if not results:
        print(f"No results found for {term}")
        continue

    for status in results:
        user = status['account']['username']
        date = status["created_at"]
        raw_message = status['content']
        message = clean_message(raw_message)

        if not message:
            print("Empty message, skipping...")
            continue        

        cursor.execute('''
        INSERT INTO data (Product, User, Date, Message, Sentiment)
        VALUES (?, ?, ?, ?, ?)
        ''', (term, user, date, message, None))
conn.commit()