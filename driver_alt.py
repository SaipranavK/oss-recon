# Imports and Globals
import os
import sys
import re
import argparse
import subprocess
import json 
import urllib.request
import shutil
import zipfile
import yaml

import DataManager as dm
import RepoBrewer as rb
import RepoDriller as rd
import CommitClassifier as cc
import GraphKit as gk
import GlobalConfigs as gc
import Reporter as rp
import Compliance as cp

from analyzers import meta, portability, legal, ghcommunity, usability, reliability, security, deep_security

purge_list = ["repo_clones", "repo_data", "repo_commit_classification", "commit_classification_sheets", "graph_images", "reports"]

###### Run Analyzers set ######
def run_analyzer_set(repo_git_urls, repo_ordered_release_dates, clone_parent_dir):
    repo_meta_analysis = meta.meta_analyzer(repo_git_urls)
    repo_portability_analysis = portability.portability_analyzer(repo_git_urls)
    repo_legal_analysis = legal.legal_analyzer(repo_git_urls)
    repo_ghc_analysis = ghcommunity.ghcommunity_analyzer(repo_git_urls)
    repo_usability_analysis = usability.usability_analyzer(repo_git_urls)
    repo_reliability_analysis = reliability.reliability_analyzer(repo_git_urls, repo_ordered_release_dates)
    repo_security_analysis = security.security_analyzer(repo_git_urls)
    repo_deep_security_analysis = deep_security.security_analyzer(repo_git_urls, clone_parent_dir)
    return [repo_meta_analysis, repo_portability_analysis, repo_legal_analysis, repo_ghc_analysis, repo_usability_analysis, repo_reliability_analysis, repo_security_analysis, repo_deep_security_analysis] 


###### Repo Data extraction pipeline/flow ######
def repoDataPipeline(repo_git_urls):
    # Clone the repositories
    clone_parent_dir = rb.clone_repo(repo_git_urls)
    # Generate repo version data
    [repo_releases, repo_has_releases] = rb.fetch_repo_version_data(repo_git_urls)
    # Package tags and dates
    [repo_release_tags, repo_release_dates] = rb.tag_date_packing(repo_releases, repo_has_releases)
    # Split build branches and get repos with parallel releases
    repo_release_tags_split = rb.split_build_branches(repo_release_tags)    
    # Produce release dates
    repo_ordered_release_dates = rb.produce_release_dates(repo_has_releases, repo_release_dates, repo_release_tags ,repo_release_tags_split)
    
    # Export generated data
    export_context = {
        "repo_git_urls": repo_git_urls,
        "repo_has_releases": repo_has_releases, 
        "repo_release_tags": repo_release_tags , 
        "repo_release_tags_split": repo_release_tags_split,
        
    }
    repo_data_dir = dm.export_data("analysis/" + gc.user + "/repo_data", export_context)
 
    # Get commits between each release
    rd.get_commits_between_releases_tags(
        clone_parent_dir,
        repo_data_dir,
        repo_git_urls,
        repo_has_releases,
        repo_release_tags_split,
        repo_ordered_release_dates,
        repo_release_tags
    )    
    
    # Identify if the repo has parallel release
    repo_has_parallel_releases = rb.find_if_parallel_releases(repo_ordered_release_dates)
    # Get active release branches
    repo_active_release_branches = rd.get_active_release_branches(repo_ordered_release_dates)
    # Run analyzers set
    [repo_meta_analysis, repo_portability_analysis, repo_legal_analysis, repo_ghc_analysis, repo_usability_analysis, repo_reliability_analysis, repo_security_analysis, repo_deep_security_analysis] = run_analyzer_set(repo_git_urls, repo_ordered_release_dates, clone_parent_dir)
    
    # Export updated data in repo data
    export_context = {
        "repo_has_parallel_releases": repo_has_parallel_releases,
        "repo_ordered_release_dates": repo_ordered_release_dates,
        "repo_active_release_branches": repo_active_release_branches,
        "repo_meta_analysis": repo_meta_analysis,
        "repo_portability_analysis": repo_portability_analysis,
        "repo_legal_analysis": repo_legal_analysis,
        "repo_ghc_analysis": repo_ghc_analysis,
        "repo_usability_analysis": repo_usability_analysis,
        "repo_reliability_analysis": repo_reliability_analysis,
        "repo_security_analysis": repo_security_analysis,
        "repo_deep_security_analysis": repo_deep_security_analysis
    }
    repo_data_dir = dm.export_data(repo_data_dir, export_context, config = "OW")
   
    return [repo_data_dir, repo_release_tags_split, repo_has_parallel_releases]

