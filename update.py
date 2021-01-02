from updator.github import GithubHandler
from pathlib import Path
from constants import PACKAGES_PATH
import json

for file in Path(PACKAGES_PATH).glob('*.json'):
    with open(file) as f:
        info = json.load(f)
    if info['type'] == 'github':
        a=GithubHandler(info)
        print(a.remote_version)
