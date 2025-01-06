# GitHub Data Fetcher

## Overview
The **GitHub Data Fetcher** script automates the collection of governance and contribution data from specified GitHub repositories. It retrieves information about:

- Governance file changes (e.g., `README.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`)
- High-engagement issues (with more than 10 comments)
- Pull requests and associated comments

This data is consolidated into a JSON file for further analysis.

---

## Features
- **Clone Repositories Locally**: Ensures offline access to repository contents.
- **Fetch Governance Commits**: Tracks changes in key governance files.
- **High-Engagement Issue Analysis**: Captures issue discussions with significant activity.
- **Pull Request Analysis**: Gathers pull request details and their associated comments.
- **Customisable Time Range**: Specify the desired timeframe for data collection.

---

## Prerequisites

1. **Python**:
   - Ensure Python 3.7 or higher is installed.

2. **Git**:
   - Required for cloning repositories.

3. **GitHub Token**:
   - A personal access token with the following scopes:
     - `repo` (for private repositories)
     - `public_repo` (for public repositories)
     - `read:org` (if accessing organisation-level data)
   - Set the token as an environment variable:
     ```bash
     export GITHUB_TOKEN="your_personal_access_token"
     ```

---

## Installation

1. **Clone This Repository**:
   ```bash
   git clone https://github.com/yourusername/github-data-fetcher.git
   cd github-data-fetcher
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install required packages (if applicable):
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Set Up Environment Variable**:
   Ensure your GitHub token is set in the `GITHUB_TOKEN` environment variable.

2. **Run the Script**:
   ```bash
   python github_data_fetcher.py
   ```

3. **Outputs**:
   - Results will be saved to `istio_data.json` in the working directory.

---

## Configuration

- **Repositories**: Specify the repositories to analyse in the `REPOSITORIES` list.
- **Time Range**: Adjust `START_DATE` and `END_DATE` for the desired timeframe.
- **Governance Files**: Update the `GOVERNANCE_FILES` list as needed.

---

## Sample Output
A JSON file with data structured as:
```json
{
  "community_governance_commits": [
    {
      "file": "README.md",
      "commit_message": "Update governance documentation",
      "timestamp": "2022-09-01T12:00:00Z",
      "url": "https://github.com/istio/community/commit/abcd1234"
    }
  ],
  "istio_issues": [
    {
      "title": "Feature Request: Improve Documentation",
      "body": "Details about the feature request...",
      "url": "https://github.com/istio/istio/issues/1234",
      "created_at": "2022-06-01T10:00:00Z",
      "comments": [
        {
          "body": "Great idea!",
          "author": "user123",
          "created_at": "2022-06-02T08:00:00Z"
        }
      ]
    }
  ]
}
```

---

## Troubleshooting

1. **Rate Limits**:
   If you hit the GitHub API rate limit, the script will pause and retry after 60 seconds.

2. **Token Errors**:
   Ensure your GitHub token is valid and has the correct permissions.

3. **Cloning Issues**:
   Check your network connection and Git installation if repositories fail to clone.

---

## Contributing
Feel free to submit issues or pull requests to improve this script.

---

## License
This project is licensed under the GPL3 License. See the `LICENSE` file for details.

---

## Acknowledgements
Special thanks to the GitHub API for enabling programmatic access to repository data.
