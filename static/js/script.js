
      function flipCard(element) {
  element.querySelector('.flip-card-inner').classList.add('flipped');
}

function unflipCard(element) {
  element.querySelector('.flip-card-inner').classList.remove('flipped');
}
document.getElementById('learnMoreBtn').addEventListener('click', function() {
    // Scroll to the features section
    document.getElementById('features-section').scrollIntoView({ behavior: 'smooth' });
});


      // Global state to keep track of the selected recommendation
      let selectedRecommendation = null;
    
      // Function to display recommendations or a single description
      function displayRecommendations(recommendations) {
  const suggestionsArea = document.getElementById('suggestionsArea');
  const inputText = document.getElementById('inputText'); // Make sure to get the inputText element
  suggestionsArea.innerHTML = ''; // Clear previous suggestions

  recommendations.forEach(rec => {
    const emojiCombination = rec['emojis'];
    const sentimentScore = rec['sentiment']; // Assuming this is included
    const recommendationDiv = document.createElement('div');
    recommendationDiv.textContent = emojiCombination;

    recommendationDiv.classList.add('recommendation');
    recommendationDiv.onclick = function() {
      inputText.value = emojiCombination; // Set the text box to the selected recommendation
      // Hide the suggestionsArea or clear it, depending on your UI needs
      suggestionsArea.innerHTML = ''; // This hides the recommendations after selection
      // Store the selected recommendation for later use
      selectedRecommendation = rec;
    };
    suggestionsArea.appendChild(recommendationDiv);
  });
}
    
      // Function to display the corresponding sentence for a selected recommendation
      function displayCorrespondingSentence(sentence) {
        const sentenceDisplay = document.getElementById('sentenceDisplay');
        sentenceDisplay.textContent = sentence; // Update the text content with the sentence
      }
    
      // Function to fetch recommendations based on input text
      function fetchRecommendations(text) {
        fetch('/convert', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ emoji: text })
        })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            displayCorrespondingSentence(data.error);
          } else if (data.emojiCombinations && data.emojiCombinations.length > 0) {
            displayRecommendations(data.emojiCombinations);
          } else {
            displayCorrespondingSentence("No recommendations found.");
          }
        })
        .catch(error => {
          console.error('Error:', error);
          displayCorrespondingSentence('Error fetching recommendations.');
        });
      }
    
      document.addEventListener('DOMContentLoaded', function() {
        const emojiPicker = document.getElementById('emojiPicker');
        const inputText = document.getElementById('inputText');
        const generateSentenceBtn = document.getElementById('generateSentenceBtn');

        emojiPicker.addEventListener('emoji-click', event => {
          const emoji = event.detail.unicode;
          inputText.value += emoji; // Append the clicked emoji to the input value
          fetchRecommendations(inputText.value); // Fetch recommendations based on the input value
        });
    
        generateSentenceBtn.addEventListener('click', function() {
          if (selectedRecommendation) {
            displayCorrespondingSentence(selectedRecommendation.sentence);
          } else {
            displayCorrespondingSentence('Please select a recommendation first.');
          }
        });
 
      });
   