###### Perform all steps without skips ######
def all_steps(repo_git_urls):
    # Purge data
    dm.purge_data(purge_list)
    # Extract repo data with data extraction pipeline
    [repo_data_dir, repo_release_tags_split, repo_has_parallel_releases] = repoDataPipeline(repo_git_urls)
    # call commit classifier
    classification_data_dir = cc.classify_commits(repo_data_dir, repo_git_urls)   
    # export the commit classifications as csv
    sheets_dir = dm.generate_commit_classification_csv(classification_data_dir, repo_data_dir, repo_release_tags_split)
    # graph the classification
    gk.plot_commit_classifications(sheets_dir)
    gk.plot_commit_activity(repo_git_urls)
    return

###### Perform steps with custom skips ######
def skip_steps(repo_git_urls, skip_list):
    cwd = os.getcwd()
    classification_data_dir = None
    repo_data_dir = None
    repo_release_tags_split = None
    sheets_dir = None
    
    if 'sheets' in skip_list and os.path.isdir("analysis/" +  gc.user + '/commit_classification_sheets'):
        sheets_dir = cwd + "/analysis/" + gc.user + "/commit_classification_sheets"
    
    elif 'extract' in skip_list and os.path.isdir("analysis/" + gc.user + '/repo_data'):
        repo_data_dir = cwd + "/analysis/" +  gc.user + "/repo_data"
        try:
            _file = repo_data_dir + "/repo_release_tags_split.json" 
            repo_release_tags_split = {}
            with open(_file) as json_file:
                repo_release_tags_split = json.load(json_file)
    
        except Exception as e:
            print("Something went wrong while skipping extraction. Using to default pipeline")
            print("Error message:" + e.message)
            all_steps(repo_git_urls)

    if 'classify' in skip_list and os.path.isdir("analysis/" + gc.user + '/repo_commit_classification'):
        classification_data_dir = cwd + "/analysis/" +  gc.user + "/repo_commit_classification"
        
    if skip_list == ['purge']:
        gc.is_skip_purge = True
        # Extract repo data with data extraction pipeline
        [repo_data_dir, repo_release_tags_split, repo_has_parallel_releases] = repoDataPipeline(repo_git_urls)
        # call commit classifier
        classification_data_dir = cc.classify_commits(repo_data_dir, repo_git_urls)   
        # export the commit classifications as csv
        sheets_dir = dm.generate_commit_classification_csv(classification_data_dir, repo_data_dir, repo_release_tags_split)
        # graph the classification
        gk.plot_commit_classifications(sheets_dir)
        gk.plot_commit_activity(repo_git_urls)
        return
    
    elif skip_list == ['purge', 'extract'] and repo_data_dir != None:
        # purge any previous classification and csv data
        purge_list = ["repo_commit_classification","commit_classification_sheets", "graph_images"]
        dm.purge_data(purge_list)
        
        # call commit classifier
        classification_data_dir = cc.classify_commits(repo_data_dir, repo_git_urls)   
        # export the commit classifications as csv
        sheets_dir = dm.generate_commit_classification_csv(classification_data_dir, repo_data_dir, repo_release_tags_split)
        # graph the classification
        gk.plot_commit_classifications(sheets_dir)
        gk.plot_commit_activity(repo_git_urls)
        return
    
    elif skip_list == ['purge', 'extract', 'classify'] and repo_data_dir != None and classification_data_dir != None and repo_release_tags_split != None:
        # purge any previous csv data
        purge_list = ["commit_classification_sheets", "graph_images" ]
        dm.purge_data(purge_list)
        
        # export the commit classifications as csv
        sheets_dir = dm.generate_commit_classification_csv(classification_data_dir, repo_data_dir, repo_release_tags_split)
        # graph the classification
        gk.plot_commit_classifications(sheets_dir)
        gk.plot_commit_activity(repo_git_urls)
        return
    
    elif skip_list == ['purge', 'extract', 'classify', 'sheets'] and sheets_dir != None:
        # graph the classification
        gk.plot_commit_classifications(sheets_dir)
        gk.plot_commit_activity(repo_git_urls)
        return
        
    else:
        print("Unable pass the required parameters for the requested function with skip list. Falling back to default pipeline with no step skips...")
        all_steps(repo_git_urls)
        return
     
        
