"""Check Github if there is any open PR.
"""

import requests
import os

github_token = os.getenv("GITHUB_TOKEN", None)
branch_label = "naveen521kk:update"
headers = {"Authorization": github_token} if github_token is not None else {}
BASE_REPOS = ["msys2/MINGW-packages", "msys2/MSYS2-packages"]

API_URL = [f"https://api.github.com/repos/{i}/pulls" for i in BASE_REPOS]

update = False
for url in API_URL:
    con = requests.get(url, headers=headers)
    if con.status_code == 200:
        prs = con.json()
        for pr in prs:
            if pr["head"]["label"] == branch_label:
                break
        else:
            update = True
        if update is False:
            break
print(str(update).lower())
