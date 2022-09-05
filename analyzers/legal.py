import requests as req
import sys
import base64
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import GlobalConfigs as gc
import RepoBrewer as rb

###### Get license params ######
def get_repo_license_params(api_url):
    params_response = req.get(api_url)
    params_data = {}
    if params_response.status_code == 200:
        params_data = params_response.json()
    elif params_response.status_code == 404:
        print("Invalid API URL: " + api_url)
        exit(1)
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return params_data


###### Get license of the repository ######
def get_repo_license(api_url):
    license_response = req.get(api_url)
    license_data = {}
    if license_response.status_code == 200:
        license_data = license_response.json()
    elif license_response.status_code == 404:
        print("Invalid API URL: " + api_url)
        exit(1)
    else:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    return license_data

###### Legal analysis of the repository ######
def legal_analyzer(repo_git_urls):
    print("### LEGAL ANALYZER ###")
    repo_legal_analysis = {}
    for repo in repo_git_urls:
        print("Running analysis for " + repo + "...." , end = "")
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        api_url = gc.gh_api_base_url + repo_fullname
        
        legal_data = get_repo_license(api_url + "/license")
        if "license" in legal_data and "url" in legal_data["license"]:
            api_url = legal_data["license"]["url"]
            if api_url:
                license_params = get_repo_license_params(api_url)
            else:
                license_params = {
                    "permissions": "N/A",
                    "conditions": "N/A",
                    "limitations": "N/A"
                }

            permissions = license_params["permissions"]
            conditions = license_params["conditions"]
            limitations = license_params["limitations"]
            
            legal_data["content"] = base64.b64decode(legal_data["content"]).decode('utf-8')
            legal_data["permissions"] = permissions
            legal_data["conditions"] = conditions
            legal_data["limitations"] = limitations
            
        repo_legal_analysis[repo] = legal_data
        print("Done")
    print("Completed legal analysis")
    print("-"*50)
    
    return repo_legal_analysis
            
            
        
        
    
    