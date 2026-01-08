from github import Github
from urllib.parse import urlparse

class SetUpGithub:
    def __init__(self, github_token: str, repo_url: str):
        self.github_token = github_token
        self.repo_url = repo_url

    def _extract_repo_path(self, url: str) -> str:
        """
        Extracts 'username/repo' from 'https://github.com/username/repo.git'
        """
       
        parsed = urlparse(url)
        path = parsed.path.strip("/") 
        
       
        if path.endswith(".git"):
            path = path[:-4]
            
        return path

    def authenticate(self):
        self.github = Github(self.github_token)
    
        repo_path = self._extract_repo_path(self.repo_url)
        
        try:
            self.repo = self.github.get_repo(repo_path)
            print(f"Successfully accessed: {self.repo.full_name}")
            return self.repo
        except Exception as e:
            print(f"Error accessing repo '{repo_path}': {e}")
            raise e