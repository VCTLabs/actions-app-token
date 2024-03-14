import os
import time
from pathlib import Path

import requests
from jwt import JWT, jwk_from_pem
from github3 import GitHub


class GitHubApp(GitHub):
    """
    This is a small wrapper around the github3.py library

    Provides some convenience functions for testing purposes.
    """

    def __init__(self, pem_path, app_id, nwo):
        super().__init__()
        self.app_id = app_id
        self.path = Path(pem_path)
        if not self.path.is_file():
            raise ValueError(
                f"argument: `pem_path` must be a valid filename. {pem_path} was not found."
            )
        self.nwo = nwo

    def get_app(self):
        with open(str(self.path), "rb") as key_file:
            client = GitHub()
            client.login_as_app(private_key_pem=key_file.read(), app_id=self.app_id)
        return client

    def get_installation(self, installation_id):
        "login as app installation without requesting previously gathered data."
        with open(str(self.path), "rb") as key_file:
            client = GitHub()
            client.login_as_app_installation(
                private_key_pem=key_file.read(),
                app_id=self.app_id,
                installation_id=installation_id,
            )
        return client

    def get_test_installation_id(self):
        "Get a sample test_installation id."
        client = self.get_app()
        return next(client.app_installations()).id

    def get_test_installation(self):
        "login as app installation with the first installation_id retrieved."
        return self.get_installation(self.get_test_installation_id())

    def get_test_repo(self):
        repo = self.get_all_repos(self.get_test_installation_id())[0]
        appInstallation = self.get_test_installation()
        owner, name = repo["full_name"].split("/")
        return appInstallation.repository(owner, name)

    def get_test_issue(self):
        test_repo = self.get_test_repo()
        return next(test_repo.issues())

    def get_jwt(self):
        """
        This is needed to retrieve the installation access token (for debugging).

        Useful for debugging purposes.
        """
        now = self._now_int()
        payload = {"iat": now, "exp": now + (180), "iss": self.app_id}

        # Open PEM file
        with open(str(self.path), "rb") as pem_file:
            signing_key = jwk_from_pem(pem_file.read())

        jwt_instance = JWT()
        return jwt_instance.encode(payload, signing_key, alg="RS256")

    def get_installation_id(self):
        "https://developer.github.com/v3/apps/#find-repository-installation"

        owner, repo = self.nwo.split("/")

        url = f"https://api.github.com/repos/{owner}/{repo}/installation"

        headers = {
            "Authorization": f"Bearer {self.get_jwt()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.get(url=url, headers=headers, timeout=5)

        if response.status_code != 200:
            raise Exception(f"Status code : {response.status_code}, {response.json()}")
        return response.json()["id"]

    def get_installation_access_token(self, installation_id):
        "Get the installation access token for debugging."

        url = (
            f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        )
        headers = {
            "Authorization": f"Bearer {self.get_jwt()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.post(url=url, headers=headers, timeout=10)

        if response.status_code != 201:
            raise Exception(f"Status code : {response.status_code}, {response.json()}")
        return response.json()["token"]

    def _extract(self, d, keys):
        "extract selected keys from a dict."
        return dict((k, d[k]) for k in keys if k in d)

    def _now_int(self):
        return int(time.time())

    def get_all_repos(self, installation_id):
        """Get all repos that this installation has access to.

        Useful for testing and debugging.
        """
        url = "https://api.github.com/installation/repositories"
        headers = {
            "Authorization": f"token {self.get_installation_access_token(installation_id)}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.get(url=url, headers=headers, timeout=5)

        if response.status_code >= 400:
            raise Exception(f"Status code : {response.status_code}, {response.json()}")

        fields = ["name", "full_name", "id"]
        return [self._extract(x, fields) for x in response.json()["repositories"]]


if __name__ == "__main__":

    pem_path = "pem.txt"
    app_id = os.getenv("INPUT_APP_ID")
    nwo = os.getenv("GITHUB_REPOSITORY")
    env_file = os.getenv("GITHUB_ENV")

    assert pem_path, "Must supply input APP_PEM"
    assert app_id, "Must supply input APP_ID"
    assert nwo, "The environment variable GITHUB_REPOSITORY was not found."

    app = GitHubApp(pem_path=pem_path, app_id=app_id, nwo=nwo)
    inst_id = app.get_installation_id()
    token = app.get_installation_access_token(installation_id=inst_id)
    assert token, "Token not returned!"

    print(f"::add-mask::{token}")
    with open(env_file, "a") as myfile:
        myfile.write(f"app_token={token}\n")
