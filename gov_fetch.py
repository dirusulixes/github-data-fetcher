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
    {'owner': 'istio', 'repo': 'community', 'files': [
        'ADMINS-FOR-ISTIO.md',
        'CONTRIBUTING.md',
        'ONBOARDING-TECH-TO-ISTIO.md',
        'README.md',
        'RELEASE_MANAGERS.md',
        'ROLES.md',
        'SUPPORT.md',
        'TECH-OVERSIGHT-COMMITTEE.md',
        'WORKING-GROUP-PROCESSES.md',
        'WORKING-GROUPS.md'
    ]},
    {'owner': 'istio', 'repo': 'istio', 'files': [
        'CODEOWNERS',
        'README.md'
    ]}
]

# Time range for 2022
START_DATE = '2022-01-01T00:00:00Z'
END_DATE = '2022-12-31T23:59:59Z'

# GitHub API rate limit delay (in seconds)
API_DELAY = 4

# Fetch governance file changes
def fetch_governance_changes(owner, repo, files, results_file):
    all_changes = []

    # Load existing results if the file exists
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                all_changes = json.load(f)
        except json.JSONDecodeError:
            print(f"Failed to parse {results_file}. Starting fresh.")

    for file in tqdm(files, desc=f"Fetching governance changes for {repo}"):
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        params = {'path': file, 'since': START_DATE, 'until': END_DATE, 'per_page': 100}

        while url:
            try:
                response = requests.get(url, headers=HEADERS, params=params)
                response.raise_for_status()
                commits = response.json()

                for commit in commits:
                    all_changes.append({
                        'file': file,
                        'commit_sha': commit['sha'],
                        'commit_message': commit['commit']['message'],
                        'author': commit['commit']['author']['name'],
                        'timestamp': commit['commit']['author']['date'],
                        'url': commit['html_url']
                    })

                # Save results incrementally
                with open(results_file, 'w') as f:
                    json.dump(all_changes, f, indent=4)

                url = response.links.get('next', {}).get('url')
                time.sleep(API_DELAY)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching governance changes for {file}: {e}")
                break

    print(f"Saved governance changes to {results_file}")

# Main script
if __name__ == "__main__":
    for repo in REPOSITORIES:
        owner, repo_name, files = repo['owner'], repo['repo'], repo['files']

        print(f"Fetching governance file changes for {owner}/{repo_name}...")
        fetch_governance_changes(owner, repo_name, files, f'{repo_name}_governance_changes_2022.json')

    print("Governance file data collection complete.")
