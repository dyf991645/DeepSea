
import pathlib
from github import Github
import urllib.request
import re
import logging
import os
import sys

class GH():
    def __init__(self, ghToken, update):
        self.token = ghToken
        self.update = update
        self.github = Github(self.token)

    def downloadReleaseAssets(self, module):
        
        if 'local' in module:
            return True
        
        fpath = f"./base/{module['repo']}/"
        if os.path.isdir(fpath) and not self.update:
            logging.info(f"[{module['repo']}] existed")
            return True
        
        pathlib.Path(fpath).mkdir(parents=True, exist_ok=True)
        
        if 'link' in module:
            logging.info(f"[{module['repo']}] Downloading: {module['link']}")
            req = urllib.request.Request(module['link'], headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            with open(fpath+f"{module['filename']}", 'wb') as f:
                f.write(response.read())
            return True
        try:
            ghRepo = self.github.get_repo(module["repo"])
        except:
            logging.exception(f"Unable to get: {module['repo']}")
            sys.exit(1)
            return
        
        releases = ghRepo.get_releases()
        if releases.totalCount == 0:
            logging.warning(f"No available release for: {module['repo']}")
            return
        ghLatestRelease = releases[0]

        for pattern in module["regex"]:
            found = False
            for asset in ghLatestRelease.get_assets():
                if re.search(pattern, asset.name):
                    found = True
                    logging.info(f"[{module['repo']}] Downloading: {asset.name}")
                    urllib.request.urlretrieve(asset.browser_download_url, f"{fpath}{asset.name}")
            if not found:
                logging.warning(f"{module['regex']} not found in {module['repo']}")
                sys.exit(1)
                return
        return True