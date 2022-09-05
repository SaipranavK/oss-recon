import pandas as pd
import json
import os
from pathlib import Path
import _pickle as cPickle
from collections import Counter

import DataManager as dm
import GlobalConfigs as gc

###### Prepare model for classification ######
def train_classification_model():
    # Read labelled data
    df = pd.read_csv("classifier_assets/geX_L.csv", sep=";")
    
    # Split data
    import numpy as np
    from sklearn.model_selection import train_test_split
    x = df['Message']
    y = df['label']
    x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.25,random_state=42)
    
    # Train the model
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.linear_model import SGDClassifier

    text_clf_svm = Pipeline([('vect', CountVectorizer(stop_words='english')),
                        ('tfidf', TfidfTransformer()),
                        ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',
                                                alpha=1e-3, random_state=42)),
    ])
    _ = text_clf_svm.fit(x_train, y_train)
    predicted_svm = text_clf_svm.predict(x_test)
    np.mean(predicted_svm == y_test)
    
    with open('classifier_assets/commit_classifier.pkl', 'wb') as fid:
        cPickle.dump(text_clf_svm, fid)
    
    return text_clf_svm

###### Classify commits into A,C,P ######
def classify_commits(repo_data_dir, repo_git_urls):
    print("### CLASSIFYING COMMITS ###")
    text_clf_svm = None
    classification_data_dir = dm.create_data_dir("analysis/" + gc.user + "/repo_commit_classification")
    
    # Try loading existing classification model
    try:
        with open('classifier_assets/commit_classifier.pkl', 'rb') as fid:
            text_clf_svm = cPickle.load(fid)
        print("Model loaded from local pickle.")
        
    # If doesn't exist then create the model
    except:
        print("Model does not exist. Creating....")
        text_clf_svm = train_classification_model()
    
    for repo in repo_git_urls:
        release_v_folder_dir = repo_data_dir + "/" + repo
        release_v_folders = os.listdir(release_v_folder_dir)
      
        for release_v in release_v_folders:
            rc_data_files_dir = release_v_folder_dir + "/" + release_v        
            if os.path.isdir(rc_data_files_dir):
                _file_path = dm.create_data_dir(classification_data_dir + "/" + repo + "/" + release_v)
                rc_data_files = os.listdir(rc_data_files_dir)
    
                for _file in rc_data_files:
                    commits_data = None
                    with open(rc_data_files_dir + "/" + _file) as json_file:
                        commits_data = json.load(json_file)
                    print(repo + "-->" + _file + " || commits: " + str(len(commits_data)))
                    message_list = []

                    for commit_map in commits_data:
                        message_list.append(commit_map['message'])
                    
                    commit_activity_count = None
                    
                    if len(message_list) < 1:
                        commit_activity_count = {'c': -1, 'p': -1, 'a': -1 }                    
                    else:
                        messages = pd.Series(message_list).astype(str)
                        classified_messages = text_clf_svm.predict(messages) 
                        commit_activity_count = Counter(classified_messages)
                        
                        print("Total:", len(classified_messages))
                        print(commit_activity_count)
                        print("-"*50)
                        
                        file_name = _file_path +"/c3-" + _file
                        with open(file_name, 'w', encoding='utf-8') as f:
                            json.dump(commit_activity_count, f, ensure_ascii=False, indent=4)
        
    
    return classification_data_dir            
                
                
                
                