import json
from GlobalConfigs import user
from DataManager import export_data

def group_repos(git_repo_urls):
    print("### GROUPING REPOS ###")
    meta_data = None
    repo_groups = {}
    with open("analysis/" + user + "/repo_data/repo_meta_analysis.json") as meta:
        meta_data = json.load(meta)
    
    repo_groups["very_popular"] = []
    repo_groups["popular"] = []
    repo_groups["growing"] = []
        
    for repo in git_repo_urls:
        print("Finding a group for repo " + repo + ".....", end="")
        if meta_data["stars"] >= 5000:
            repo_groups["very_popular"].append(repo)
        if meta_data["stars"] < 5000 and meta_data["stars"] >= 1000:
            repo_groups["popular"].append(repo)
        if meta_data["stars"] < 1000:
            repo_groups["growing"].append(repo)
        print("done")
    export_context = {
        "repo_groups": repo_groups
    }
    export_data("analysis/" + user + "/repo_data/", export_context)
    print("Completed grouping")
    print("-"*35)
    return