import streamlit as st
from PIL import Image
import easyocr
from youtube_transcript_api import YouTubeTranscriptApi as yta
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from googlesearch import search
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import google.generativeai as genai

genai.configure(api_key=key) #the key has been hidden due to privancy reasons
model = genai.GenerativeModel("gemini-1.5-flash")

# NLTK setup
# nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

def extract_text_from_image(image):
    """Extract text from the given image using EasyOCR."""
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader
    image_np = np.array(image)  # Convert PIL image to NumPy array
    results = reader.readtext(image_np)
    
    # Combine text from all detected regions
    extracted_text = "\n".join([result[1] for result in results])
    return extracted_text

def extract_keywords(query):
    """
    Extract significant keywords from the query using NLTK.
    """
    words = word_tokenize(query)
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in words if word.isalpha() and word.lower() not in stop_words]
    return keywords

def perform_search(keywords):
    """
    Perform a Google search and return the URLs.
    """
    search_query = " ".join(keywords)
    print(f"Searching for: {search_query}\n")
    
    results = []
    for j in search(search_query, num_results=10):
        results.append(j)
    return results

def scrape_important_content(url):
    """
    Scrape the important content (like headings and paragraphs) from the given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return "Failed to fetch content"
        
        # Parse the webpage content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract the main headings and paragraphs
        headings = soup.find_all(['h1', 'h2', 'h3'])  # Extract headings
        paragraphs = soup.find_all('p')  # Extract paragraphs
        
        # Combine content
        content = ""
        for h in headings:
            content += h.get_text(strip=True) + " | "
        for p in paragraphs[:8]:  # Limit paragraphs to 5 to avoid too much text
            content += p.get_text(strip=True) + " "
        
        return content.strip() if content else "No significant content found."
    except Exception as e:
        return f"Error: {e}"

def save_to_csv(data, filename):
    """
    Save the scraped data to a CSV file.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Important Content"])
        for row in data:
            writer.writerow(row)

def read_csv(file_path):
    """
    Read the content from the CSV file.
    """
    df = pd.read_csv(file_path)
    col = df['Important Content'].tolist()
    data = [i for i in col if i not in ("No significant content found.","Failed to fetch content")]
    return data

def get_overall_summary(corpus):
    """
    Use MetaAI API to summarize the corpus into a single paragraph.
    """
    # ai = MetaAI()
    # combined_corpus = "\n".join(corpus)  # Combine all the content
    print("Sending content to gemini API for summarization...\n")
    
    response = model.generate_content(f"Tell whether the news: {corpus} is fake or not and why")
    print(response.text)
    return response.text
    # response = ai.prompt(message=f"Tell whether the news: {corpus} is fake or not and why.")
    # response = ai.prompt(message = "what is the weather in delhi right now")
    

def fixed(file_path, headline, output_file="table.csv"):
    
    df = pd.read_csv(file_path)

    # Create a list to store results
    results = []

    for index, row in df.iterrows():
        url = row['URL']
        content = row['Important Content']

        if content not in ("No significant content found.", "Failed to fetch content"):
            print(f"Processing URL: {url}")
            print("Sending content to gemini API for fixing...\n")
            # response = ai.prompt(message=f"In accordance to the headline: {headline}, frame 1 line that contains all the relevant information to the headline from the text: {content}.")
            response = model.generate_content(f"In accordance to the headline: {headline}, frame 1 line that contains all the relevant information to the headline from the text: {content}.")
            # Append the result as a dictionary
            results.append({'URL': url, 'Response': response.text})

    # Create a new DataFrame from the results
    output_df = pd.DataFrame(results)

    # Save the results to a new CSV file
    output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    return output_df

def get_video_id(url):
    video_id_pattern = r"(?<=v=)[^#\&\?]*"
    match = re.search(video_id_pattern, url)
    return match.group(0) if match else None

# Function to fetch transcript from YouTube video ID
def get_transcript(video_id):
    try:
        try:
            data = yta.get_transcript(video_id, languages=['en'])
        except:
            data = yta.get_transcript(video_id, languages=['hi'])
        
        transcript = ' '.join([entry['text'] for entry in data])
        return transcript
    except Exception as e:
        return f"Error fetching transcript: {e}"
    

st.sidebar.title("Fact Checking System")
option = st.sidebar.selectbox("Select an option", ["Image checker", "Text Checker", "Video checker"])

