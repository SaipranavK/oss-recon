from pydriller import Repository, Git
from pathlib import Path
import json

import RepoBrewer as rb
import DataManager as dm
import utils as ut

###### Generate missing tag dates for repos ######
def generate_dates(path_to_repo, repo, tags, repo_ordered_release_dates):
    git = Git(path_to_repo)
    print("Generating dates for " + repo + "...", end = "")
    for tag in tags:
        release_date = git.get_commit_from_tag(tag).author_date
        repo_ordered_release_dates[repo][tag] = release_date
    
    print("Done")
    print("-"*50)

###### Get commits with driller ######
def get_commits_data(path_to_repo, repo_fullname, file_path, from_tag, to_tag):
    commits_data = []
    html_url = "https://github.com/" + repo_fullname  + "/compare/"+ from_tag +"..." + to_tag
    _file = None
    
    if isinstance(from_tag, str) and isinstance(to_tag, str) and ("/" in from_tag or "/" in to_tag):
        alt_from_tag = from_tag.replace("/", "-")
        alt_to_tag = to_tag.replace("/", "-")
        _file = file_path + "/" + alt_from_tag + "}" + alt_to_tag + ".json"
    else:
        _file = file_path + "/" + from_tag + "}" + to_tag + ".json"
                    
    print("Analyzing", from_tag, " -----> ", to_tag)
    
    for commit in Repository(path_to_repo = path_to_repo, from_tag = from_tag, to_tag = to_tag).traverse_commits():
        commit_map = {
            "SHA": commit.hash, 
            "date": commit.author_date, 
            "message": commit.msg,
        }
        
        # resource expensive data
        '''
        "insertions": commit.insertions,
        "deletions": commit.deletions,
        "files": commit.files,
        "dmm_unit_size": commit.dmm_unit_size,
        "dmm_unit_complexity": commit.dmm_unit_complexity,
        "dmm_unit_interfacing": commit.dmm_unit_interfacing
        '''
        
        commits_data.append(commit_map)
    
    # Something wrong with the tagging
    if len(commits_data) < 1:
        print("Ill-structured BASE HEAD. Trying with swap....")
        commits_data = []
        html_url = "https://github.com/" + repo_fullname  + "/compare/"+ to_tag +"..." + from_tag
        
        # try swapping from and to tag
        for commit in Repository(path_to_repo = path_to_repo, from_tag = to_tag, to_tag = from_tag).traverse_commits():
            commit_map = {
                "SHA": commit.hash, 
                "date": commit.author_date, 
                "message": commit.msg,
            }
            
            # resource expensive data
            '''
            "insertions": commit.insertions,
            "deletions": commit.deletions,
            "files": commit.files,
            "dmm_unit_size": commit.dmm_unit_size,
            "dmm_unit_complexity": commit.dmm_unit_complexity,
            "dmm_unit_interfacing": commit.dmm_unit_interfacing
            '''
            
            commits_data.append(commit_map)
            
        if len(commits_data) < 1:
            print("Invalid BASE HEAD")
            print("Verify at:", html_url)
            print("-"*50)
            return []
                   
    with open(_file, 'w', encoding='utf-8') as f:
        json.dump(commits_data, f, ensure_ascii=False, indent=4, default=str)
    
    print("File saved")    
    print("Total commits:", len(commits_data))
    print("Verify at:", html_url)
    print('-'*50)

###### Get bridge commits ######
def get_bridge_commits(prev_last_vmajor, prev_file_path, path_to_repo, repo_fullname, repo_release_tags_split, repo, release_branch, repo_ordered_release_dates, file_path):
    from_tag = None
    to_tag = None
        
    if prev_last_vmajor == None:
        prev_last_vmajor = repo_release_tags_split[repo][release_branch][-1]
        prev_file_path = file_path
    else:
        transition_vmajor = ut.get_next_key(prev_last_vmajor, repo_ordered_release_dates[repo])
        if transition_vmajor == None:
            print("Got last tags already...updating prev_v_major")
            prev_last_vmajor = repo_release_tags_split[repo][release_branch][-1]
            prev_file_path = file_path
        else:
            from_tag = transition_vmajor
            to_tag = prev_last_vmajor
    
    if from_tag != None and to_tag != None:        
        print("Getting the bridge commits between " + from_tag + "----->" + to_tag)
        get_commits_data(path_to_repo, repo_fullname, prev_file_path, from_tag, to_tag)
        prev_last_vmajor = repo_release_tags_split[repo][release_branch][-1]
        prev_file_path = file_path
        
    return [prev_last_vmajor, prev_file_path]

###### Get commits between releases of repos ######
def get_commits_between_releases_tags(clone_parent_dir, data_dir, repo_git_urls, repo_has_releases, repo_release_tags_split, repo_ordered_release_dates, repo_release_tags):
    print("### GETTING COMMITS BETWEEN RELEASES ###")
    for repo in repo_release_tags_split:
        repo_fullname = rb.get_repo_fullname(repo_git_urls[repo])
        path_to_repo = clone_parent_dir + "/" + repo_fullname.split('/')[1]
        has_releases = False
        prev_last_vmajor = None
        prev_file_path = None
        
        if repo_has_releases[repo]:
            has_releases = True
            
        else:
            generate_dates(path_to_repo, repo, repo_release_tags[repo], repo_ordered_release_dates)
            print("Ordering the releases by dates for " + repo)
            repo_ordered_release_dates[repo] = rb.order_releases_dates(repo_ordered_release_dates[repo]) 
                         
        for release_branch in repo_release_tags_split[repo]:
            file_dir = None
            alt_release_branch = None
        
            if isinstance(release_branch, str) and "/" in release_branch:
                print("Poor versioning with release branch " + release_branch)
                alt_release_branch = release_branch.replace("/","-") 
                file_dir = data_dir + "/" + repo + "/" + str(alt_release_branch)
            else:
                file_dir = data_dir + "/" + repo + "/" + str(release_branch)
            
            file_path = dm.create_data_dir(file_dir)
            size = len(repo_release_tags_split[repo][release_branch])-1
            
            for i in range(0, size):
                from_tag = repo_release_tags_split[repo][release_branch][i+1]
                to_tag = repo_release_tags_split[repo][release_branch][i]
                get_commits_data(path_to_repo, repo_fullname, file_path, from_tag, to_tag)
            
            # Get bridge commits      
            [prev_last_vmajor, prev_file_path] = get_bridge_commits(prev_last_vmajor, prev_file_path, path_to_repo, repo_fullname, repo_release_tags_split, repo, release_branch, repo_ordered_release_dates, file_path)
        
        print("Checking if missed any bridge commits")
        [prev_last_vmajor, prev_file_path] = get_bridge_commits(prev_last_vmajor, prev_file_path, path_to_repo, repo_fullname, repo_release_tags_split, repo, release_branch, repo_ordered_release_dates, file_path)
    
    print("Completed fetching commits")
    print("-"*50)

###### Get active release branches from the repository ######
def get_active_release_branches(repo_ordered_release_dates):
    print("### GETTING ACTIVE RELEASE BRANCHES ###")
    repo_active_release_branches = {}
    for repo in repo_ordered_release_dates:
        print("Finding active branches for " + repo + "....", end = "")
        active_releases = []
        
        for version in ut.take(10, repo_ordered_release_dates[repo]):
            v_major = ut.get_version_major(version)
            if v_major not in active_releases:
                active_releases.append(str(v_major))
                
        print("Done")
        repo_active_release_branches[repo] = active_releases
    print("Generated active releases data")
    print("-"*50)
    return repo_active_release_branches
                