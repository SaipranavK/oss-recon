import json 
import os
import GlobalConfigs as gc
import DataManager as dm
from datetime import datetime

def generate_reports(repo_git_urls):
    print("###### GENERATING REPORTS ######")
    analysis_dir = "analysis/" + gc.user
    reports_dir = dm.create_data_dir(analysis_dir + "/" + "reports", config="OW")
    
    base_html = ""
    with open("templates/report-template.html", "r") as html_txt:
        base_html = html_txt.read()
    
    meta_data = None
    with open(analysis_dir + "/repo_data/repo_meta_analysis.json") as meta:
        meta_data = json.load(meta)
    
    portability_data = None
    with open(analysis_dir + "/repo_data/repo_portability_analysis.json") as portability:
        portability_data = json.load(portability)
        
    reliability_data = None
    with open(analysis_dir + "/repo_data/repo_reliability_analysis.json") as reliability:
        reliability_data = json.load(reliability)
        
    usability_data = None
    with open(analysis_dir + "/repo_data/repo_usability_analysis.json") as usability:
        usability_data = json.load(usability)
    
    security_data = None
    with open(analysis_dir + "/repo_data/repo_security_analysis.json") as security:
        security_data = json.load(security)
            
    deep_security_data = None
    with open(analysis_dir + "/repo_data/repo_deep_security_analysis.json") as security:
        deep_security_data = json.load(security)
        
    legal_data = None
    with open(analysis_dir + "/repo_data/repo_legal_analysis.json") as legal:
        legal_data = json.load(legal)
        
    ghc_data = None
    with open(analysis_dir + "/repo_data/repo_ghc_analysis.json") as ghc:
        ghc_data = json.load(ghc)
    
    active_releases_data = None
    with open(analysis_dir + "/repo_data/repo_active_release_branches.json") as releases:
        active_releases_data = json.load(releases)
    
    commit_maturity_data = None
    with open(analysis_dir + "/repo_data/repo_commit_maturity.json") as maturity:
        commit_maturity_data = json.load(maturity)
    
    compliance_data = None
    if gc.check_compliance:
        with open(analysis_dir + "/repo_data/repo_compliance_check.json") as compliance:
            compliance_data = json.load(compliance)
        
    for repo in repo_git_urls: 
        print("Generating report for " + repo + ".....", end="")
        report_html = base_html
        
        ### Meta Analyzer ###    
        report_html = report_html.replace("{{repo_name}}", repo)
        report_html = report_html.replace("{{repo_owner}}", meta_data[repo]['owner'])
        report_html = report_html.replace("{{description}}", meta_data[repo]['description'])
        report_html = report_html.replace("{{topics}}", str(meta_data[repo]['topics'])[1:-1].replace("'", ""))
        report_html = report_html.replace("{{api_url}}", meta_data[repo]['api_url'])
        
        report_html = report_html.replace("{{stars}}", str(meta_data[repo]['stars']))
        report_html = report_html.replace("{{forks}}", str(meta_data[repo]['forks']))
        report_html = report_html.replace("{{watchers}}", str(meta_data[repo]['watchers'])) 
        report_html = report_html.replace("{{issues}}", str(meta_data[repo]['issues']))
        report_html = report_html.replace("{{last_updated}}", meta_data[repo]['updated_at'])
        
        created_on = meta_data[repo]['created_at']
        now = str(datetime.today().strftime('%Y-%m-%d'))
        d1 = datetime.strptime(created_on.split("T")[0], "%Y-%m-%d")
        d2 = datetime.strptime(now, "%Y-%m-%d")
        age = abs((d2 - d1).days)
        
        report_html = report_html.replace("{{age}}", str(age))
        
        ### Community analyzer ###
        report_html = report_html.replace("{{github_community_health}}", str(ghc_data[repo]["health_percentage"]))
        
        ### Reliability Analyzer ###
        report_html = report_html.replace("{{average_time_to_release}}", str(reliability_data[repo]["days_per_release"].split(".")[0]))
        
        ### Usability Analyzer ###
        report_html = report_html.replace("{{qa_count}}", usability_data[repo])
        
        ### Legal Analyzer ###
        report_html = report_html.replace("{{license_name}}", legal_data[repo]["license"]["name"])
        report_html = report_html.replace("{{license_url}}", legal_data[repo]["html_url"])
        report_html = report_html.replace("{{permissions}}", ", ".join(legal_data[repo]["permissions"]))
        report_html = report_html.replace("{{conditions}}", ", ".join(legal_data[repo]["conditions"]))
        report_html = report_html.replace("{{limitations}}", ", ".join(legal_data[repo]["limitations"]))
        
        ### Portability Analyzer ###
        programming_languages = ""
        for language, loc in portability_data[repo]["languages"].items():
            programming_languages += "<tbody><tr><td style='text-align: left;'>" + str(language) + "</td><td style='text-align: right;'>" + str(loc) + "</td></tr></tbody>"
        
        report_html = report_html.replace("{{programming_languages}}", programming_languages)
        
        ### Active releases ###
        report_html = report_html.replace("{{active_releases}}", ", ".join(active_releases_data[repo]))
        
        ### Commit maturity crossovers ###
        report_html = report_html.replace("{{cp_count}}", str(commit_maturity_data[repo]["corrective-perfective"]))
        report_html = report_html.replace("{{ca_count}}", str(commit_maturity_data[repo]["corrective-adaptive"]))
        report_html = report_html.replace("{{pa_count}}", str(commit_maturity_data[repo]["perfective-adaptive"]))
        
        ### Graphs ###
        recent_commit_activity = os.path.abspath(analysis_dir + "/graph_images/" + repo +  "-commit_activity.png")
        commit_maturity = os.path.abspath(analysis_dir + "/graph_images/" + repo +  "-commit_maturity.svg")
        commit_classification = os.path.abspath(analysis_dir + "/graph_images/" + repo +  ".png")
        
        report_html = report_html.replace("{{recent_commit_activity}}", recent_commit_activity)
        report_html = report_html.replace("{{commit_maturity}}", commit_maturity)
        report_html = report_html.replace("{{commit_classification}}", commit_classification)
        
        ### Security Analyzer ###
        # Move report from tmp/ to reports/
        if gc.reports_only == False and repo in deep_security_data:
            with open(reports_dir + "/" + repo + "-security-report.html", "w") as security_report:
                with open("tmp/security/"+ repo +"/dependency-check-report.html", "r") as tmp_dc_report:
                    security_report.write(tmp_dc_report.read())
        
        mitre_url = "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=" + repo        
        report_html = report_html.replace("{{vulnerability_count}}", str(len(security_data[repo]))) 
        report_html = report_html.replace("{{mitre_url}}", mitre_url)
        if repo in deep_security_data:
            report_html = report_html.replace("{{deep_vulnerability_count}}", str(deep_security_data[repo]["vulnerability_count"]))
            report_html = report_html.replace("{{deep_security_report_url}}", os.path.abspath(reports_dir + "/" + repo + "-security-report.html"))
        
        ### Compliance ###
        if compliance_data is None:
            legal_val = "N/A"
            community_val = "N/A"
            security_CVSS_val = "N/A"
            security_CVE_val = "N/A"
        else:
            if compliance_data[repo]["legal"] == "Passed":
                legal_val = "✅"
            else:
                legal_val = "❌"    
            if compliance_data[repo]["community"] == "Passed":
                community_val = "✅"
            else:
                community_val = "❌"
            if compliance_data[repo]["security"]["max_CVE_count"] == "Passed":
                security_CVE_val = "✅"
            else:
                security_CVE_val = "❌"
            if compliance_data[repo]["security"]["max_CVSS_limit"] == "Passed":
                security_CVSS_val = "✅"
            else:
                security_CVSS_val = "❌"
            
        report_html = report_html.replace("{{legal}}", legal_val)
        report_html = report_html.replace("{{community}}", community_val)
        report_html = report_html.replace("{{CVE}}", security_CVE_val)
        report_html = report_html.replace("{{CVSS}}", security_CVSS_val) 
        
        
        ### Export ###
        with open(reports_dir + "/" + repo + "-report.html", "w") as report:
            report.write(report_html)
            
        print("Done")
    print("Compeleted report generation")
    print("-"*50)