import requests
import time
import os
import subprocess
import json
from datetime import datetime
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

# Time range
START_DATE = '2021-09-01T00:00:00Z'
END_DATE = '2023-09-30T23:59:59Z'

# File paths to track governance changes
GOVERNANCE_FILES = ['README.md', 'CONTRIBUTING.md', 'GOVERNANCE.md']

# GitHub API rate limit delay (in seconds)
API_DELAY = 2

# Helper function to fetch data from GitHub API
def fetch_github_data(url, params=None):
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 403:  # Rate limit hit
            print("Rate limit hit, sleeping for 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            response.raise_for_status()
        data = response.json()
        yield data
        url = response.links.get('next', {}).get('url')

# Fetch comments for pull requests
def fetch_pull_request_comments(owner, repo, pull_number):
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments'
    comments = []
    for data in fetch_github_data(url):
        for comment in data:
            comments.append({'body': comment['body'], 'author': comment['user']['login'], 'created_at': comment['created_at']})
    return comments

# Fetch pull requests from repositories
def fetch_pull_requests(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    params = {'state': 'all', 'since': START_DATE, 'per_page': 100}
    pull_requests = []
    for data in tqdm(fetch_github_data(url, params), desc=f"Fetching pull requests for {owner}/{repo}"):
        for pr in data:
            pr_comments = fetch_pull_request_comments(owner, repo, pr['number'])
            pull_requests.append({
                'title': pr['title'],
                'body': pr['body'],
                'url': pr['html_url'],
                'created_at': pr['created_at'],
                'comments': pr_comments,
                'labels': [label['name'] for label in pr['labels']],
                'milestone': pr['milestone']['title'] if pr['milestone'] else None
            })
        time.sleep(API_DELAY)
    return pull_requests

# Clone repositories locally
def clone_repositories():
    for repo in REPOSITORIES:
        owner = repo['owner']
        repo_name = repo['repo']
        repo_url = f'https://github.com/{owner}/{repo_name}.git'
        clone_path = os.path.join(os.getcwd(), repo_name)
        if not os.path.exists(clone_path):
            print(f'Cloning {repo_url} into {clone_path}')
            try:
                result = subprocess.run(['git', 'clone', repo_url, clone_path], check=True, capture_output=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error cloning repository {repo_name}: {e.stderr}")
        else:
            print(f'Repository {repo_name} already cloned at {clone_path}')

# Fetch commits for governance files
def fetch_governance_commits(owner, repo):
    commits = []
    for file in tqdm(GOVERNANCE_FILES, desc=f"Fetching commits for governance files in {owner}/{repo}"):
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        params = {'path': file, 'since': START_DATE, 'until': END_DATE}
        for data in fetch_github_data(url, params):
            for commit in data:
                commits.append({
                    'file': file,
                    'commit_message': commit['commit']['message'],
                    'timestamp': commit['commit']['author']['date'],
                    'url': commit['html_url']
                })
        time.sleep(API_DELAY)
    return commits

# Fetch comments for issues
def fetch_issue_comments(owner, repo, issue_number):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
    comments = []
    for data in fetch_github_data(url):
        for comment in data:
            comments.append({'body': comment['body'], 'author': comment['user']['login'], 'created_at': comment['created_at']})
    return comments

# Fetch issues from repositories
def fetch_issues(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    params = {'state': 'all', 'since': START_DATE, 'per_page': 100}
    issues = []
    for data in tqdm(fetch_github_data(url, params), desc=f"Fetching issues for {owner}/{repo}"):
        for issue in data:
            if 'comments' in issue and issue['comments'] > 10:
                issue_comments = fetch_issue_comments(owner, repo, issue['number'])
                issues.append({
                    'title': issue['title'],
                    'body': issue['body'],
                    'url': issue['html_url'],
                    'created_at': issue['created_at'],
                    'comments': issue_comments,
                    'labels': [label['name'] for label in issue['labels']],
                    'milestone': issue['milestone']['title'] if issue['milestone'] else None
                })
        time.sleep(API_DELAY)
    return issues

# Main script execution
def main():
    # Clone repositories locally
    clone_repositories()

    results = {}
    for repo in REPOSITORIES:
        owner, repo_name = repo['owner'], repo['repo']
        print(f"Fetching data for {owner}/{repo_name}...")

        # Fetch governance commits
        results[f'{repo_name}_governance_commits'] = fetch_governance_commits(owner, repo_name)

        # Fetch high-engagement issues
        results[f'{repo_name}_issues'] = fetch_issues(owner, repo_name)

        # Fetch pull requests
        results[f'{repo_name}_pull_requests'] = fetch_pull_requests(owner, repo_name)

    # Output results to JSON file
    with open('istio_data.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("Data collection complete. Results saved to 'istio_data.json'.")

if __name__ == "__main__":
    main()
