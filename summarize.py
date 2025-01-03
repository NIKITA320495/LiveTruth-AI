from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from googlesearch import search
import re
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
import torch
from peft import PeftModel
import csv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
# NLTK setup
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

# Model from Hugging Face hub
base_model = "NousResearch/Llama-2-7b-chat-hf"

#fine-tuned model
fine_tuned_model = "llama-fine-tuned1/pytorch/default/1"

# Set torch dtype and attention implementation
if torch.cuda.get_device_capability()[0] >= 8:
    # !pip install -qqq flash-attn
    torch_dtype = torch.bfloat16
    attn_implementation = "flash_attention_2"
else:
    torch_dtype = torch.float16
    attn_implementation = "eager"

# QLoRA config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch_dtype,
    llm_int8_enable_fp32_cpu_offload=True,
    bnb_4bit_use_double_quant=True,
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map="auto",
    attn_implementation=attn_implementation
    
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Store related summaries in a global variable (temporary solution)
related_summaries_global = []

##FUNCTIONS FOR PIPELINE
def initialise_base_model(base_model_dir):
    bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            llm_int8_enable_fp32_cpu_offload=True,
            bnb_4bit_use_double_quant=True,
    )

    # Load model
    base_model = AutoModelForCausalLM.from_pretrained(
            base_model_dir,
            quantization_config=bnb_config,
            device_map="auto"
        )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_dir)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    base_model = base_model.to(device)
    base_model.eval()

    return tokenizer, base_model, device

def initialise_fine_tuned_model(base_model, adapter_dir):
    model = PeftModel.from_pretrained(base_model, adapter_dir)
        
    # Move Model to Appropriate Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    return model


# PHASE 1 FUNCTIONS
def analyze_news(headline, tokenizer, model, device):
    # Input Prompt
    input_text = (
        "You are a news analyzer. Given the headline, provide a confidence score (0-100) indicating how likely the news is true, "
        "and give a detailed explanation for your assessment. "
        f"Headline: '{headline}'\n"
    )

    # Tokenize Input
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    # Generate Response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=250,   # Limits generated tokens only
            num_beams=5,          # Enhance quality with beam search
            temperature=0.7,      # Balance randomness
            top_k=40,             # Limit to top-k tokens
            top_p=0.9,            # Nucleus sampling
            repetition_penalty=1.2  # Reduce repetitive outputs
        )
    
    # Decode and Post-process
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()


# PHASE 2 FUNCTIONS
def scrape_important_content(url):
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
        for p in paragraphs[:8]:  # Limit paragraphs to avoid too much text
            content += p.get_text(strip=True) + " "
        
        return content.strip() if content else "No significant content found."
    except Exception as e:
        return f"Error: {e}"
        
def process_query(query, filename):
    # Step 1: Extract keywords from the query
    words = word_tokenize(query)
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in words if word.isalpha() and word.lower() not in stop_words]

    # Step 2: Perform Google search using extracted keywords
    search_query = " ".join(keywords)
    search_results = [url for url in search(search_query, num_results=10)]

    # Step 3: Scrape content from search results
    scraped_data = []
    for url in search_results:
        content = scrape_important_content(url)
        scraped_data.append([url, content])

    # Step 4: Save scraped data to a CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Important Content"])
        writer.writerows(scraped_data)
    return scraped_data

def generate_summary_with_llama(file_path,tokenizer,model,device):

    df = pd.read_csv(file_path)
    col = df['Important Content'].tolist()
    corpus = [i for i in col if i not in ("No significant content found.","Failed to fetch content")]
    
    combined_corpus = "\n".join(corpus)[:4000]  # Limit the input to avoid exceeding model input size

    input_text = (
        f"You are a news summarization expert. analyse the data scrapped from web which is: [{combined_corpus}] and provide an overall summary in maximum 100 words.\n"
    )

    # Tokenize input
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,   # Limit generated tokens
            num_beams=5,          # Enhance quality with beam search
            temperature=0.7,      # Balance randomness
            top_k=40,             # Limit to top-k tokens
            top_p=0.9,            # Nucleus sampling
            repetition_penalty=1.2  # Reduce repetitive outputs
        )

    # Decode and post-process
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()

