import json

from pathlib import Path

PACKAGES_PATH = Path(__file__).parent.resolve().parent / "packages" 
commit_message = []
for file in Path(PACKAGES_PATH).glob("*.json"):
    with open(file) as f:
        info = json.load(f)
    if "update" in info:
        if info["update"]:
            commit_message.append(info["name"])

print(f"::set-output name=commit_message::Update {' '.join(commit_message)}")