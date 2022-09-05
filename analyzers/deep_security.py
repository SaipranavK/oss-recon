import os
import shutil
import subprocess
import json

import GlobalConfigs as gc
from DataManager import create_data_dir, delete_tmp

def security_analyzer(repo_git_urls, clone_parent_dir):
    print("### DEEP SECURITY ANALYZER ###")
    repo_security_analysis = {}    
    deleteTmp = True
    for repo in repo_git_urls:
        print("Running analysis on " + repo + ".....", end="")
        repo_git_url = repo_git_urls[repo]
        owasp_dc_out = create_data_dir("tmp/security/" + repo + "/", config="OW")
        owasp_dc_src = clone_parent_dir + repo
        
        owasp_dc_abs_path = os.path.abspath("analyzers/resources/dependency-check/bin/dependency-check.sh")
        cmd = "sh " + owasp_dc_abs_path + " --enableExperimental"
        cmd += " --project " + repo
        cmd += " --scan " + owasp_dc_src
        cmd += " --out " + owasp_dc_out
        cmd += " --format HTML"
        cmd += " --format JSON"
        print("Executing cmd: ", cmd)
        if gc.check_compliance:
            if gc.cvss_limit > -1:
                cmd += " --failOnCVSS " + str(gc.cvss_limit)
         
        owasp_dc = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if owasp_dc.returncode != 0:
            print("Analysis failed")
            print(owasp_dc.stderr.decode('utf-8'))
            repo_security_analysis[repo] = {"vulnerability_count": 0, "CVSS_check": "Failed"}
        else:
            json_out = {"message": "Something went wrong while loading JSON for " + repo}    
            with open(owasp_dc_out + "dependency-check-report.json") as json_str:
                json_out = json.loads(json_str.read())
                vulnerability_count = 0
                
                for dependency in json_out["dependencies"]:
                    if 'vulnerabilities' in dependency:
                        vulnerability_count += len(dependency["vulnerabilities"])
                json_out["vulnerability_count"] = vulnerability_count
                if gc.check_compliance:
                    if owasp_dc.returncode == 0:
                        json_out["CVSS_check"] = "Passed"
                    else:
                        json_out["CVSS_check"] = "Failed"
                        
            repo_security_analysis[repo] = json_out     
        print("done")
        
    print("Completed security analysis")
    print("-"*50)
    return repo_security_analysis    
        
        
        