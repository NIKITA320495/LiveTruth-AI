const apiKey = '';
const apiUrl = `https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=${apiKey}`;

// Fetch news articles from the API
async function fetchNews() {
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        displayNews(data.articles);
    } catch (error) {
        console.error('Error fetching news:', error);
    }
}

// Display news articles dynamically
function displayNews(articles) {
    const newsContainer = document.querySelector('.pb-3');
    newsContainer.innerHTML = ''; // Clear old content

    articles.forEach((article, index) => {
        if (index < 5) { // Limit to 5 articles
            const newsItem = `
                <div class="d-flex mb-3 trending-article" 
                    data-url="${article.url}" 
                    data-image="${article.urlToImage}" 
                    data-title="${article.title}">
                    <img src="${article.urlToImage}" 
                        style="width: 100px; height: 120px; object-fit: cover;">
                    <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" 
                        style="height: 120px;">
                        <div class="mb-1" style="font-size: 11px;">
                            <span>${article.source.name}</span>
                            <span class="px-1">/</span>
                            <span>${new Date(article.publishedAt).toLocaleDateString()}</span>
                        </div>
                        <p class="h6 m-0">${article.title}</p>
                    </div>
                </div>`;
            newsContainer.innerHTML += newsItem;
        }
    });

    // Add click event listeners for dynamic articles
    document.querySelectorAll('.trending-article').forEach(article => {
        article.addEventListener('click', async function () {
            const articleUrl = this.getAttribute('data-url');
            const imageUrl = this.getAttribute('data-image');
            const title = this.getAttribute('data-title');
            embedImage(imageUrl, title); // Embed image in the video container
            await fetchAndDisplaySummary(articleUrl); // Fetch and display the summary
        });
    });
}

// Embed the article image and title in the video container
function embedImage(imageUrl, title) {
    const videoContainer = document.querySelector('.embed-responsive');
    videoContainer.innerHTML = `
        <div style="position: relative; width: 100%; height: auto;">
            <img src="${imageUrl}" class="img-fluid w-100" 
                style="object-fit: cover; border: none; margin: 0; padding: 0;">
        </div>
        <h4 class="mt-3 text-center">${title}</h4>
    `;
}

// Fetch summary from Flask backend and display it
// Fetch summary from Flask backend and display it
async function fetchAndDisplaySummary(articleUrl) {
    const summaryContainer = document.querySelector('.summary-container');
    summaryContainer.innerHTML = '<p>Loading summary...</p>'; // Show loading text

    try {
        const response = await fetch('http://127.0.0.1:5000/summarize', { // Correct endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: articleUrl }), // Send the article URL
        });

        if (!response.ok) {
            // Handle HTTP errors
            const errorData = await response.json();
            console.error('Error response:', errorData);
            summaryContainer.innerHTML = `<p>Error: ${errorData.error || 'Failed to fetch summary.'}</p>`;
            return;
        }

        const data = await response.json();

        if (data && data.summary) {
            // Display the summary
            summaryContainer.innerHTML = `
                <h3 class="mb-3">Summary</h3>
                <p>${data.summary}</p>
            `;
        } else {
            // Handle missing summary field
            console.error('Invalid response structure:', data);
            summaryContainer.innerHTML = '<p>Summary not available. Please try again later.</p>';
        }
    } catch (error) {
        // Handle network or other errors
        console.error('Error fetching summary:', error);
        summaryContainer.innerHTML = '<p>An error occurred while fetching the summary.</p>';
    }
}


// Set default content for the embed container
document.addEventListener('DOMContentLoaded', () => {
    const videoContainer = document.querySelector('.embed-responsive');
    videoContainer.innerHTML = `
        <div class="default-content">
            <!-- Default content, such as a video or image -->
            <iframe width="560" height="315" src="https://www.youtube.com/embed/DUYM-JhQgS4" 
                title="Default Video" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; 
                encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
    `;

    fetchNews(); // Fetch news on page load
});