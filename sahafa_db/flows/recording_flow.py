from prefect import flow, task
from typing import List
import httpx


@task(log_prints=True)
def get_stars(repo: str):
    """
    Fetches the number of stars for a given GitHub repository.
    
    Args:
        repo (str): The repository name in the format "owner/repo".
    
    Returns:
        None: Prints the star count to the console.
    """
    url = f"https://api.github.com/repos/{repo}"
    count = httpx.get(url).json()["stargazers_count"]
    print(f"{repo} has {count} stars!")


@flow(name="GitHub Stars")
def github_stars(repos: List[str]):
    """
    A flow that retrieves star counts for multiple GitHub repositories.
    
    Args:
        repos (List[str]): A list of repository names in the format "owner/repo".
    
    Returns:
        None: Executes the get_stars task for each repository.
    """
    for repo in repos:
        get_stars(repo) 


# run the flow!
if __name__=="__main__":
    github_stars(["PrefectHQ/Prefect"])