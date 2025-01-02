const apiKey = ''; // Replace with your Newsdata.io API key
const apiUrl = `https://newsdata.io/api/1/news?apikey=${apiKey}&language=en&country=in`;

let currentChart = null; // Variable to keep track of the current chart
let currentArticleUrl = ''; // Track the current article being processed

async function fetchNews(query = '') {
    let searchUrl = apiUrl;
    if (query) {
        searchUrl += `&q=${encodeURIComponent(query)}`; // Add search term to the API URL
    }
    console.log('Fetching news from:', searchUrl); // Log the URL for debugging
    try {
        const response = await fetch(searchUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayNews(data.results || []); // Ensure results are passed as an array
    } catch (error) {
        console.error('Error fetching news:', error.message);
        document.querySelector('.pb-3').innerHTML = '<p>Failed to fetch news. Please try again later.</p>';
    }
}

function displayNews(articles) {
    const newsContainer = document.querySelector('.pb-3');
    newsContainer.innerHTML = ''; // Clear old content

    if (!articles || articles.length === 0) {
        newsContainer.innerHTML = '<p>No news found for this search term.</p>';
        return;
    }

    // Track if the first article is already displayed
    let firstArticleDisplayed = false;

    articles.forEach((article, index) => {
        if (index < 5) { // Limit to 5 articles
            const newsItem = `
                <div class="d-flex mb-3 trending-article" 
                    data-url="${article.link || '#'}" 
                    data-image="${article.image_url || 'default-image.jpg'}" 
                    data-title="${article.title || 'Untitled Article'}">
                    <img src="${article.image_url || 'default-image.jpg'}" 
                        style="width: 100px; height: 120px; object-fit: cover;">
                    <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" 
                        style="height: 120px;">
                        <div class="mb-1" style="font-size: 11px;">
                            <span>${article.source_id || 'Unknown Source'}</span>
                            <span class="px-1">/</span>
                            <span>${article.pubDate ? new Date(article.pubDate).toLocaleDateString() : 'Unknown Date'}</span>
                        </div>
                        <p class="h6 m-0">${article.title || 'No Title Available'}</p>
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

            // Only fetch summary if not already fetched for this article
            if (articleUrl !== currentArticleUrl) {
                currentArticleUrl = articleUrl; // Update the current article URL
                embedImage(imageUrl, title); // Embed image in the video container
                await fetchAndDisplaySummary(articleUrl, title); // Fetch and display the summary for clicked article
            }
        });
    });

    // Set the first article as default if available and not already displayed
    if (articles.length > 0 && !firstArticleDisplayed) {
        const firstArticle = articles[0];
        embedImage(firstArticle.image_url || 'default-image.jpg', firstArticle.title || 'No Title Available');
        fetchAndDisplaySummary(firstArticle.link || '#', firstArticle.title || 'No Title Available'); // Automatically fetch summary for the first article
        firstArticleDisplayed = true;
    }
}

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

async function fetchAndDisplaySummary(articleUrl, articleTitle = '') {
    if (!articleUrl) {
        console.log('No URL provided for summarization.');
        return;
    }

    const summaryContainer = document.querySelector('.summary-container');
    summaryContainer.innerHTML = '<p>Loading summary...</p>'; // Show loading text
    
    // Hide the graph while summary is loading
    const graphContainer = document.getElementById('confidenceChart');
    graphContainer.style.display = 'none'; // Hide the graph

    try {
        const response = await fetch('http://127.0.0.1:5000/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: articleUrl, title: articleTitle }), // Send URL and title
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data && typeof data.main_summary === 'string') {
            let relatedSummariesTable = `
                <h4>Related Summaries:</h4>
                    <table class="table table-bordered mt-3" style="table-layout: fixed; width: 100%;">
                    <thead>
                        <tr>
                            <th style="width: 40%; word-wrap: break-word;">Web Source</th>
                            <th style="width: 60%;">Summary</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.related_summaries.forEach((summary) => {
                relatedSummariesTable += `
                    <tr>
                <td><a href="${summary.URL}" target="_blank">${summary.URL}</a></td>
                <td style="text-align: justify;">${summary.Summary}</td>
            </tr>
                `;
            });

            relatedSummariesTable += `
                    </tbody>
                </table>
            `;

            summaryContainer.innerHTML = `
                <h3 class="mb-3">Summary</h3>
                <p>${data.main_summary}</p>
                ${relatedSummariesTable}
            `;

            // Embed image in the container
            const imageUrl = data.image_url || 'default-image.jpg';
            embedImage(imageUrl, articleTitle);

            // Destroy the previous chart if it exists
            if (currentChart) {
                currentChart.destroy();
            }

            // Wait for accuracy score and then draw the graph
            await fetchAndDrawGraph();

            // Show the graph after it's drawn
            graphContainer.style.display = 'block'; // Show the graph again

        } else {
            summaryContainer.innerHTML = '<p>Summary not available. Please try again later.</p>';
        }
    } catch (error) {
        console.error('Error fetching summary:', error.message);
        summaryContainer.innerHTML = '<p>An error occurred while fetching the summary.</p>';
    }
}

async function fetchAndDrawGraph() {
    console.log("Attempting to draw graphs...");
    try {
        const response = await fetch('http://127.0.0.1:5000/graph_data');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Graph data fetched:", data);

        const sampleData = data.sample_data;
        const averageAccuracy = data.average_accuracy;

        if (!sampleData || sampleData.length === 0) {
            console.warn("No valid data for graphs. Skipping visualization.");
            return;
        }

        const labels = sampleData.map(item => new URL(item.URL).hostname);
        const confidenceScores = sampleData.map(item => item.Accuracy);

        labels.push("Average");
        confidenceScores.push(averageAccuracy);

        // --- First Graph: Confidence Scores (Horizontal Bar Chart) ---
        const ctx1 = document.getElementById('confidenceChart').getContext('2d');

        // If a chart already exists, destroy it before creating a new one
        if (currentChart) {
            currentChart.destroy();
        }

        // Create the first chart (horizontal bar chart)
        currentChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Confidence Scores (%)',
                    data: confidenceScores,
                    backgroundColor: labels.map(label =>
                        label === "Average" ? 'rgba(255, 99, 132, 0.2)' : 'rgba(75, 192, 192, 0.2)'
                    ),
                    borderColor: labels.map(label =>
                        label === "Average" ? 'rgba(255, 99, 132, 1)' : 'rgba(75, 192, 192, 1)'
                    ),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',  // Horizontal bar chart
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });

        // --- Second Graph: Average Accuracy (Vertical Bar Chart) ---
        const ctx2 = document.getElementById('averageAccuracyChart').getContext('2d');

        // Create the second chart (vertical bar chart for average accuracy)
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['Average Accuracy', 'Ground Truth'],
                datasets: [{
                    label: 'Accuracy (%)',
                    data: [averageAccuracy, 70],  // Add 70 as the constant value for Ground Truth
                    backgroundColor: [
                        'rgba(153, 102, 255, 0.2)',  // Color for Average Accuracy
                        'rgba(255, 159, 64, 0.2)'    // Color for Ground Truth
                    ],
                    borderColor: [
                        'rgba(153, 102, 255, 1)',  // Border color for Average Accuracy
                        'rgba(255, 159, 64, 1)'    // Border color for Ground Truth
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 10
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Error drawing the graphs:", error);
    }
}


// Add event listener for search button
document.addEventListener('DOMContentLoaded', () => {
    fetchNews(); // Fetch news on page load

    // Add event listener for search button
    document.getElementById('searchButton').addEventListener('click', (event) => {
        event.preventDefault(); // Prevent page refresh on search
        const query = document.getElementById('searchInput').value;
        fetchNews(query); // Fetch news based on search input
    });
});