def combinedPipeline(txt):
    adapter_dir = "llama-fine-tuned1/pytorch/default/1"
    base_model_dir = "NousResearch/Llama-2-7b-chat-hf" 
    # Initialize Model
    tokenizer, base_model, device = initialise_base_model(base_model_dir)
    fine_tuned_model = initialise_fine_tuned_model(base_model, adapter_dir)
    
    # PHASE 1
    headline = txt
    fine_tune_response = analyze_news(headline, tokenizer, fine_tuned_model, device)
    
    #phase 2
    filename = "web_content_summary.csv"
    # print("scrapping web")
    scraped_data = process_query(txt, filename)   

    # print("\nReading scraped content from CSV and Generating summary using Llama model...")
    filepath = filename
    news_summary = generate_summary_with_llama(filepath,tokenizer,base_model,device)
    start_index = news_summary.find("provide an overall summary in maximum 100 words."
    )
    if start_index != -1:
        news_summary = news_summary[start_index:]
    # print(news_summary)
        
    return fine_tune_response, news_summary    
    

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
        headline = article_text
        base_model_dir = "NousResearch/Llama-2-7b-chat-hf" 
        tokenizer, base_model, device = initialise_base_model(base_model_dir)
        fine_tune_response, news_summary = combinedPipeline(headline)
        input_text = (
        f"You are a news analyser. under the result from a fine tuned LLM which is [{fine_tune_response}] and the data scrapped from web which is: [{news_summary}] and provide an overall resultt that whether the news is true and false and a confidence score to it for the headline [{headline}].\n")

        # Tokenize input
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
        )
        inputs = {key: value.to(device) for key, value in inputs.items()}

        # Generate response
        with torch.no_grad():
            outputs = base_model.generate(
                **inputs,
                max_new_tokens=512,   # Limit generated tokens
                num_beams=5,          # Enhance quality with beam search
                temperature=0.7,      # Balance randomness
                top_k=40,             # Limit to top-k tokens
                top_p=0.9,            # Nucleus sampling
                repetition_penalty=1.2  # Reduce repetitive outputs
            )

        # Decode and post-process
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
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
                # Base model setup
                base_model_dir = "NousResearch/Llama-2-7b-chat-hf"  # Update with your model directory
                tokenizer, base_model, device = initialise_base_model(base_model_dir)

                input_text = (
                    f"Summarize this: {content} in 50 words and verify accuracy of news in percentage {main_summary} based on this.\n"
                )

                # Tokenize input
                inputs = tokenizer(
                    input_text,
                    return_tensors="pt",
                    truncation=True,
                    padding="max_length"
                )
                inputs = {key: value.to(device) for key, value in inputs.items()}

                # Generate response
                with torch.no_grad():
                    outputs = base_model.generate(
                        **inputs,
                        max_new_tokens=512,   # Limit generated tokens
                        num_beams=5,          # Enhance quality with beam search
                        temperature=0.7,      # Balance randomness
                        top_k=40,             # Limit to top-k tokens
                        top_p=0.9,            # Nucleus sampling
                        repetition_penalty=1.2  # Reduce repetitive outputs
                    )

                # Decode and post-process
                response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                summary = response or "No summary generated."
                related_summaries.append({'URL': result_url, 'Summary': summary})
            except Exception as e:
                print(f"Error during related summarization: {e}")
                related_summaries.append({'URL': result_url, 'Summary': "Error during summarization."})

        # Save summaries globally
        related_summaries_global = related_summaries

        return jsonify({
            "main_summary": main_summary,
            "related_summaries": related_summaries
        })

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
