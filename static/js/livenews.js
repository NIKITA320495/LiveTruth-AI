const apiKey = ""; // Replace with your YouTube Data API key
const query = "India live news"; // Search keyword for live news
const apiUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${query}&type=video&eventType=live&key=${apiKey}&maxResults=5`;

// Fetch live news from YouTube API
async function fetchYouTubeLiveNews() {
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        if (data.items && data.items.length > 0) {
            displayLiveNews(data.items);
        } else {
            console.error("No live news streams found.");
        }
    } catch (error) {
        console.error("Error fetching live news:", error);
    }
}
fetch(apiUrl)
  .then(response => response.json())
  .then(data => {
    if (data.items && data.items.length > 0) {
      // Extract the first live video's ID
      const videoId = data.items[0].id.videoId;

      // Debug: Log the videoId to ensure it's correct
      console.log("Live Video ID:", videoId);

      // Update the iframe src dynamically with the correct format
      const iframe = document.getElementById("youtube-embed");
      iframe.src = `https://www.youtube.com/embed/${videoId}`;
    } else {
      console.error("No live news streams found.");
      // Optionally update the iframe with a placeholder or message
      const iframe = document.getElementById("youtube-embed");
      iframe.src = "https://via.placeholder.com/500x280?text=No+Live+News+Found";
    }
  })
  .catch(error => console.error("Error fetching live news:", error));

// Display live news
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
            <div class="d-flex mb-3 trending-article" data-video-id="${videoId}">
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

    // Add click event listeners for dynamic articles
    document.querySelectorAll('.trending-article').forEach(article => {
        article.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            embedYouTubeVideo(videoId); // Embed YouTube video in the player
        });
    });
}

// Embed YouTube video in a container
function embedYouTubeVideo(videoId, title) {
  const iframe = document.getElementById("youtube-embed");
  iframe.src = 'https://www.youtube.com/embed/$' + videoId;
  const titleElement = document.querySelector('.h6.m-0'); // Assuming the title element has these classes
  titleElement.textContent = title;
}
// Call the function to fetch and display news

fetchYouTubeLiveNews();
