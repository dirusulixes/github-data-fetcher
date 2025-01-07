import requests
import os

# Set your GitHub token here (retrieve from environment variable)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your_token_here')
if GITHUB_TOKEN == 'your_token_here':
    raise ValueError("Please set your GitHub token in the environment variable 'GITHUB_TOKEN'")
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Define the owner, repo, and issue number
OWNER = 'istio'
REPO = 'community'
ISSUE_NUMBER = 1

# Fetch issue details
def fetch_issue(owner, repo, issue_number):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issue: {e}")
        return None

# Main script
if __name__ == "__main__":
    print(f"Fetching details for issue #{ISSUE_NUMBER} in {OWNER}/{REPO}...")
    issue_data = fetch_issue(OWNER, REPO, ISSUE_NUMBER)
    if issue_data:
        print("Issue Data:")
        print(issue_data)
    else:
        print("Failed to fetch issue data. Check your token and API status.")
