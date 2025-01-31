import requests
from bs4 import BeautifulSoup
import sqlite3
import boto3
import csv
import os

# URL of the website to scrape
url = 'https://www.cricinfo.com'

# Send a GET request to the website
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.content, 'html.parser')

# Find all headlines on the page
headlines = soup.find_all('h3')

# Print the headlines
for headline in headlines:
    print(headline.get_text())
    print(headline.text)

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('headlines.db')
    cursor = conn.cursor()

    # Create a table to store the headlines
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS headlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headline TEXT NOT NULL
    )
    ''')

    # Insert the headlines into the table
    for headline in headlines:
        cursor.execute('INSERT INTO headlines (headline) VALUES (?)', (headline.get_text(),))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print ("reading headlines from sqlite db")
    # Connect to SQLite database
    conn = sqlite3.connect('headlines.db')
    cursor = conn.cursor()

    # Read the headlines from the table
    cursor.execute('SELECT * FROM headlines')
    rows = cursor.fetchall()

    # Print the headlines
    for row in rows:
        print(row[1])

    # Close the connection
    conn.close()

    # AWS S3 configuration
    s3_bucket = 'dv-scraping-bucket'
    s3_file_name = 'headlines.csv'

    # Create a CSV file with the headlines
    csv_file = 'headlines.csv'
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Headline'])
        for row in rows:
            writer.writerow(row)

    # Upload the CSV file to S3
    s3 = boto3.client('s3')
    s3.upload_file(csv_file, s3_bucket, s3_file_name)

    # Remove the local CSV file
    os.remove(csv_file)

   