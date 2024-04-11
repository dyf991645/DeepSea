import os, sys, shutil, logging, re, urllib.request, pathlib, json
from github import Github

class GH():
    def __init__(self, ghToken, updateAll):
        self.token = ghToken
        self.updateAll = updateAll
        self.github = Github(self.token)

    def downloadReleaseAssets(self, module):
        
        fpath = f"./base/{module['repo']}/"
        update=self.updateAll
        
        existed = os.path.isdir(fpath)
        
        if 'local' in module and module['local']:
            shutil.copytree(f"./asset/{module['repo']}", f"./base/{module['repo']}", dirs_exist_ok=True)
            return True
        
        pathlib.Path(fpath).mkdir(parents=True, exist_ok=True)
        
        if 'link' in module:
            if existed and not update:
                logging.info(f"[{module['key']}] existed")
                return True
            
            logging.info(f"[{module['key']}] Downloading: {module['link']}")
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
        latestTag = ghLatestRelease.tag_name
        
        existedTag = module['tag']
        
        if not update and latestTag != existedTag:
            print(module['key']+":\n")
            needUpdate = input(f"update {module['repo']} from <{existedTag}> to <{latestTag}>?")
            if needUpdate == '':
                update = True
        
        need = latestTag != existedTag 
                
        if existed and (not need or not update):
            logging.info(f"[{module['key']}] existed")
            return True
        
        for pattern in module["regex"]:
            found = False
            for asset in ghLatestRelease.get_assets():
                if re.search(pattern, asset.name):
                    found = True
                    logging.info(f"[{module['key']}] Downloading: {asset.name}")
                    urllib.request.urlretrieve(asset.browser_download_url, f"{fpath}{asset.name}")
            if not found:
                logging.warning(f"{module['regex']} not found in {module['repo']}")
                sys.exit(1)
                return
        
        with open('./settings.json', 'r') as f:
            settings = json.load(f)
        settings["moduleList"][module["key"]]["tag"] = latestTag
        with open('./settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
            
        return True