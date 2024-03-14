import json
from pathlib import Path

from token_getter import GitHubApp

import pytest


inputs = {
    "pem_path": "pem.txt",
    "app_id": "153667",
    "nwo": "VCTLabs/actions-app-token",
}

test_app = GitHubApp(inputs["pem_path"], inputs["app_id"], inputs["nwo"])


def test_inputs():
    assert inputs["pem_path"]
    assert inputs["app_id"]
    assert inputs["nwo"]


def test_get_jwt():
    res = test_app.get_jwt()
    print(f"jwt type is: {type(res)}")
    print(res)


# def test_get_install_id():
#     res = test_app.get_installation_id()
#     print(res)
