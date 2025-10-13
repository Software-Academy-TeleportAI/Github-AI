from github import Github

class InitModelAI:
    def __init__(self, api_key: str):
        self.api_key = api_key

class SetUpGithub:
    def __init__(self, github_token: str, repo_name: str):
        self.github_token = github_token
        self.repo_name = repo_name

    def authenticate(self):
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.repo_name)

        print(f"github token: {self.github}")
        print(f"repo name: {self.repo}")
        return self.repo