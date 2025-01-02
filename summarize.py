from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from meta_ai_api import MetaAI
from flask_cors import CORS
from googlesearch import search
import re

app = Flask(__name__)
CORS(app)

# Store related summaries in a global variable (temporary solution)
related_summaries_global = []

def fetch_article(url):
    """Fetch the article text from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        return article_text.strip() or None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the article: {e}")
        return None

def summarize_text(article_text):
    """Summarize the given text using MetaAI."""
    try:
        ai = MetaAI()
        response = ai.prompt(
            message=f"Summarize {article_text} in a concise and objective manner within 200 words, focusing only on the most critical information."
        )
        return response.get('message', None)
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

def perform_search(keywords):
    """Perform a Google search and return the URLs."""
    search_query = " ".join(keywords)
    print(f"Searching for: {search_query}\n")

    try:
        return list(search(search_query, num_results=10))
    except Exception as e:
        print(f"Error during search: {e}")
        return []

def scrape_important_content(url):
    """Scrape the important content (headings and paragraphs) from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        headings = soup.find_all(['h1', 'h2', 'h3'])
        paragraphs = soup.find_all('p')

        content = " ".join(h.get_text(strip=True) for h in headings) + " "
        content += " ".join(p.get_text(strip=True) for p in paragraphs[:8])

        return content.strip() or "No significant content found."
    except Exception as e:
        print(f"Error during content scraping: {e}")
        return None

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/summarize', methods=['POST'])
def summarize_article():
    """Endpoint to fetch and summarize an article."""
    global related_summaries_global

    data = request.json
    url = data.get('url')
    title = data.get('title', "")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Fetch and summarize the main article
        article_text = fetch_article(url)
        if not article_text:
            return jsonify({"error": "Failed to fetch the article"}), 500

        main_summary = summarize_text(article_text)
        if not main_summary:
            return jsonify({"error": "Failed to generate a summary"}), 500

        # Perform related searches
        related_summaries = []
        search_results = perform_search([title]) if title else []

        for result_url in search_results:
            content = scrape_important_content(result_url)
            if not content:
                continue

            try:
                ai = MetaAI()
                response = ai.prompt(
                    message=f"Summarize this: {content} in 50 words and verify accuracy of news in percentage {main_summary} based on this."
                )
                summary = response.get('message', "No summary generated.")
                related_summaries.append({'URL': result_url, 'Summary': summary})
            except Exception as e:
                print(f"Error during related summarization: {e}")
                related_summaries.append({'URL': result_url, 'Summary': "Error during summarization."})

        # Save summaries globally
        related_summaries_global = related_summaries

        return jsonify({
            "main_summary": main_summary,
            "related_summaries": related_summaries})

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/graph_data', methods=['GET'])
@app.route('/graph_data', methods=['GET'])
def graph_data():
    """Endpoint to extract and return accuracy data for visualization."""
    global related_summaries_global

    sample_data = []
    total_accuracy = 0
    count = 0
    print("Related Summaries:", related_summaries_global)
    for i in related_summaries_global:
        # Extract accuracy value from the Summary text
        accuracy_match = re.search(r'Accuracy of news:\s*(\d+)%', i['Summary'])
        if accuracy_match:
            accuracy = int(accuracy_match.group(1))
            sample_data.append({
                "URL": i['URL'],
                "Accuracy": accuracy
            })
            total_accuracy += accuracy
            count += 1

    # Calculate the average accuracy
    average_accuracy = total_accuracy / count if count > 0 else 0

    # Print the resulting sample_data
    print("Sample Data for Graph:", sample_data)
    print("Average Accuracy:", average_accuracy)

    return jsonify({
        "sample_data": sample_data,
        "average_accuracy": average_accuracy
    })


if __name__ == '__main__':
    app.run(debug=True)
