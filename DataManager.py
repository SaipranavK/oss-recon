import glob
import os
from pathlib import Path
import shutil
import datetime
import json
import csv

import GlobalConfigs as gc

###### Create directory to store data ######
def create_data_dir(data_dir, config = "W"):
    created_dir = ""
    try:
        Path(data_dir).mkdir(parents = True)
        created_dir = data_dir
    
    except:
        if config == "OW" or gc.is_skip_purge:
            created_dir = data_dir
            
        else:
            date = datetime.datetime.now()
            date_str = str(date).replace(" ","-")
            date_str = "-" + date_str[:-7]
            
            Path(data_dir + date_str).mkdir(parents = True)
            created_dir = data_dir+date_str
    
    return created_dir

###### Delete a directory #######
def delete_data_dir(data_dir):
    try:
        shutil.rmtree(data_dir)
    except OSError as e:
        print("Error: %s : %s" % (data_dir, e.strerror))    
    return

###### Clear tmp directory ######
def delete_tmp():
    return delete_data_dir("tmp")

###### Export data ######
def export_data(folder, export_context, config="W"):
    export_dir = "."
    if config == "W":
        export_dir = create_data_dir(folder)
    else:
        export_dir = folder
        
    for data in export_context:
        with open(export_dir + "/" + data + ".json", 'w', encoding='utf-8') as f:
            if "date" in data: 
                print("using def str")
                json.dump(export_context[data], f, ensure_ascii=False, indent=4, default=str)
            else:
                json.dump(export_context[data], f, ensure_ascii=False, indent=4)

    return export_dir

###### Purge data ######
def purge_data(purge_list):
    print("### PURGING DATA ###")
    for data in purge_list:
        data = "analysis/" + gc.user + "/" + data + "*"
        print("Purging " + data)
        for directory in glob.glob(data):
            try:
                shutil.rmtree(directory)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
                exit(1)
    
    print("Purged all supplied data")
    print("-"*50)    


###### Custom dict sorter for generating commit classification csv ######
def custom_sorted(dict):
    sorted_dict = {}
    str_dict = {}
    int_dict = {}
    
    for key in dict:        
        try:
            key = int(key)
            int_dict[key] = dict[str(key)]
        except:
            str_dict[key] = dict[key]
            
    str_dict = sorted(str_dict.items())
    int_dict = sorted(int_dict.items())
    
    for key, val in str_dict:
        sorted_dict[key] = val
        
    for key, val in int_dict:
        sorted_dict[key] = val
    
    return sorted_dict
    
###### Generate commit classifications csv ######
def generate_commit_classification_csv(classification_data_dir, repo_data_dir, repo_release_tags_split):
    print("### GENERATING COMMIT CLASSIFICATION CSVs ###")
    repo_release_tags_split_copy = repo_release_tags_split.copy()            
    export_dir = create_data_dir("analysis/" + gc.user + "/commit_classification_sheets") 
    
    for repo in repo_release_tags_split_copy:
        print("Generating csv for " + repo)
        repo_classification_data_dir = classification_data_dir + repo + "/"
        
        versions = ["Variables/Versions"]
        variables = [
            ["Adaptive"], 
            ["Corrective"], 
            ["Perfective"], 
        ]
    
        custom_sorted_dict = custom_sorted(repo_release_tags_split_copy[repo])
        for release_branch in custom_sorted_dict:
            # reverse the releases order of the release_branch (oldest to newest)
            custom_sorted_dict[release_branch].reverse()
            
            if isinstance(release_branch, str) and "/" in release_branch:
                print("Poor versioning with release branch " + release_branch)
                alt_release_branch = release_branch.replace("/","-") 
                key_data_dir = classification_data_dir + "/" + repo + "/" + str(alt_release_branch)
            
            else:
                key_data_dir = classification_data_dir + "/" + repo + "/" + str(release_branch)          
                
            v_files = os.listdir(key_data_dir)

            for release in custom_sorted_dict[release_branch]:
                release_match = False
                versions.append(release)
                
                if isinstance(release, str) and "/" in release:
                    print("Poor versioning with release " + release)
                    release = release.replace("/","-") 
                
                for _file in v_files:
                    v_file_name = _file
                    v_file_name = v_file_name.split("}")
                    
                    if release == v_file_name[-1][:-5]:
                        release_match = True
                        with open(key_data_dir + "/" + _file) as json_file:
                            commit_dict = json.load(json_file)
                            if "a" in commit_dict:
                                variables[0].append(commit_dict["a"])
                            else:
                                variables[0].append(0)
                            if "c" in commit_dict:
                                variables[1].append(commit_dict["c"])
                            else:
                                variables[1].append(0)
                            if "p" in commit_dict:
                                variables[2].append(commit_dict["p"])
                            else:
                                variables[2].append(0)
                                         
                    if release_match:
                        break
                    
                if release_match == False:
                    print(release, "=> Initial release")
                    variables[0].append(0)
                    variables[1].append(0)
                    variables[2].append(0)
                    print("-")    
            
        file_name = export_dir + "/" + repo + ".csv"
        
        # writing to csv file 
        with open(file_name, 'w') as csvfile: 
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(versions) 
            csvwriter.writerows(variables)

        print(repo + " metric sheet completed")
        print("---")
    
    print("Completed all sheets")
    print("-"*50)
    return export_dir