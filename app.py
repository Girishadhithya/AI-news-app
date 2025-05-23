# from flask import Flask, render_template, request, jsonify
# import requests
# import os

# # Initialize the Flask application
# app = Flask(__name__)

# # IMPORTANT: Enable Jinja2 extensions, specifically the 'do' extension,
# # which includes the 'cycle' tag used in trending.html for alternating colors.
# app.jinja_env.add_extension('jinja2.ext.do')

# # --- API Keys ---
# # It's generally recommended to load API keys from environment variables
# # for security and flexibility, rather than hardcoding them.
# # Example: os.environ.get("GUARDIAN_API_KEY")
# GUARDIAN_API_KEY = "90102d1e-71df-4588-be30-8eb861265c06"
# HUGGINGFACE_API_KEY = "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"

# # --- Helper Function to Fetch News from The Guardian API ---
# def fetch_news(section=None):
#     """
#     Fetches news articles from The Guardian API.
#     Optionally filters by a specific section (e.g., 'sport', 'politics').
#     """
#     try:
#         url = "https://content.guardianapis.com/search"
#         params = {
#             'api-key': GUARDIAN_API_KEY,
#             'show-fields': 'headline,trailText,thumbnail,bodyText', # Request specific fields
#             'page-size': 10, # Number of articles to fetch
#             'order-by': 'newest' # Order by newest articles
#         }
#         if section:
#             params['section'] = section # Add section filter if provided
        
#         # Make the API request with a timeout
#         response = requests.get(url, params=params, timeout=10)
        
#         # Raise an HTTPError for bad responses (4xx or 5xx)
#         response.raise_for_status()
        
#         # Parse the JSON response and return the results
#         return response.json().get('response', {}).get('results', [])
#     except requests.RequestException as e:
#         # Print error for debugging purposes
#         print(f"Error fetching news: {e}")
#         return [] # Return an empty list on error

# # --- Routes ---

# @app.route('/')
# def index():
#     """Renders the main index page."""
#     return render_template('index.html')

# @app.route('/trending')
# def trending():
#     """
#     Fetches and displays trending news articles.
#     Articles are fetched via fetch_news (no specific section).
#     """
#     articles = fetch_news()
#     return render_template('trending.html', articles=articles)

# @app.route('/sports')
# def sports():
#     """
#     Fetches and displays sports news articles.
#     """
#     articles = fetch_news('sport') # Fetch articles specifically from the 'sport' section
#     return render_template('sports.html', articles=articles)

# @app.route('/politics')
# def politics():
#     """
#     Fetches and displays politics news articles.
#     """
#     articles = fetch_news('politics') # Fetch articles specifically from the 'politics' section
#     return render_template('politics.html', articles=articles)

# @app.route('/summarizer', methods=['GET', 'POST'])
# def summarizer():
#     """
#     Handles article summarization.
#     - GET: Displays the summarizer form.
#     - POST: Fetches an article based on user input and summarizes it
#             using the Hugging Face BART Large CNN model.
#     """
#     summary = ''
#     if request.method == 'POST':
#         incident = request.form.get('incident', '').strip()
#         if incident:
#             try:
#                 # First, search for a relevant article using the incident keyword
#                 guardian_response = requests.get("https://content.guardianapis.com/search", params={
#                     'q': incident,
#                     'api-key': GUARDIAN_API_KEY,
#                     'show-fields': 'bodyText', # We need the full body text for summarization
#                     'page-size': 1 # Get only the top result
#                 }, timeout=10)
#                 guardian_response.raise_for_status()
#                 articles = guardian_response.json().get("response", {}).get("results", [])

