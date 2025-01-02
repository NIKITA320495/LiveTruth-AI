const apiKey = ''; // Replace with your Newsdata.io API key
const apiUrl = `https://newsdata.io/api/1/news?apikey=${apiKey}&language=en&country=in`;

// Set a cache expiration time (in milliseconds, e.g., 1 hour)
const CACHE_EXPIRATION_TIME = 60 * 60 * 1000; // 1 hour

async function fetchNews() {
    // Check if cached news exists and is still valid
    const cachedNews = localStorage.getItem('cachedNews');
    const cachedTime = localStorage.getItem('cachedTime');
    
    if (cachedNews && cachedTime && (Date.now() - cachedTime) < CACHE_EXPIRATION_TIME) {
        // Use cached news if it's still valid
        displayNews(JSON.parse(cachedNews));
        console.log('Using cached news data');
    } else {
        // Fetch new news if no valid cache exists
        console.log('Fetching new news from API:', apiUrl);
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            localStorage.setItem('cachedNews', JSON.stringify(data.results)); // Cache the news
            localStorage.setItem('cachedTime', Date.now().toString()); // Cache the time
            displayNews(data.results); // Display the fetched news
        } catch (error) {
            console.error('Error fetching news:', error.message);
        }
    }
}

function displayNews(newsArticles) {
    const carouselContainer = document.getElementById('news-carousel');
    carouselContainer.innerHTML = ''; // Clear any existing content

    newsArticles.forEach(article => {
        const newsItem = document.createElement('div');
        newsItem.classList.add('position-relative', 'overflow-hidden');
        newsItem.style.height = '435px';

        const imageUrl = article.image_url || '/static/img/default-image.jpg'; // Fallback image if none is available
        const articleUrl = article.link;

        newsItem.innerHTML = `
            <img class="img-fluid h-100" src="${imageUrl}" style="object-fit: cover;">
            <div class="overlay">
                <div class="mb-1">
                    <a class="text-white" href="#">${article.category || 'General'}</a>
                    <span class="px-2 text-white">/</span>
                    <a class="text-white" href="#">${new Date(article.pubDate).toLocaleDateString()}</a>
                </div>
                <a class="h2 m-0 text-white font-weight-bold" href="${articleUrl}" target="_blank">${article.title}</a>
            </div>
        `;
        
        carouselContainer.appendChild(newsItem);
    });

    // Reinitialize the carousel after dynamically adding items
    $('#news-carousel').owlCarousel('destroy'); // Destroy existing carousel instance if any
    $('#news-carousel').owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        nav: false,  // Disable navigation buttons
        dots: true    // Keep dots for navigation
    });
}

// Fetch the news when the page loads
fetchNews();
