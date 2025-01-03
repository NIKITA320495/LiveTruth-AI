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

## **Overview**

LiveTruth is an AI-driven platform addressing the critical issue of misinformation in real-time live broadcasts. Using a combination of AI models, fact-checking APIs, and ground-truth verification, LiveTruth provides an intuitive interface to evaluate the credibility of news content in seconds.

---

## **Key Features**

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

## **Getting Started**

### **Prerequisites**

Before running LiveTruth, ensure the following steps are completed to set up APIs and models:

1. **Set Up an API on Hugging Face**  
   - Create an account on [Hugging Face](https://huggingface.co/).  
   - Generate an API key from your Hugging Face account settings.  
   - Add the API key to the `.env` file:  
     ```env
     HUGGINGFACE_TOKEN=your_huggingface_api_key
     ```

2. **Download Meta's LLaMA 2 Model**  
   - Apply for access to the LLaMA 2 model on [Meta AI's website](https://ai.meta.com/llama/).  
   - Download the model and place it in the `models/` directory of the project.  

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

### **Installation**

1. **Install Required Dependencies**  
   - Ensure all Python dependencies are installed:  
     ```bash
     pip install -r requirements.txt
     ```

2. **Fine-Tune the LLaMA 2 Model**  
   - Open the Jupyter Notebook at `LiveTruth-AI/Backend Model/fineTuneModelTraining.ipynb`.  
   - Follow the steps to fine-tune the LLaMA 2 model.  

3. **Run the LiveTruth Pipeline**  
   - Execute the notebook `LiveTruth-AI/Backend Model/LiveTruthPipeline.ipynb` to set up the main processing pipeline.  

4. **Run Server**  
   - Navigate to the `LiveTruth-AI/summarize.py` script:  
     [summarize.py](https://github.com/NIKITA320495/LiveTruth-AI/blob/main/summarize.py)  
   - Run the script in the terminal:  
     ```bash
     python summarize.py
     ```

5. **Start**  
   - Open `LiveTruth-AI/templates/index.html` in your web browser to access the LiveTruth dashboard:  
     [index.html](https://github.com/NIKITA320495/LiveTruth-AI/blob/main/templates/index.html)  


## **File Structure**
The file structure of the LiveTruth project is organized as follows:

```plaintext
LiveTruth-AI/
├── Backend Model/                    
│   ├── LiveTruthPipeline.ipynb        # Main Jupyter notebook for setting up the LiveTruth processing pipeline
│   ├── fineTuneModelTraining.ipynb    # Jupyter notebook for fine-tuning the LLaMA 2 model
│   └── gpsSMSverification.ipynb       # Jupyter notebook for GPS-based SMS verification integration
├── Streamlit/                         
│   └── factcheck.py                   # Script for handling fact-checking through the Streamlit interface
├── lib/                               # Contains external libraries or custom utilities for the project
├── mail/                              # Files related to email notifications or messaging functionality
├── scss/                              # Contains SCSS files for the project frontend
├── static/                            # Contains static assets such as CSS, images, and JS
│   ├── css/                           
│   ├── img/                          
│   ├── js/                                          
├── templates/                         # Contains HTML files for different pages of the site
│   ├── index.html                     # Main landing page of the project
│   ├── livenews.html                  # Page displaying live news and updates
├── summaries.csv                      # CSV file containing summaries for processed news data
├── summarize.py                       # Python script for processing and summarizing news data
└── Readme.md                          # Project documentation and setup instructions
     
```


