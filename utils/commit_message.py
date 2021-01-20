import json
from updator.utils import get_repo_path
from pathlib import Path
from git import Repo
from git import Actor
import os
committer_email = os.getenv("AUTHOR_EMAIL","41898282+github-actions[bot]@users.noreply.github.com")
PACKAGES_PATH = Path(__file__).parent.resolve().parent / "packages" 
commit_message = []
for file in Path(PACKAGES_PATH).glob("*.json"):
    with open(file) as f:
        info = json.load(f)
    if "update" in info:
        if info["update"]:
            repo_path = get_repo_path()
            repo = Repo(repo_path)
            index = repo.index
            index.add(f'{info["name"]}/"PKGBUILD"')
            name = info["name"].replace("mingw-w64-","")
            commit_message = f'{name}:update to {info["version"]}'
            author = Actor("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")
            committer = Actor("Naveen", committer_email)
            index.commit(commit_message, author=author, committer=committer)

#message = "\n- " + "\n- ".join(commit_message)
#message = " ".join(commit_message)
#print(f"UPDATE {len(commit_message)}:{message}")