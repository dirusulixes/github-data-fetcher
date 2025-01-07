import requests
import os
import json
import time
from tqdm import tqdm

# Set your GitHub token here (retrieve from environment variable)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your_token_here')
if GITHUB_TOKEN == 'your_token_here':
    raise ValueError("Please set your GitHub token in the environment variable 'GITHUB_TOKEN'")
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Repositories to fetch data from
REPOSITORIES = [
    {'owner': 'istio', 'repo': 'community'},
    {'owner': 'istio', 'repo': 'istio'}
]

# Time range for 2022
START_DATE = '2022-01-01T00:00:00Z'
END_DATE = '2022-12-31T23:59:59Z'

# GitHub API rate limit delay (in seconds)
API_DELAY = 4

# Fetch commit comments
def fetch_commit_comments(owner, repo, results_file):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    params = {'since': START_DATE, 'until': END_DATE, 'per_page': 100}
    all_comments = []

    # Load existing results if the file exists
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                all_comments = json.load(f)
        except json.JSONDecodeError:
            print(f"Failed to parse {results_file}. Starting fresh.")

    existing_commit_shas = {comment['commit_sha'] for comment in all_comments}

    while url:
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            commits = response.json()

            for commit in tqdm(commits, desc="Fetching commit comments"):
                if commit['sha'] in existing_commit_shas:
                    continue  # Skip already fetched commits
                comments_url = commit.get('comments_url')
                if comments_url:
                    comments_response = requests.get(comments_url, headers=HEADERS)
                    comments_response.raise_for_status()
                    comments = comments_response.json()
                    for comment in comments:
                        all_comments.append({
                            'commit_sha': commit['sha'],
                            'comment_body': comment['body'],
                            'author': comment['user']['login'],
                            'created_at': comment['created_at']
                        })

            # Save results incrementally
            with open(results_file, 'w') as f:
                json.dump(all_comments, f, indent=4)

            url = response.links.get('next', {}).get('url')
            time.sleep(API_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commit comments: {e}")
            break

    print(f"Saved commit comments to {results_file}")

# Fetch issue comments
def fetch_issue_comments(owner, repo, results_file):
    all_comments = []
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            all_comments = json.load(f)

    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    params = {'state': 'all', 'since': START_DATE, 'until': END_DATE, 'per_page': 100}

    existing_issue_numbers = {comment['issue_number'] for comment in all_comments}

    while url:
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            issues = response.json()

            for issue in tqdm(issues, desc="Fetching issue comments"):
                if issue['number'] in existing_issue_numbers:
                    continue  # Skip already fetched issues
                if 'pull_request' in issue:  # Skip pull requests
                    continue
                comments_url = issue.get('comments_url')
                if comments_url:
                    comments_response = requests.get(comments_url, headers=HEADERS)
                    comments_response.raise_for_status()
                    comments = comments_response.json()
                    for comment in comments:
                        all_comments.append({
                            'issue_number': issue['number'],
                            'comment_body': comment['body'],
                            'author': comment['user']['login'],
                            'created_at': comment['created_at']
                        })

            # Save results incrementally
            with open(results_file, 'w') as f:
                json.dump(all_comments, f, indent=4)

            url = response.links.get('next', {}).get('url')
            time.sleep(API_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issue comments: {e}")
            break

    print(f"Saved issue comments to {results_file}")

# Main script
if __name__ == "__main__":
    for repo in REPOSITORIES:
        owner, repo_name = repo['owner'], repo['repo']

        print(f"Fetching commit comments for {owner}/{repo_name}...")
        fetch_commit_comments(owner, repo_name, f'{repo_name}_commit_comments_2022.json')

        print(f"Fetching issue comments for {owner}/{repo_name}...")
        fetch_issue_comments(owner, repo_name, f'{repo_name}_issue_comments_2022.json')

    print("Data collection complete.")
