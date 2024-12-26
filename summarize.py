from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from meta_ai_api import MetaAI
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def fetch_article(url):
    """Fetch the article text from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        return article_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the article: {e}")
        return None

def summarize_text(article_text):
    """Summarize the given text using MetaAI."""
    try:
        ai = MetaAI()
        response = ai.prompt(
            message=f"Using the following corpus:\n{article_text}\n\nProvide an overall summary in 200 words."
        )
        return response
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/summarize', methods=['POST'])
def summarize_article():
    """Endpoint to fetch and summarize an article."""
    data = request.json
    url = data.get('url')
    print(url)

    if not url:
        return jsonify({"error": "URL is required"}), 400

    article_text = fetch_article(url)
    if not article_text:
        return jsonify({"error": "Failed to fetch the article"}), 500
    print(article_text)

    summary = summarize_text(article_text)
    summary_message=summary['message']
    print("######################### SUMMARY ############################")
    print(summary['message'])

    return jsonify({"summary": summary_message})
    # Ensure you return the response
  

if __name__ == '__main__':
    app.run(debug=True)
