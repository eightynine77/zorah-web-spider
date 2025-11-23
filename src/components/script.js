// Wait for the DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', () => {

    // Get references to all the DOM elements we need
    const form = document.getElementById('crawl-form');
    const startUrlInput = document.getElementById('start-url');
    const crawlButton = document.getElementById('crawl-button');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    const resultsContainer = document.getElementById('results-container');
    const statusMessage = document.getElementById('status-message');

    // --- THIS IS THE KEY CHANGE ---
    // Since Python serves this script AND the API, we can just use a
    // relative path. This is much cleaner and more robust.
    const API_URL = '/crawl'; 

    // --- Event Listener for Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent the form from submitting normally
        const startUrl = startUrlInput.value;

        if (!startUrl) {
            displayError("Please enter a valid URL.");
            return;
        }

        setLoading(true);
        resultsContainer.innerHTML = ''; // Clear old results
        statusMessage.textContent = 'Crawling in progress... This may take a few minutes.';

        try {
            // --- API Call ---
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: startUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const results = await response.json();
            displayResults(results);

        } catch (error) {
            console.error('Crawl failed:', error);
            displayError(error.message);
        } finally {
            setLoading(false);
        }
    });

    // --- Helper Functions ---

    function setLoading(isLoading) {
        if (isLoading) {
            crawlButton.disabled = true;
            crawlButton.classList.add('opacity-50', 'cursor-not-allowed');
            buttonText.textContent = 'Crawling...';
            spinner.classList.remove('hidden');
        } else {
            crawlButton.disabled = false;
            crawlButton.classList.remove('opacity-50', 'cursor-not-allowed');
            buttonText.textContent = 'Start Crawl';
            spinner.classList.add('hidden');
        }
    }

    function displayResults(results) {
        if (results.length === 0) {
            statusMessage.textContent = 'Crawl finished. No pages found or all pages failed to load.';
            return;
        }

        statusMessage.textContent = `Crawl finished. Found ${results.length} pages.`;
        const fragment = document.createDocumentFragment();
        
        results.forEach(item => {
            const div = document.createElement('div');
            // Your uploaded file had a typo 'bg--800', I've fixed it
            div.className = 'p-3 bg-gray-800 rounded-lg shadow-md break-words';
            
            const link = document.createElement('a');
            link.href = item.url;
            link.textContent = item.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.className = 'text-blue-400 hover:underline';
            
            const title = document.createTextNode(` - ${item.title}`);
            
            div.appendChild(link);
            div.appendChild(title);
            fragment.appendChild(div);
        });

        resultsContainer.appendChild(fragment);
    }

    function displayError(message) {
        statusMessage.textContent = '';
        resultsContainer.innerHTML = `<div class="p-3 bg-red-800 text-red-100 rounded-lg">${message}</div>`;
    }
});