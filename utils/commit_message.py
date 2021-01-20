import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.resolve().parent))
import json
import os

from git import Actor, Repo
from updator.utils import get_repo_path

committer_email = os.getenv(
    "AUTHOR_EMAIL", "41898282+github-actions[bot]@users.noreply.github.com"
)
PACKAGES_PATH = Path(__file__).parent.resolve().parent / "packages"
commit_message = []
for file in Path(PACKAGES_PATH).glob("*.json"):
    with open(file) as f:
        info = json.load(f)
    if "update" in info:
        if info["update"]:
            repo_path = get_repo_path(info)
            repo = Repo(repo_path)
            index = repo.index
            repo.git.add(f'{info["name"]}/PKGBUILD')
            name = info["name"].replace("mingw-w64-", "")
            commit_message = f'{name}: update to {info["version"]}'
            author = Actor(
                "github-actions[bot]",
                "41898282+github-actions[bot]@users.noreply.github.com",
            )
            committer = Actor("Naveen", committer_email)
            index.commit(commit_message, author=author, committer=committer)
            print(commit_message)

# message = "\n- " + "\n- ".join(commit_message)
# message = " ".join(commit_message)
# print(f"UPDATE {len(commit_message)}:{message}")
