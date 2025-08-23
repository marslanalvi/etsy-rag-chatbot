document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const $chatbot = document.querySelector('.chatbot');
  const $chatbotMessages = document.querySelector('.chatbot__messages');
  const $chatbotInput = document.querySelector('.chatbot__input');
  const $chatbotSubmit = document.querySelector('.chatbot__submit');
  const $minimizeBtn = document.querySelector('.minimize-btn');
  const $expandBtn = document.querySelector('.expand-btn');
  const $sourcesPanel = document.querySelector('.sources-panel');
  const $closeSourcesBtn = document.querySelector('.close-sources');
  const $sourcesList = document.querySelector('.sources-list');
  const $noSources = document.querySelector('.no-sources');

  // Current sources for the latest message
  let currentSources = [];
  let isFullscreen = false;

  // Initialize
  $chatbotInput.focus();

  // Event Listeners
  $chatbotSubmit.addEventListener('click', sendMessage);

  $chatbotInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  });

  $minimizeBtn.addEventListener('click', () => {
    $chatbot.classList.toggle('chatbot--minimized');
    if ($chatbot.classList.contains('chatbot--minimized')) {
      $minimizeBtn.innerHTML = '<i class="fas fa-expand"></i>';
    } else {
      $minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
      $chatbotInput.focus();
    }
  });

  $expandBtn.addEventListener('click', () => {
    isFullscreen = !isFullscreen;
    if (isFullscreen) {
      $chatbot.style.position = 'fixed';
      $chatbot.style.top = '0';
      $chatbot.style.left = '0';
      $chatbot.style.width = '100%';
      $chatbot.style.height = '100%';
      $chatbot.style.maxWidth = '100%';
      $chatbot.style.borderRadius = '0';
      $expandBtn.innerHTML = '<i class="fas fa-compress"></i>';
    } else {
      $chatbot.style.position = '';
      $chatbot.style.top = '';
      $chatbot.style.left = '';
      $chatbot.style.width = '';
      $chatbot.style.height = '';
      $chatbot.style.maxWidth = '';
      $chatbot.style.borderRadius = '';
      $expandBtn.innerHTML = '<i class="fas fa-expand"></i>';
    }
  });

  $closeSourcesBtn.addEventListener('click', () => {
    $sourcesPanel.classList.remove('active');
  });

  // Functions
  function sendMessage() {
    const text = $chatbotInput.value.trim();
    if (text === '') return;

    // Add user message
    addMessage('user', text);

    // Clear input
    $chatbotInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Send to backend
    fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text })
    })
    .then(response => response.json())
    .then(data => {
      // Hide typing indicator
      hideTypingIndicator();

      // Store sources with relevance scores
      currentSources = data.sources || [];
      const relevanceScore = data.relevance_score || 0;

      // Add AI response with relevance score
      addMessage('ai', data.message, currentSources, relevanceScore);
    })
    .catch(error => {
      console.error('Error:', error);
      hideTypingIndicator();
      addMessage('ai', 'Sorry, something went wrong. Please try again.');
    });
  }

  function addMessage(sender, content, sources = [], relevanceScore = 0) {
    const senderClass = sender === 'user' ? 'is-user' : 'is-ai';
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Process markdown if it's an AI message
    let processedContent = content;
    if (sender === 'ai' && window.marked) {
      processedContent = marked.parse(content);
    }

    // Create message element
    const messageEl = document.createElement('li');
    messageEl.className = `${senderClass} animation`;

    // Create message content
    const messageContent = document.createElement('div');
    messageContent.className = 'chatbot__message';
    messageContent.innerHTML = processedContent;

    // Add message to DOM
    messageEl.appendChild(messageContent);
    $chatbotMessages.appendChild(messageEl);

    // Add event listener to "View Sources" button
    if (sender === 'ai' && sources.length > 0) {
      const viewSourcesBtn = messageEl.querySelector('.view-sources');
      if (viewSourcesBtn) {
        viewSourcesBtn.addEventListener('click', () => {
          $sourcesPanel.classList.add('active');
        });
      }
    }

    // Delay scroll to bottom
    setTimeout(() => {
      $chatbotMessages.scrollTop = $chatbotMessages.scrollHeight;
    }, 100); // Delay scroll by 100ms to allow DOM updates
  }

  function showTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    $chatbotMessages.appendChild(typingIndicator);
    $chatbotMessages.scrollTop = $chatbotMessages.scrollHeight;
  }

  function hideTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  function updateSourcesPanel(sources) {
    if (sources.length > 0) {
      $noSources.style.display = 'none';
      $sourcesList.innerHTML = '';

      sources.forEach((source, index) => {
        const sourceItem = document.createElement('li');
        sourceItem.className = 'source-item';

        // Determine relevance class based on score
        let relevanceClass = 'low-relevance';
        const relevance = source.relevance || 0;

        if (relevance >= 90) {
          relevanceClass = 'high-relevance';
        } else if (relevance >= 70) {
          relevanceClass = 'medium-relevance';
        }

        // Get text snippet if available
        const textSnippet = source.text_snippet || 'No text preview available';

        // Create source item with relevance indicator and text snippet
        sourceItem.innerHTML = `
          <div class="source-header">
            <h4>Source ${index + 1}</h4>
            <span class="source-relevance ${relevanceClass}">${relevance}%</span>
          </div>
          <p class="source-name">${source.name || source}</p>
          <div class="source-snippet">
            <h5>Text Preview:</h5>
            <p>${textSnippet}</p>
          </div>
        `;

        $sourcesList.appendChild(sourceItem);
      });
    } else {
      $noSources.style.display = 'block';
      $sourcesList.innerHTML = '';
    }
  }

  function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }
});
