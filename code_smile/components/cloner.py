#Collect all projects repositories of NICHE dataset
#Please consider to use debug mode with debug_filter_repo function to avoid downloading a lot of data
#The debug mode is used to test the code and the experiment setup

import os
import pandas as pd
BASE_PATH = "../input/projects/"

def get_repo(repo_url):
    folder_url = repo_url.replace("/", "")
    build_path = BASE_PATH+"/"+folder_url

    build_path = os.path.abspath(build_path)
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    os.system("git clone " + "https://github.com/"+repo_url + " " + build_path)

def filter_repos(df,stars=200, commits=100):
    df = df[df["Engineered ML Project"] == 'Y']
    df = df[df["Stars"] > stars]
    df = df[df["Commits"] > commits]
    return df


def debug_filter_repo(df):
    #for first selection tries and setup the experiment, we try to select only projects that have a low size
    #to avoid downloading a lot of data
    df = df[df["Lines of Code"] < 10000]
    df = df.head(10)
    return df

def get_debug_projects():
    df = pd.read_csv("../input/dataset/NICHE.csv")
    df = filter_repos(df)
    df = debug_filter_repo(df)
    for repo_url in df["GitHub_Repo"]:
        get_repo(repo_url)

def get_projects():
    df = pd.read_csv("../input/dataset/NICHE.csv")
    df = filter_repos(df)
    for repo_url in df["GitHub_Repo"]:
        get_repo(repo_url)
def clean():
    if os.name == "nt":
        if os.path.exists(".\\projects"):
            os.system("rmdir /s /q .\\projects")
    else:
        if os.path.exists("./projects"):
            os.system("rm -r ./projects")

def setup():
    if os.name == "nt":
        if not os.path.exists(f"{BASE_PATH}/projects"):
            os.makedirs(f"{BASE_PATH}/projects")
    else:
        if not os.path.exists(f"{BASE_PATH}/projects"):
            os.makedirs(f"{BASE_PATH}/projects")


if __name__ == "__main__":
    clean()
    setup()
    get_projects()




