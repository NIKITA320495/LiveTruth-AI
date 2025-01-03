# LiveTruth: Real-Time Misinformation Detection System

LiveTruth is an AI-powered solution designed to combat the spread of misinformation during live broadcasts. By leveraging advanced AI models, real-time data integration, and multi-source fact-checking, LiveTruth ensures the credibility of news content, empowering users to make informed decisions.

## **Index**

1. [Overview](#overview)
2. [Key Features](#key-features) 
3. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
4. [File Structure](#file-structure)  
5. [Usage](#usage)  
6. [Contributing](#contributing)  
7. [License](#license)  
8. [Contact](#contact)  

---


## **Key-Features**

1. **AI-Powered News Analysis**  
   - Processes news articles using a fine-tuned local Large Language Model (LLM), LLaMA, trained on 100,000+ news articles.  
2. **Multi-Source Fact-Checking**  
   - Incorporates Google Search API to fetch articles from 6-7 trusted sources for validation.  
3. **Confidence Scoring System**  
   - Generates confidence scores by comparing LLaMA model outputs with verified articles and GPS-based SMS feedback.  
4. **Ground-Truth Verification**  
   - Uses GPS-based SMS verification to confirm or refute news from local sources.  
5. **Interactive Dashboard**  
   - Displays real-time, comprehensive credibility assessments with source-wise confidence scores.

---

### **Prerequisites**

Before running LiveTruth, ensure the following steps are completed to set up APIs and models:

1. **Set Up an API on Hugging Face**  
   - Create an account on [Hugging Face](https://huggingface.co/).  
   - Generate an API key from your Hugging Face account settings.  
   - Add the API key to the `.env` file:  
     ```env
     HF_TOKEN=your_huggingface_api_key
     ```

2. **Download Meta's LLaMA 2 Model**  
   - Apply for access to the LLaMA 2 model on [Meta AI's website](https://ai.meta.com/llama/).  
   - Download the model and place it in the `models/` directory of the project.  
   - Ensure the directory structure is as follows:  
     ```
     LiveTruth/
     ├── src/
     │   ├── models/
     │   │   └── llama2/
     │   │       └── model_files_here
     ```

3. **Set Up a Twilio API**  
   - Create an account on [Twilio](https://www.twilio.com/).  
   - Verify your phone number and set up a new messaging service.  
   - Generate an API key and SID from the Twilio console.  
   - Add the credentials to the `.env` file:  
     ```env
     TWILIO_ACCOUNT_SID=your_account_sid
     TWILIO_AUTH_TOKEN=your_auth_token
     ```

4. **Create a News API**  
   - Sign up for an API key at [News API](https://newsapi.org/).  
   - Use the API to fetch articles on specific topics.  
   - Add the API key to the `.env` file:  
     ```env
     NEWS_API_KEY=your_news_api_key
     ```

5. **Install Required Dependencies**  
   - Ensure all Python dependencies are installed:  
     ```bash
     pip install -r requirements.txt
     ```


## **How It Works**

1. **News Input**  
   - A news article is submitted for analysis.

2. **Initial Processing**  
   - The LLaMA model processes the article, generating an initial authenticity assessment.

3. **Fact-Checking Integration**  
   - The Google Search API retrieves articles on the same topic from trusted sources.
   - Summarized fetched articles are compared with the LLaMA model's output for validation.

4. **Confidence Score Calculation**  
   - Confidence scores are generated based on alignment and discrepancies between the LLaMA output and fetched articles.

5. **Ground-Truth Verification**  
   - GPS-based SMS verification collects local feedback to further refine the confidence score.

6. **Dashboard Presentation**  
   - Confidence scores from all layers (LLaMA, Google Search API, and GPS verification) are aggregated and presented on an interactive dashboard for real-time assessment.

---

## **Technology Stack**

- **AI Model**: Fine-tuned LLaMA model  
- **Fact-Checking APIs**: Google Search API for trusted source integration  
- **Verification**: GPS-based SMS for ground-truth validation  
- **Dashboard**: Interactive interface for credibility visualization  

---

## **Setup Instructions**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/LiveTruth.git
   cd LiveTruth

