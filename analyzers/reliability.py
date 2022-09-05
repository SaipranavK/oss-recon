import requests as req
import sys
from os import path
from datetime import datetime
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Get the status of the repository ######
def get_repo_status(api_url):
    print(api_url)
    status_response = req.get(api_url)
    status = {}
    if 'statuses' in status_response.json():
        status = status_response.json()["statuses"]
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return status

###### Get the traffic of the repository ######
def get_repo_traffic(api_url):
    traffic = {}
    traffic_clones_response = req.get(api_url+"/clones")
    traffic_views_response = req.get(api_url+"/views")
    if traffic_clones_response.status_code == 200:
        traffic["clones"] = traffic_clones_response.json()["uniques"]
    if traffic_views_response.status_code == 200:
        traffic["views"] = traffic_views_response.json()["uniques"]
    
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return traffic

###### Get the weekly aggregate of commit activity of the repository ######
def get_repo_commit_activity(api_url):
    commit_activity_response = req.get(api_url)
    commit_activity = {}
    if commit_activity_response.status_code == 200:
        commit_activity = commit_activity_response.json()
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return commit_activity


###### Reliability analyzer for the repositories #######
def reliability_analyzer(repo_git_urls, repo_ordered_release_dates):
    print("### RELIABILITY ANALYZER ###")
    repo_reliability_analysis = {}
    for repo in repo_git_urls:
        repo_reliability_analysis[repo] = {}
        print("Running analysis for " + repo + "...", end = "")
        
        repo_release_dates = repo_ordered_release_dates[repo]
        total_releases_count = len(repo_release_dates)
        total_release_gap = 0
        prev_release_date = None
        for release_date in repo_release_dates.values():
            if prev_release_date == None:
                prev_release_date = release_date
            else:
                current_release_date = release_date
                time_for_release = abs((current_release_date - prev_release_date).days)
                total_release_gap += time_for_release
                prev_release_date = current_release_date
        avg_release_time = int(total_release_gap / total_releases_count)
        repo_reliability_analysis[repo]["days_per_release"] = str(avg_release_time) + " Days/Release"
        
        # Get repo status
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        api_url = gc.gh_api_base_url + repo_fullname
        latest_tag = list(repo_ordered_release_dates[repo].keys())[0]
        status = get_repo_status(api_url + "/commits/" + latest_tag + "/status")
        repo_reliability_analysis[repo]["status"] = status
        
        # Get repo traffic - requires push access to repo 
        '''
        api_url = gc.gh_api_base_url + repo_fullname 
        traffic = get_repo_traffic(api_url + "/traffic/")
        repo_reliability_analysis[repo]["traffic"] = traffic
        '''
        
        # Get repo commit activity
        api_url = gc.gh_api_base_url + repo_fullname 
        commit_activity = get_repo_commit_activity(api_url + "/stats/code_frequency")
        repo_reliability_analysis[repo]["commit_activity"] = commit_activity
        
        print("Done")
    print("Completed Reliability analysis")
    print("-"*50)
    return repo_reliability_analysis    


        
                
            