#                 if articles:
#                     article_text = articles[0]['fields'].get('bodyText', '')
#                     # Check if the article text is long enough for summarization
#                     if len(article_text) >= 200:
#                         # Call the Hugging Face summarization API
#                         hf_response = requests.post(
#                             "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
#                             headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
#                             json={"inputs": article_text[:4000]} # Truncate text if too long for API
#                         )
#                         if hf_response.status_code == 200:
#                             summary = hf_response.json()[0].get('summary_text', '')
#                         else:
#                             summary = f'Summarization failed due to API error: {hf_response.status_code} - {hf_response.text}'
#                     else:
#                         summary = 'Article too short to summarize (requires at least 200 characters).'
#                 else:
#                     summary = 'No relevant news found for the incident.'
#             except requests.RequestException as e:
#                 summary = f'Error fetching news for summarization: {e}'
#         else:
#             summary = 'Please provide an incident to summarize.'
#     return render_template('summarizer.html', summary=summary)

# @app.route('/game')
# def game():
#     """Renders the game page."""
#     return render_template('game.html')

# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     """
#     Handles news search functionality.
#     - GET: Displays the search page, potentially with results if a query is present.
#     """
#     query = request.args.get('q', '').strip()
#     articles = []

#     if query:
#         try:
#             # Search The Guardian API for articles matching the query
#             response = requests.get("https://content.guardianapis.com/search", params={
#                 'q': query,
#                 'api-key': GUARDIAN_API_KEY,
#                 'show-fields': 'headline,trailText,thumbnail,bodyText',
#                 'page-size': 10
#             }, timeout=10)
#             response.raise_for_status()
#             articles = response.json().get("response", {}).get("results", [])
#         except requests.RequestException as e:
#             print(f"Error during search: {e}")
#             articles = [] # Ensure articles is an empty list on error

#     return render_template('search.html', articles=articles, query=query)

# @app.route('/article/<path:article_id>')
# def article(article_id):
#     """
#     Displays a single article by its ID.
#     The article_id is a path, e.g., 'world/2023/jan/01/example-article'.
#     """
#     try:
#         url = f"https://content.guardianapis.com/{article_id}"
#         params = {
#             'api-key': GUARDIAN_API_KEY,
#             'show-fields': 'headline,body' # Request headline and full body
#         }
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json().get("response", {}).get("content", {})
        
#         # Pass the fetched article data to the template
#         return render_template("article.html", article=data)
#     except requests.RequestException as e:
#         print(f"Error loading article {article_id}: {e}")
#         # Return a user-friendly error message
#         return "Error loading article. Please try again later.", 500


# if __name__ == '__main__':
#     # Run the Flask application in debug mode (useful for development)
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import requests
import os

# Initialize the Flask application
app = Flask(__name__)

# IMPORTANT: Enable Jinja2 extensions, specifically the 'do' extension,
# which includes the 'cycle' tag used in trending.html for alternating colors.
app.jinja_env.add_extension('jinja2.ext.do')

# --- API Keys ---
# It's generally recommended to load API keys from environment variables
# for security and flexibility, rather than hardcoding them.
# Example: os.environ.get("GUARDIAN_API_KEY")
GUARDIAN_API_KEY = "90102d1e-71df-4588-be30-8eb861265c06"
HUGGINGFACE_API_KEY = "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"

# --- Helper Function to Fetch News from The Guardian API ---
def fetch_news(section=None):
    """
    Fetches news articles from The Guardian API.
    Optionally filters by a specific section (e.g., 'sport', 'politics').
    """
    try:
        url = "https://content.guardianapis.com/search"
        params = {
            'api-key': GUARDIAN_API_KEY,
            'show-fields': 'headline,trailText,thumbnail,bodyText', # Request specific fields
            'page-size': 10, # Number of articles to fetch
            'order-by': 'newest' # Order by newest articles
        }
        if section:
            params['section'] = section # Add section filter if provided
        
        # Make the API request with a timeout
        response = requests.get(url, params=params, timeout=10)
        
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response and return the results
        return response.json().get('response', {}).get('results', [])
    except requests.RequestException as e:
        # Print error for debugging purposes
        print(f"Error fetching news: {e}")
        return [] # Return an empty list on error

# --- Routes ---

@app.route('/')
def index():
    """Renders the main index page."""
    return render_template('index.html')

