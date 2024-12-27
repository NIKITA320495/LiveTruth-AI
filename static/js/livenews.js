// YouTube API and Google Custom Search API keys
const apiKeyyt = ""; // Replace with your YouTube Data API key
const query = "India live news"; // Search keyword for live news
const apiUrlyt = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${query}&type=video&eventType=live&key=${apiKeyyt}&maxResults=5`;

const customSearchApiKey = ""; // Replace with your Google Custom Search API key
const customSearchEngineId = ""; // Replace with your Google Custom Search Engine ID
const dateFilter = "d10"; // Last 7 days

// Fetch live news from YouTube API
async function fetchYouTubeLiveNews() {
    try {
        const response = await fetch(apiUrlyt);
        const data = await response.json();

        if (data.items && data.items.length > 0) {
            const firstVideo = data.items[0];
            embedYouTubeVideo(firstVideo.id.videoId, firstVideo.snippet.title); // Embed the first video by default
            displayLiveNews(data.items); // Display all live videos
        } else {
            console.error("No live news streams found.");
            displayPlaceholder("No Live News Found");
        }
    } catch (error) {
        console.error("Error fetching live news:", error);
        displayPlaceholder("Error Fetching News");
    }
}

// Display live news in the list
function displayLiveNews(videos) {
    const newsContainer = document.querySelector('.pb-3');
    newsContainer.innerHTML = ''; // Clear old content

    videos.forEach(video => {
        const videoId = video.id.videoId;
        const title = video.snippet.title;
        const thumbnail = video.snippet.thumbnails.medium.url;
        const channelName = video.snippet.channelTitle;
        const publishedAt = new Date(video.snippet.publishedAt).toLocaleDateString();

        const newsItem = `
            <div class="d-flex mb-3 trending-article" data-video-id="${videoId}" data-title="${title}">
                <img src="${thumbnail}" 
                    style="width: 100px; height: 120px; object-fit: cover;">
                <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" 
                    style="height: 120px;">
                    <div class="mb-1" style="font-size: 11px;">
                        <span>${channelName}</span>
                        <span class="px-1">/</span>
                        <span>${publishedAt}</span>
                    </div>
                    <p class="h6 m-0">${title}</p>
                </div>
            </div>`;
        newsContainer.innerHTML += newsItem;
    });

    document.querySelectorAll('.trending-article').forEach(article => {
        article.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            const title = this.getAttribute('data-title');
            embedYouTubeVideo(videoId, title);
        });
    });
}

// Embed YouTube video in the iframe
function embedYouTubeVideo(videoId, title) {
    const iframe = document.getElementById("youtube-embed");
    iframe.src = `https://www.youtube.com/embed/${videoId}`;
    const titleElement = document.querySelector('.video-title'); // Update with your title element
    if (titleElement) {
        titleElement.textContent = title || "Live News";
    }

    // Fetch related sources for the current video
    findRelatedSources(title);
}

// Fetch related sources using Google Custom Search
async function findRelatedSources(topic) {
    try {
        const searchQuery = encodeURIComponent(topic);
        const searchApiUrl = `https://www.googleapis.com/customsearch/v1?q=${searchQuery}&key=${customSearchApiKey}&cx=${customSearchEngineId}&dateRestrict=${dateFilter}`;

        const response = await fetch(searchApiUrl);
        const searchData = await response.json();

        if (searchData.items && searchData.items.length > 0) {
            displayRelatedSources(searchData.items);
        } else {
            console.error("No related sources found.");
            displayNoSourcesPlaceholder();
        }
    } catch (error) {
        console.error("Error fetching related sources:", error);
    }
}

// Display related sources
function displayRelatedSources(sources) {
    const sourcesContainer = document.querySelector('.related-sources');
    sourcesContainer.innerHTML = ''; // Clear old sources

    sources.forEach(source => {
        const sourceItem = `
            <div class="source-item">
                <a href="${source.link}" target="_blank">${source.title}</a>
                <p>${source.snippet}</p>
            </div>`;
        sourcesContainer.innerHTML += sourceItem;
    });
}

// Display a placeholder for no video or error
function displayPlaceholder(message) {
    const iframe = document.getElementById("youtube-embed");
    iframe.src = `https://via.placeholder.com/500x280?text=${encodeURIComponent(message)}`;
}

// Display placeholder for no related sources
function displayNoSourcesPlaceholder() {
    const sourcesContainer = document.querySelector('.related-sources');
    sourcesContainer.innerHTML = '<p>No related sources found.</p>';
}

// Call the function to fetch live videos and embed one by default
fetchYouTubeLiveNews();