def defaultAnalysisPipeline(repo_git_urls, skip_list = []):    
    if skip_list:
        return skip_steps(repo_git_urls, skip_list)
    else:
        return all_steps(repo_git_urls)
    
        
###### Check if the url is is a GitHub clone url ######
def is_github_repo_clone_url(repo_clone_url):
    pattern = r"https://github.com/.*.git"
    if re.match(pattern, repo_clone_url):
        return repo_clone_url
    else:
        raise argparse.ArgumentTypeError("Expected a GitHub clone URL")

###### Check if path is a valid file ######
def valid_file_path(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError("Expected a valid file path")

###### Parse Arguments ######
def parse_args(args):
    parser = argparse.ArgumentParser(description="GitHub repo analyzer")
    parser.add_argument("-r", "--repos", dest="all_repos_urls", nargs="+", required=False, type=is_github_repo_clone_url, help="GitHub repo clone urls")
    parser.add_argument("--check-compliance", dest="check_compliance", required=False, type=valid_file_path, help="Path to Compliance manifest file")
    parser.add_argument('--use-cache', dest="isCacheEnabled", required=False, default=False, action="store_true", help="Enable if you wish to use cached repo clones")
    parser.add_argument('--resolve-owaspdc', dest="resolve_deps", required=False, default=False, action="store_true", help="Resolve program dependencies on your first run")
    
    parser.add_argument("--reports-only", dest="reports_only", default=False, action="store_true")
    args = parser.parse_args(args)
    return args

def resolve_dependencies():
    check_owasp_cmd = "sh ./analyzers/resources/dependency-check/bin/dependency-check.sh --version"
    resolve_owasp_dc = subprocess.run([check_owasp_cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(resolve_owasp_dc)
    if resolve_owasp_dc.stderr:
        resources_dir = dm.create_data_dir("./analyzers/resources/", config="OW")
        print("Cannot locate OWASP DC locally. Fetching from GitHub...")
        
        with urllib.request.urlopen("https://github.com/jeremylong/DependencyCheck/releases/download/v6.2.2/dependency-check-6.2.2-release.zip") as response, open(resources_dir + "/dependency-check-6.2.2-release.zip", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        with zipfile.ZipFile(resources_dir + "/dependency-check-6.2.2-release.zip", 'r') as zip_ref:
                zip_ref.extractall(resources_dir)
        
        check_owasp_cmd = "sh " + resources_dir + "/dependency-check/bin/dependency-check.sh --version"         
        resolve_owasp_dc = subprocess.run([check_owasp_cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if resolve_owasp_dc.stderr:
            print("Couldn't get OWASP Dependency Checker. Try installing manually to resources folder")
            sys.exit(1)
    
    print("Resolved OWASPDC")
    return
    
###### Main ######
def main(args):
    args = parse_args(args)
    
    if args.resolve_deps:
        resolve_dependencies()
        return
    
    repo_git_urls = {}   
    for repo_url in args.all_repos_urls:
        key = rb.get_repo_fullname(repo_url).split("/")[1]
        repo_git_urls[key] = repo_url

    if args.isCacheEnabled:
        purge_list.pop(0)
        gc.use_cache = True
        
    if args.reports_only:
        gc.reports_only = True
        rp.generate_reports(repo_git_urls)
        return
    
    compliance_manifest = None
    if args.check_compliance is not None:
        gc.check_compliance = True
        compliance_manifest = yaml.safe_load(open(args.check_compliance))
        if 'security' in compliance_manifest and 'max_CVSS_limit' in compliance_manifest['security']:
            gc.cvss_limit = compliance_manifest['security']['max_CVSS_limit']
    
    print("### SCAN PARAMS ###")
    print(args)
    print(repo_git_urls)
    print("-"*50)
    
    # call default pipeline
    skip_list = []
    defaultAnalysisPipeline(repo_git_urls, skip_list = skip_list)
    
    # check compliance
    if gc.check_compliance:
        data_path = "analysis/" + gc.user + "/repo_data/"
        compliance_manifest = yaml.safe_load(open(args.check_compliance))
        compliance = cp.check_compliance(repo_git_urls, compliance_manifest, data_path)
        export_context = {
            "repo_compliance_check": compliance
        }
        dm.export_data(data_path, export_context, config="OW")
    
    # generate reports
    rp.generate_reports(repo_git_urls)
    
    # cleanup
    dm.delete_tmp()

if __name__ == "__main__":
    main(sys.argv[1:])
