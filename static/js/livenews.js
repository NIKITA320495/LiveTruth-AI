const apiKey = "AIzaSyCmH0ch5rXw18hHmTXBtk5bC77LwpqN8c0"; // Replace with your YouTube Data API key
const query = "live news"; // Your search keyword
const apiUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${query}&type=video&eventType=live&key=${apiKey}`;

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
