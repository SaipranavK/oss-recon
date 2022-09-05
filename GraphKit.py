import os
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

import numpy as np
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt 
from matplotlib.pyplot import figure

import DataManager as dm
import GlobalConfigs as gc

###### Visualize the commit classifications and commit maturity ######
def plot_commit_classifications(sheets_dir):
    print("### PLOTING COMMIT CLASSIFICATIONS AND COMMIT MATURITY ###")
    graph_imgs_dir = dm.create_data_dir("analysis/" + gc.user + "/graph_images", config = "OW")
    sheets = os.listdir(sheets_dir)
    commit_maturity_json = {}
    
    for sheet in sheets:
        csv_dir = sheets_dir + "/" + sheet
        df = pd.read_csv(csv_dir)
        
        sheet_name = sheet[:-4]
        print("Generating for " + sheet_name + "....", end = "")
        
        # Commit classification graph
        cols = df.columns
        cols = cols[1:]
        df_np = df.to_numpy()
        
        fig  = go.Figure()
        fig.add_trace(go.Bar(
            x = cols,
            y = df_np[0][1:],
            name = "Adaptive",
            marker_color = 'blue',
            text = df_np[0][1:],
            textposition = 'auto'
        ))
        fig.add_trace(go.Bar(
            x = cols,
            y = df_np[1][1:],
            name = "Corrective",
            marker_color = 'red',
            text = df_np[1][1:],
            textposition = 'auto'
        ))
        fig.add_trace(go.Bar(
            x = cols,
            y = df_np[2][1:],
            name = "Perfective",
            marker_color = 'rgb(255,217,47)',
            text = df_np[2][1:],
            textposition = 'auto'
        ))
        
        fig.update_xaxes(title_text = 'Releases')
        fig.update_yaxes(title_text = 'Number of commits')
        fig.update_layout(
            barmode = 'stack', 
            title_text = sheet_name + " commit classification",
            xaxis_tickangle = -90,
            height = 2160, 
            width = 3840,
        )     
        _image = graph_imgs_dir + "/" + sheet_name + ".png"
        fig.write_image(_image)
        
        # Commit maturity graph
        version_list=[]
        for k in range(1, len(df.columns)):
            version_list.append(df.columns[k])
        
        adaptive = df.loc[0].tolist()
        adaptive.pop(0)
        adaptive = np.array(adaptive)
        corrective = df.loc[1].tolist()
        corrective.pop(0)
        corrective = np.array(corrective)
        perfective = df.loc[2].tolist()
        perfective.pop(0)
        perfective = np.array(perfective)
            
        plt.figure(figsize=(20,10))
        x = np.arange(0,len(adaptive)) 

        plt.title("Commit Maturity")
        plt.xlabel("Version") 
        plt.ylabel("Activity") 
        plt.plot(x, adaptive ,label="Adaptive")
        plt.plot(version_list,corrective, label="Corrective")
        plt.plot(version_list,perfective, label="Perfective")

        idx = np.argwhere(np.diff(np.sign(corrective - perfective))).flatten()
        idx1 = np.argwhere(np.diff(np.sign(corrective - adaptive))).flatten()
        idx2 = np.argwhere(np.diff(np.sign(perfective - adaptive))).flatten()
        plt.plot(x[idx], corrective[idx], 'ro')
        plt.plot(x[idx1], adaptive[idx1], 'bo')
        plt.plot(x[idx2], perfective[idx2], 'go')
        plt.title(
            "Commit Maturity\n" 
            + "Corrective and Perfective graph cross over times == " 
            + str(len(idx))
            + "\nCorrective and Adaptive graph cross over times == "
            + str(len(idx1))
            + "\nPerfective and Adaptive graph cross over times == "
            + str(len(idx2))
        )

        #print(idx)
        plt.legend(loc="upper right")

        plt.xticks(rotation=90)
        plt.show()
        
        commit_maturity_graphname = graph_imgs_dir + "/" + sheet_name + "-commit_maturity.svg"
        plt.savefig(commit_maturity_graphname, format="svg", facecolor='white')
        
        # This cross over is maturity 1
        print("Corrective and Perfective graph cross over times == " + str(len(idx)))
        print("Corrective and Adaptive graph cross over times == " + str(len(idx1)))
        print("Perfective and Adaptive graph cross over times == " + str(len(idx2)))

        M1 = len(idx)
        M2 = len(idx1)
        M3 = len(idx2)

        commit_maturity_json[sheet_name] = {}
        commit_maturity_json[sheet_name]["corrective-perfective"] = M1
        commit_maturity_json[sheet_name]["corrective-adaptive"] = M2
        commit_maturity_json[sheet_name]["perfective-adaptive"] = M3
        
        print("exporting image...Done")
    
    json_export_folder = "analysis/" + gc.user + "/repo_data"
    export_context = {
        "repo_commit_maturity": commit_maturity_json
    }
    dm.export_data(json_export_folder, export_context, config="OW")
    print("exporting maturity json...Done")    
    print("Completed plotting")
    print("-"*50)
    
###### Generate commit activity graph ######
def plot_commit_activity(repo_git_urls):
    print("###### PLOTTING COMMIT ACTIVITY ######")
    data_path = "analysis/" + gc.user + "/repo_data/repo_reliability_analysis.json"
    graph_imgs_dir = "analysis/" + gc.user + "/graph_images"
    reliability_data = None
    with open(data_path) as reliability_json:
        reliability_data = json.load(reliability_json)
    
    for repo in repo_git_urls:
        print("Plotting for repo " + repo + ".....", end="")
        commit_activity = reliability_data[repo]["commit_activity"]
        
        dates = []
        additions = []
        deletions = []
        
        for activity in commit_activity:
            dates.append(activity[0])
            additions.append(activity[1])
            deletions.append(activity[2])
        
        for i in range(len(dates)):
            dates[i] = datetime.utcfromtimestamp(dates[i]).strftime('%Y-%m-%d %H:%M:%S')
            
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x = dates, 
                y = additions,
                name='Additions',
                line=dict(color='rgb(255,217,47)', width=4)
            )
        )
        fig.add_trace(
            go.Scatter(
                x = dates, 
                y = deletions,
                name='Deletions',
                line=dict(color='red', width=4)
            )
        )
        fig.update_layout(
            title = "Recent commit activity",
            xaxis_title = "Date",
            yaxis_title = "Number of Deletions/Additions",
            xaxis_tickangle = -90,
            width = 1920,
            height = 1080
        )
        
        _image = graph_imgs_dir + "/" + repo + "-commit_activity.png"
        fig.write_image(_image)
        print("exporting image...Done")
    
    print("Completed plotting")
    print("-"*50)
        