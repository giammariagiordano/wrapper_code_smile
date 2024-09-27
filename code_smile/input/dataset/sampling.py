import github
from github import Github
from github import Auth
import pandas as pd
#apply mods to niche csv adding contributors and age columns


def split_dataset():
    df = pd.read_csv("NICHE_extended.csv")
    df_yes = df[df["Engineered ML Project"] == 'Y']
    df_no = df[df["Engineered ML Project"] == 'N']
    df_yes.to_csv("NICHE_yes.csv",index=False)
    df_no.to_csv("NICHE_no.csv",index=False)


def filter_dataset(filename):
    df = pd.read_csv(filename)
    out_file_name = filename.split(".")[0]+"_filtered_sample.csv"
    df = df[df["Stars"] > 300]
    df = df[df["Commits"] > 300]
    df = df[df["Lines of Code"] > 9000]
    df = df[df["Contributors"] > 4]
    df = df[df["Age"] > 730]

    df.to_csv(out_file_name,index=False)

def edit_dataset(g):
    df = pd.read_csv("NICHE.csv")
    df["Contributors"] = 0
    df["Age"] = 0
    for index, row in df.iterrows():
        repo_url = row["GitHub Repo"]
        try:
            age,cont = get_repo_info(g,repo_url)
            df.at[index, "Contributors"] = cont
            df.at[index, "Age"] = age.days
        except github.GithubException:
            print("GithubException on repo: "+repo_url)
            continue

    df.to_csv("NICHE_extended.csv",index=False)

def get_repo_info(g,repo_url):

    repo = g.get_repo(repo_url)
    cont = repo.get_contributors().totalCount
    initial_commit = repo.created_at
    last_commit = repo.updated_at
    age = last_commit - initial_commit
    return age,cont

def setup():
    auth = Auth.Token("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")
    g = Github(auth=auth)
    return g

if __name__ == "__main__":
    filter_dataset("NICHE_no.csv")
    filter_dataset("NICHE_yes.csv")




