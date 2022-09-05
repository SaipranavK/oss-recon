import requests as req
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Fetch GH community profile from API ######
def get_ghc_profile(api_url):
    repo_response = req.get(api_url)
    repo_data = {}
    if repo_response.status_code == 200:
        repo_data = repo_response.json()
    elif repo_response.status_code == 404:
        print("Invalid API URL: " + api_url)
        exit(1)
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return repo_data

###### GH community analysis of the repository ######
def ghcommunity_analyzer(repo_git_urls):
    print("### GH COMMUNITY ANALYZER ###")
    repo_ghc_analysis = {}
    for repo in repo_git_urls:
        print("Running analysis for " + repo + "...", end = "")
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        api_url = gc.gh_api_base_url + repo_fullname + "/community/profile"
        
        community_profile = get_ghc_profile(api_url)
        repo_ghc_analysis[repo] = community_profile
        print("Done")
    print("Completed GH community analysis")
    print("-"*50)
    
    return repo_ghc_analysis
        
        
        