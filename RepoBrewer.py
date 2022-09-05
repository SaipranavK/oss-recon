import os
from pathlib import Path
import requests
import subprocess
import datetime
import utils as ut

import GlobalConfigs as gc

###### Get repo fullname ######
def get_repo_fullname(repo_git_url):
    repo_fullname = repo_git_url.split('.com/')[1]
    repo_fullname = repo_fullname.split('.git')[0]
    
    return repo_fullname

###### Clone repositories ######
def clone_repo(repo_git_urls):
    print("### REPO CLONING ###")
    Path("analysis/" + gc.user + "/repo_clones").mkdir(parents=True, exist_ok=True)
    cwd = os.getcwd()
    working_dir = cwd + "/analysis/" + gc.user + "/repo_clones/"
    
    for repo in repo_git_urls:
        if gc.use_cache and os.path.isdir(working_dir + repo):
            print("Using cached repo clone for " + repo)
        else:
            try:
                print("Cloning " + repo)
                subprocess.check_call(['git', 'clone', repo_git_urls[repo]], cwd = working_dir)
            except:
                print("Something went wrong")

        print("---")
        
    print("Cloning complete")
    print("-"*50)
    return working_dir
    
###### Get all tags of the repository ######
def get_all_tags(req_url, tags = [], page=1):
    req_url_pg = req_url + "?per_page=100&page=" + str(page)
    print("Fetching tags for repository from: " + req_url_pg)
    response = requests.get(req_url_pg)
    
    if response.status_code == 404:
        print("Invalid API URL: " + req_url)
        exit(1)
    elif response.status_code != 200:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)

    if len(response.json()) == 0:
        return tags
    
    tags.extend(response.json())
    return get_all_releases(req_url, tags, page+1)

###### Get all releases of the repository from Inception ###### 
def get_all_releases(req_url, releases = [], page = 1):
    req_url_pg = req_url + "?per_page=100&page=" + str(page)
    print("Fetching releases for repository from: " + req_url_pg)
    response = requests.get(req_url_pg)
    
    if response.status_code == 404:
        print("Invalid API URL: " + req_url)
        exit(1)
    elif response.status_code != 200:
        print('Max request limit for GitHub API reached. Cannot complete report')
        exit(1)
    
    if len(response.json()) == 0 or page == 10:
        return releases
    
    releases.extend(response.json())
    if page < 10:
        return get_all_releases(req_url, releases, page+1)

##### Generate repo tags/releases ######
def fetch_repo_version_data(repo_git_urls):
    print("### REPO VERSION DATA ###")
    repo_releases = {}
    repo_has_releases = {}
    
    for repo in repo_git_urls:
        repo_fullname = get_repo_fullname(repo_git_urls[repo])
        print("Generating repo version data for " + repo + " with fullname "+ repo_fullname)
        releases_req_url = gc.gh_api_base_url + repo_fullname + "/releases"
        releases = get_all_releases(releases_req_url, [])
        
        # repository has no formal releases other than tags
        if len(releases) == 0 or releases == []:
            print(repo + " has no formal releases other than tags. Fetching tags...")
            tags_req_url = gc.gh_api_base_url + repo_fullname + '/tags'
            tags = get_all_tags(tags_req_url, [])
            repo_releases[repo] = tags
            repo_has_releases[repo] = False  
        else:
            print(repo + " has formal releases.")
            repo_releases[repo] = releases
            repo_has_releases[repo] = True
        
        print('---')
    
    print("Done")
    print("-"*50)
    return [repo_releases, repo_has_releases]
            
###### Package release tags and dates ######
def tag_date_packing(repo_releases, repo_has_releases, duration = 0):
    print("### PACKING TAGS AND DATES ###")
    repo_release_tags = {}
    repo_release_dates = {}
    
    for repo in repo_releases:
        release_history = repo_releases[repo]
        print("Packing tags for " + repo + "....", end = "")
        tags = []
        release_dates = []
        current_release = None
        has_releases  = True
        
        if repo_has_releases[repo] == False:
            print(repo + " has no formal releases. Therefore cannot package dates or leverage the pick by minimum release gap functionality for this repository.")
            has_releases = False
        
        for release in release_history:
            if has_releases:
                if current_release == None:     
                    current_release_date = release["published_at"][:10]
                    current_release_date = datetime.datetime.strptime(current_release_date, "%Y-%m-%d").date()
                    tag = release["tag_name"]
                    if tag not in tags:
                        tags.append(tag)  
                        release_dates.append(current_release_date)  
                        
                else:
                    instance_release_date = release["published_at"][:10]
                    instance_release_date = datetime.datetime.strptime(instance_release_date, "%Y-%m-%d").date()
                    if abs((instance_release_date - current_release_date).days) >= duration:
                        tag = release["tag_name"]
                        if tag not in tags:
                            tags.append(tag)
                            current_release_date = instance_release_date
                            release_dates.append(instance_release_date)
             
            else:
                tag = release["name"]
                if tag not in tags:
                    tags.append(tag)
                
        repo_release_tags[repo] = tags
        repo_release_dates[repo] = release_dates
        print("Done")
        
    print("-"*50)
    return [repo_release_tags, repo_release_dates]

