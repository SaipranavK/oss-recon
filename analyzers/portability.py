import requests as req
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Get the programming languages of the repository ######
def get_repo_languages(api_url):
    languages_response = req.get(api_url)
    languages = {}
    if languages_response.status_code == 200:
        languages = languages_response.json()
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return languages

###### Analyse portability of the repository ######
def portability_analyzer(repo_git_urls):
    print("### PORTABILITY ANALYSIS")
    repo_portability_analysis = {}
    for repo in repo_git_urls:
        print("Running portability analysis for " + repo + "...", end = "")
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        api_url = gc.gh_api_base_url + repo_fullname
        
        languages = get_repo_languages(api_url + "/languages")
        context = {
            "languages": languages
        }
        repo_portability_analysis[repo] = context
        print("Done")
    print("Completed Portability analysis")
    print("-"*50)

    return repo_portability_analysis