@app.route('/trending')
def trending():
    """
    Fetches and displays trending news articles.
    Articles are fetched via fetch_news (no specific section).
    """
    articles = fetch_news()
    return render_template('trending.html', articles=articles)

@app.route('/sports')
def sports():
    """
    Fetches and displays sports news articles.
    """
    articles = fetch_news('sport') # Fetch articles specifically from the 'sport' section
    return render_template('sports.html', articles=articles)

@app.route('/politics')
def politics():
    """
    Fetches and displays politics news articles.
    """
    articles = fetch_news('politics') # Fetch articles specifically from the 'politics' section
    return render_template('politics.html', articles=articles)

@app.route('/summarizer', methods=['GET', 'POST'])
def summarizer():
    """
    Handles article summarization.
    - GET: Displays the summarizer form.
    - POST: Fetches an article based on user input and summarizes it
            using the Hugging Face BART Large CNN model.
    """
    summary = ''
    if request.method == 'POST':
        incident = request.form.get('incident', '').strip()
        if incident:
            try:
                # First, search for a relevant article using the incident keyword
                guardian_response = requests.get("https://content.guardianapis.com/search", params={
                    'q': incident,
                    'api-key': GUARDIAN_API_KEY,
                    'show-fields': 'bodyText', # We need the full body text for summarization
                    'page-size': 1 # Get only the top result
                }, timeout=10)
                guardian_response.raise_for_status()
                articles = guardian_response.json().get("response", {}).get("results", [])

                if articles:
                    article_text = articles[0]['fields'].get('bodyText', '')
                    # Check if the article text is long enough for summarization
                    if len(article_text) >= 200:
                        # Call the Hugging Face summarization API
                        hf_response = requests.post(
                            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
                            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                            json={"inputs": article_text[:4000]} # Truncate text if too long for API
                        )
                        if hf_response.status_code == 200:
                            summary = hf_response.json()[0].get('summary_text', '')
                        else:
                            summary = f'Summarization failed due to API error: {hf_response.status_code} - {hf_response.text}'
                    else:
                        summary = 'Article too short to summarize (requires at least 200 characters).'
                else:
                    summary = 'No relevant news found for the incident.'
            except requests.RequestException as e:
                summary = f'Error fetching news for summarization: {e}'
        else:
            summary = 'Please provide an incident to summarize.'
    return render_template('summarizer.html', summary=summary)

@app.route('/game')
def game():
    """Renders the game page."""
    return render_template('game.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Handles news search functionality.
    - GET: Displays the search page, potentially with results if a query is present.
    """
    query = request.args.get('q', '').strip()
    articles = []

    if query:
        try:
            # Search The Guardian API for articles matching the query
            response = requests.get("https://content.guardianapis.com/search", params={
                'q': query,
                'api-key': GUARDIAN_API_KEY,
                'show-fields': 'headline,trailText,thumbnail,bodyText',
                'page-size': 10
            }, timeout=10)
            response.raise_for_status()
            articles = response.json().get("response", {}).get("results", [])
        except requests.RequestException as e:
            print(f"Error during search: {e}")
            articles = [] # Ensure articles is an empty list on error

    return render_template('search.html', articles=articles, query=query)

@app.route('/article/<path:article_id>')
def article(article_id):
    """
    Displays a single article by its ID.
    The article_id is a path, e.g., 'world/2023/jan/01/example-article'.
    """
    try:
        url = f"https://content.guardianapis.com/{article_id}"
        params = {
            'api-key': GUARDIAN_API_KEY,
            'show-fields': 'headline,body,thumbnail' # ADDED 'thumbnail' here
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("response", {}).get("content", {})
        
        # Pass the fetched article data to the template
        return render_template("article.html", article=data)
    except requests.RequestException as e:
        print(f"Error loading article {article_id}: {e}")
        # Return a user-friendly error message
        return "Error loading article. Please try again later.", 500


if __name__ == '__main__':
    # Run the Flask application in debug mode (useful for development)
    app.run(debug=True)
