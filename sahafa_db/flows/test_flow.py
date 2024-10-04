from prefect import flow, task
from typing import List
import httpx
import boto3  # Added boto3 import
from prefect_aws import AwsCredentials
import os

aws_credentials_block = AwsCredentials.load("minio-local2")

@task(log_prints=True)
def get_stars(repo: str):
    """
    Fetches the number of stars for a given GitHub repository.
    
    Args:
        repo (str): The repository name in the format "owner/repo".
    
    Returns:
        None: Prints the star count to the console.
    """
    print("Getting stars")
    url = f"https://api.github.com/repos/{repo}"
    count = httpx.get(url).json()["stargazers_count"]
    print(f"{repo} has {count} stars!")

@task(log_prints=True)
def save_to_s3():
    """
    Saves a file named 'test.txt' with 'Hello World' text to the 'az' folder in the 'recordings' bucket.
    """
    print("Saving to S3")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_credentials_block.aws_access_key_id,
        aws_secret_access_key=aws_credentials_block.aws_secret_access_key.get_secret_value()
    )
    
    s3_client.put_object(
        Bucket='recordings',
        Key='az/test.txt',  # Save file in 'az' folder
        Body='Hello World'
    )
    print("File 'test.txt' with 'Hello World' text has been saved to 'az' folder in 'recordings' bucket.")

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
    save_to_s3()  # Added call to save_to_s3 task

# run the flow!
if __name__=="__main__":
    github_stars(["PrefectHQ/Prefect"])