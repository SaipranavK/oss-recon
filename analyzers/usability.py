import requests as req
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Get the tags count of the repositories in SE ######
def get_repo_tags_se(api_url):
    se_response = req.get(api_url)
    se_data = {}
    if se_response.status_code == 200:
        se_data = se_response.json()
    elif se_response.status_code == 404:
        print("Invalid API URL: " + api_url)
        exit(1)
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return se_response

###### Usability analysis of the repos ######
def usability_analyzer(repo_git_urls):
    print("### USABILITY ANALYZER ###")
    repo_usability_analysis = {}
    for repo in repo_git_urls:
        print("Running analysis for " + repo + "...", end = "")
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        repo_name = repo_fullname.split('/')[1]
        api_url = gc.se_api_base_url + "tags?order=desc&sort=popular&inname=" + repo_name + "&site=stackoverflow"
        se_response = get_repo_tags_se(api_url)
        tags_count = 0
        if se_response.json()['items']:
            tags_count = se_response.json()['items'][0]['count']
        repo_usability_analysis[repo] = str(tags_count)  
        print("Done")
    print("Completed Usability analysis")
    print("-"*50)
    return repo_usability_analysis
        
        