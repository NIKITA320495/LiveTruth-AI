## <img src="static/img/logo.png" width="20" />  LiveTruth: Real-Time Misinformation Detection System

LiveTruth is an AI-powered solution designed to combat the spread of misinformation during live broadcasts. By leveraging advanced AI models, real-time data integration, and multi-source fact-checking, LiveTruth ensures the credibility of news content, empowering users to make informed decisions.

## **Index**

1. [Overview](#overview)  
2. [Key Features](#key-features)
3. [File Structure](#file-structure)  
4. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
5. [Architecture](#architecture)
6. [User Interaction](#user-interaction)


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
|   ├── trending.html                  # Page displaying trending news and factcheck dashboard
├── summaries.csv                      # CSV file containing summaries for processed news data
├── summarize.py                       # Python script for processing and summarizing news data
└── Readme.md                          
```

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
   - Run the script in the terminal:  
     ```bash
     python summarize.py
     ```

5. **Start**  
   - Open `LiveTruth-AI/templates/index.html` in your web browser to access the LiveTruth news analysis and dashboard.

## **Architecture**

![Architecture Diagram](https://github.com/NIKITA320495/LiveTruth-AI/blob/main/static/img/architecture.png)

## **User Interaction**
### **Trending Page**
![WhatsApp Image 2025-01-03 at 20 32 57_cae7a47c](https://github.com/user-attachments/assets/53025b0d-3a2c-486a-a3f5-0d8dbcb31071)
*The trending page shows the trending news and the analysis and dashboard of the selected news.*

### **Fact Check Page**
#### Fact checking from image
![WhatsApp Image 2025-01-03 at 20 34 32_23e0eeb8](https://github.com/user-attachments/assets/368b84b6-99d0-41a5-824b-13eabd6ccc70)
![WhatsApp Image 2025-01-03 at 20 34 55_93c8aacf](https://github.com/user-attachments/assets/8059b5f8-8869-42f9-86bb-e6d9a508e17c)

#### Fact checking from video
![WhatsApp Image 2025-01-03 at 20 35 57_e532c6af](https://github.com/user-attachments/assets/cb577611-5eb4-4340-a324-15bf3d1a413a)

*The **Fact Check Page** enables users to input content (text, image, or video) for fact-checking. The page leverages a fine-tuned LLaMA model to provide responses based on the input and cross-checks the sources across the web.*

## **Outputs**
<p align="center">
  <img src="https://github.com/user-attachments/assets/50af5f83-5ec8-4fad-bff7-5ee79359f650" alt="Output Image" />
</p>


The **Output** aggregates and displays the results based on multiple analyses and user inputs. 
Here's a breakdown of how the output works:

1. **Accuracy Score from Different Sources**:  
   The system pulls data from various trusted web sources and performs fact-checking using advanced algorithms. Each source provides an **accuracy score**, which is calculated based on how reliable and consistent the information is with other trusted sources.

2. **Average Accuracy**:  
   After gathering accuracy scores from different sources, the system calculates the **average accuracy score**. This provides an overall measure of the credibility of the article being analyzed. The average accuracy score is displayed to the user as a percentage, showing how trustworthy the article is based on the analysis from different sources.

3. **User Responses and Ground Truth**:  
   Users can contribute their own responses to the article's authenticity. These responses are aggregated and analyzed, and a **Ground Truth** is established based on the consensus of user inputs. The system compares the users' responses to the analysis results and adjusts the final output accordingly. The **Ground Truth** score is displayed to users, offering a clear representation of how the community perceives the article's truthfulness.

## **Disclaimer**
The LLaMA model used in this project is solely for research and educational purposes. It is not intended for production or commercial use. All findings and results from this project should be considered as experimental and exploratory. Use of the model should comply with any applicable legal regulations and ethical considerations. Please refer to the [LLaMA model's official documentation](https://huggingface.co/models) for additional guidelines and limitations.