if option =="Image checker":
    st.title("Fake News Detection from Image")
    st.write("Upload any image with a news headline or content to analyze its authenticity")

    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Open the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        st.write("Processing the image...")
        
        # Extract text from the image
        extracted_text = extract_text_from_image(image)

        if extracted_text.strip():
            st.subheader("Extracted Text:")
            st.write( extracted_text)

            # Extract keywords and search
            # extracted_text = "STUDENTS HAVING LESS THAN 75% ATTENDANCE WILL NOW PAY 28% ADDITIONAL GST ON THEIR EMESTER FEES: 3oe"
            keywords = extract_keywords(extracted_text)
            print(f"Extracted Keywords: {keywords}")
            search_results = perform_search(keywords)
            
            # Scrape content for each URL
            scraped_data = []
            print("\nScraping content from search results...")
            for idx, url in enumerate(search_results, 1):
                print(f"Scraping [{idx}]: {url}")
                content = scrape_important_content(url)
                scraped_data.append([url, content])
            
            # Save data to CSV
            filename = "web_content_summary.csv"
            save_to_csv(scraped_data, filename)
            print(f"\nData saved to '{filename}'")

            # Read the saved data
            corpus = read_csv(filename)
    
            # Step 2: Get the overall summary using MetaAI API
            if corpus:
                summary = get_overall_summary(extracted_text)
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.write("No relevant content found in the search results!")
            
            # Generate the table for detailed responses
            tab = fixed(filename, extracted_text)
            st.subheader("Detailed Responses:")
            st.table(tab)
        else:
            st.write("No text found in the image.")

elif option == "Text Checker":
    st.title("Fake News Detection from text")
    st.write("Enter a news headline or content to analyze its authenticity.")

    # User input for text
    user_text = st.text_area("Enter the news content or headline:")

    if st.button("Analyze"):
        if user_text.strip():
            st.write("Processing your input...")

            # Extract keywords and search
            keywords = extract_keywords(user_text)
            print(f"Extracted Keywords: {keywords}")
            search_results = perform_search(keywords)
            
            # Scrape content for each URL
            scraped_data = []
            print("\nScraping content from search results...")
            for idx, url in enumerate(search_results, 1):
                print(f"Scraping [{idx}]: {url}")
                content = scrape_important_content(url)
                scraped_data.append([url, content])
            
            # Save data to CSV
            filename = "web_content_summary.csv"
            save_to_csv(scraped_data, filename)
            print(f"\nData saved to '{filename}'")

            # Read the saved data
            corpus = read_csv(filename)
    
            # Step 2: Get the overall summary using MetaAI API
            if corpus:
                summary = get_overall_summary(user_text)
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.write("No relevant content found in the search results!")
            
            # Generate the table for detailed responses
            tab = fixed(filename, user_text)
            st.subheader("Detailed Responses:")
            st.table(tab)

        else:
            st.write("Please enter some text to analyze.")

elif option == "Video checker":
    st.title("YouTube Video Fake News Detection")
    st.write("Enter the YouTube link of the video to analyze its authenticity.")

    # User input for YouTube link
    youtube_url = st.text_input("Enter YouTube video URL:")

    if st.button("Analyze Video"):
        if youtube_url.strip():
            # Extract video ID from the YouTube URL
            video_id = get_video_id(youtube_url)
            if video_id:
                # Fetch the transcript of the video
                transcript = get_transcript(video_id)
                # Extract keywords from transcript and search online
                keywords = extract_keywords(transcript)
                search_results = perform_search(keywords)
                
                # Scrape content from search results
                scraped_data = []
                for idx, url in enumerate(search_results, 1):
                    content = scrape_important_content(url)
                    scraped_data.append([url, content])

                # Save data to CSV and display results
                filename = "web_content_summary.csv"
                save_to_csv(scraped_data, filename)
                corpus = read_csv(filename)
                if corpus:
                    summary = get_overall_summary(transcript)
                    st.subheader("Summary:")
                    st.write(summary)
                
                # Generate and display the table for detailed responses
                headline = transcript.split('.')[0]  # A simple heuristic to generate headline from the transcript
                table = fixed(filename, headline)
                st.subheader("Detailed Responses:")
                st.table(table)
            else:
                st.write("Invalid YouTube URL.")
        else:
            st.write("Please enter a YouTube URL.")



