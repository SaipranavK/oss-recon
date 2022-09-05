import requests as req
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Fetch repository information from API ######
def get_repo_information(api_url):
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

###### Get the topics of the repositories ######
def get_repo_topics(api_url):
    topics_response = req.get(api_url, headers = gc.HEADERS)
    topics_data = {}
    if topics_response.status_code == 200:
        topics_data = topics_response.json()
    elif topics_response.status_code == 404:
        print("Invalid API URL: " + api_url)
        exit(1)
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return topics_data

###### Meta analysis of the repository ######
def meta_analyzer(repo_git_urls):
    print("### META ANALYZER ###")
    repo_meta_analysis = {}
    for repo in repo_git_urls:
        print("Running analysis for " + repo + "...", end = "")
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        api_url = gc.gh_api_base_url + repo_fullname
        
        repo_data = get_repo_information(api_url)
        topics_data = get_repo_topics(api_url + "/topics")

        [owner, repo_name] = repo_data['full_name'].split('/')
        description = repo_data['description']
        forks = repo_data['forks_count']
        stars = repo_data['stargazers_count']
        watchers = repo_data['subscribers_count']
        issues = repo_data['open_issues_count']
        created_at = repo_data['created_at']
        updated_at = repo_data['updated_at']
        pushed_at = repo_data['pushed_at']
        issues_url = gc.gh_html_base_url + repo_fullname + "/issues"
        topics = topics_data['names']
         
        context = {
            "owner": owner ,
            "repository_name": repo_name, 
            "api_url": api_url,
            "description": description,
            "topics": topics,
            "forks": forks,
            "stars": stars,
            "watchers": watchers,
            "issues": issues,
            "issues_url": issues_url,
            "created_at": created_at,
            "updated_at": updated_at,
            "pushed_at": pushed_at
        }
        repo_meta_analysis[repo] = context
        print("Done")
    print("Completed meta analysis")
    print("-"*50)
    
    return repo_meta_analysis