## split the build branches of the repository
def split_build_branches(repo_release_tags):
    print("### SPLITTING RELEASE BRANCHES ###")
    repo_release_tags_split = {}
    repo_release_tags_copy = repo_release_tags.copy()
    
    for repo in repo_release_tags_copy:
        print("Spliting release branches of " + repo + "....", end="")
        bk_store_data = repo_release_tags_copy[repo]
        repo_release_tags_split[repo] = {}   
        
        for version in bk_store_data:
            v_major = ut.get_version_major(version)                                      
            if str(v_major) not in repo_release_tags_split[repo]:
                repo_release_tags_split[repo][str(v_major)] = []
                
            repo_release_tags_split[repo][str(v_major)].append(version)
            
        print("Done")
    print('-'*50)
    return repo_release_tags_split

###### Order releases according to their release dates ######
def order_releases_dates(order_release_dates):
    new_repo_ordered_release_dates = {}
    for key, val in sorted(order_release_dates.items(), key=lambda p: p[1], reverse=True):
        new_repo_ordered_release_dates[key] = val
    
    return new_repo_ordered_release_dates

###### Process and generate packaged dates json #####
def produce_release_dates(repo_has_releases, repo_release_dates, repo_release_tags ,repo_release_tags_split):
    print("### PROCESSING RELEASE DATES ###")
    repo_ordered_release_dates = {}
    
    for repo in repo_release_tags_split:
        repo_ordered_release_dates[repo] = {}
        
        if repo_has_releases[repo] == False:
            print("Skipping dates packing for " + repo)
        else:
            print("Packing dates for " + repo + "....", end = "")
            for release_branch in repo_release_tags_split[repo]:
                for release in repo_release_tags_split[repo][release_branch]:
                    idx = repo_release_tags[repo].index(release)
                    release_date = repo_release_dates[repo][idx]
                    repo_ordered_release_dates[repo][release] = release_date
        print("Done")
        
    print("Ordering the releases by dates")
    for repo in repo_ordered_release_dates:
        repo_ordered_release_dates[repo] = order_releases_dates(repo_ordered_release_dates[repo]) 
    
    print('-'*50)
    return repo_ordered_release_dates

###### Identify if the repository has parallel releases ######
def find_if_parallel_releases(repo_ordered_release_dates):
    repo_has_parallel_releases = {}
    for repo in repo_ordered_release_dates: 
        int_v_major = None
        str_v_major = None
        prev_v_major = None
        repo_has_parallel_releases[repo] = False
        
        for tag in repo_ordered_release_dates[repo]:
            v_major = ut.get_version_major(tag)
               
            # check for parallel releases
            if prev_v_major != None:    
                if isinstance(v_major, str) and isinstance(prev_v_major, int):
                    if str_v_major == None:
                        str_v_major = v_major
                    else:
                        print(repo + ' has parallel releases')
                        is_parallel_release = True
                        repo_has_parallel_releases[repo] = True
                        break
                elif isinstance(v_major, int) and isinstance(prev_v_major, str):
                    if int_v_major == None:
                        int_v_major = v_major
                    else:
                        print(repo + ' has parallel releases')
                        is_parallel_release = True
                        repo_has_parallel_releases[repo] = True
                        break 
                elif isinstance(v_major, int) and isinstance(prev_v_major, int) and prev_v_major < v_major:
                    print(repo + ' has parallel releases')
                    is_parallel_release = True
                    repo_has_parallel_releases[repo] = True
                    break
                           
            prev_v_major = v_major
            
    return repo_has_parallel_releases
        