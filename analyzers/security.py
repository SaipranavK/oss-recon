# Source = https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=<repo>

import requests
import pandas as pd
import numpy as np
import json
import warnings
from lxml import html
from bs4 import BeautifulSoup
from RepoBrewer import get_repo_fullname

warnings.filterwarnings('ignore')
CVE_URL = "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword="
        
def security_analyzer(repo_git_urls):
    print("### SECURITY ANALYZER ###")
    repo_security_analysis = {}    
    for repo in repo_git_urls:
        repo_git_url = repo_git_urls[repo]
        keyword = get_repo_fullname(repo_git_url).split("/")[1]        
        req_url = CVE_URL + keyword
        print("Running analysis on " + repo + " by requesting information from cve_url = " + req_url + " .....", end="")
        
        response = requests.get(req_url)
        json_out = {"message": "Invalid response from cve_url = " + req_url}
        if(response.status_code==200):
            tree = html.fromstring(response.content)
            soup = BeautifulSoup(response.content, "html.parser")
            header = soup.head
            match_div = soup.html.find(id="TableWithRules")
            table_df = pd.read_html(match_div.prettify())
            dfs = pd.DataFrame(table_df[0])
            json_str = dfs.to_json(orient="records")
            json_out = json.loads(json_str)
            
        repo_security_analysis[repo] = json_out
        print("Done")
    print("Completed Security analysis")
    print("-"*50)
    return repo_security_analysis