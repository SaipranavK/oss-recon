import json

def check_compliance(repo_git_urls, compliance_manifest, data_path):
    print("### CHECKING COMPLAINCE ###")
    compliance = {}
    
    enableLegal = False
    enableSecurity = False
    enableCommunity = False
    
    license_requirement = None
    community_health_requirement = None
    security_CVSS_limit_requirement = None
    security_CVE_count_requirement = None
    
    legal_info = None
    security_info = None
    community_info = None
    
    if 'legal' in compliance_manifest:
        enableLegal = True
        with open(data_path + "/repo_legal_analysis.json") as legal_json:
            legal_info = json.load(legal_json)
        license_requirement = compliance_manifest["legal"]["license"]
        
    if 'security' in compliance_manifest:
        enableSecurity = True
        with open(data_path + "/repo_deep_security_analysis.json") as security_json:
            security_info = json.load(security_json)
        
        if compliance_manifest["security"]["max_CVSS_limit"] > -1:
            security_CVSS_limit_requirement = compliance_manifest["security"]["max_CVSS_limit"]
        if compliance_manifest["security"]["max_CVE_count"] > -1:
            security_CVE_count_requirement = compliance_manifest["security"]["max_CVE_count"]
            
    if 'ghc' in compliance_manifest:
        enableCommunity = True
        with open(data_path + "/repo_ghc_analysis.json") as community_json:
            community_info = json.load(community_json)
        community_health_requirement = compliance_manifest["community"]["min_ghc_percentage"]
        
    for repo in repo_git_urls:
        compliance[repo] = {}
        print("Running compliance check for " + repo + "...", end = "")
    
        if enableLegal and legal_info[repo]["license"]["key"] != license_requirement:
            compliance[repo]["legal"] = "Failed"
        else:
            compliance[repo]["legal"] = "Passed"
        
        if enableCommunity and community_info[repo]["health_percentage"] < community_health_requirement:
            compliance[repo]["community"] = "Failed"
        else:
            compliance[repo]["community"] = "Passed"
            
        if enableSecurity:
            compliance[repo]["security"] = {}
            if security_CVE_count_requirement is not None and repo in security_info and security_info[repo]["vulnerability_count"] > security_CVE_count_requirement:
                compliance[repo]["security"]["max_CVE_count"] = "Failed"
            else:
                compliance[repo]["security"]["max_CVE_count"] = "Passed"
            
            if security_CVSS_limit_requirement is not None and repo in security_info:
                compliance[repo]["security"]["max_CVSS_limit"] = security_info[repo]["CVSS_check"]
            else:
                compliance[repo]["security"]["max_CVSS_limit"] = ""
        
        print("Done")
    print("Compeleted compliance check")
    print("-"*50)
    return compliance    
            
            
        