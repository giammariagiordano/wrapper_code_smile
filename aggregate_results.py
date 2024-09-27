import subprocess

import pandas as pd
import os
import shutil

from git import GitCommandError
from pydriller import Repository, git
from pydriller.domain.commit import ModificationType

def reset_repo_to_head(repo):
    repo = git.Repo(repo)

    actual_path = os.getcwd()
    os.chdir(repo.working_dir)
    sys_command = "git remote show origin | findstr \"HEAD branch:\""

    branch_name = subprocess.check_output(sys_command, shell=True).decode("utf-8").split(":")[1].split("\n")[0].strip()
    print(branch_name)
    try:
        repo.git.reset('--hard', 'HEAD')
        repo.git.clean('-fd')
        repo.git.checkout(branch_name, force=True)
    except GitCommandError:
        os.chdir(actual_path)
        print("Error in reset_repo_to_head")
        raise GitCommandError("Error in reset_repo_to_head")
    os.chdir(actual_path)



def get_list_of_commits(repo):
    reset_repo_to_head(repo)
    commits = []
    for commit in Repository(repo).traverse_commits():
        commits.append(commit)
    return commits

def main():
    base_path = "output_analysis_test/"
    input_path = "F://input//projects22-06//"

    df = pd.DataFrame(columns=["repo","commit","commit_date","file","change_type","code_smell","line"])
    for repo in os.listdir(base_path):
        repo_path = os.path.join(input_path,repo.split("/")[-1])
        print(repo_path)
        commits = get_list_of_commits(os.path.join(base_path,repo_path))

        commits = [commit for commit in commits if os.path.exists(os.path.join(base_path,repo,commit.hash))]
        for commit in commits:
            path = os.path.join(base_path,repo,commit.hash,"output")
            for change_type in os.listdir(path):
                for file in os.listdir(os.path.join(path,change_type)):
                    if file.endswith("to_save.csv"):
                        continue
                    file_path = os.path.join(path,change_type,file)
                    file_df = pd.read_csv(file_path)
                    for index,row in file_df.iterrows():
                        df.loc[len(df)] = [repo,commit.hash,commit.author_date,row["filename"],change_type,row["smell_name"],row["line"]]

    df.to_csv("overall_analysis_results.csv",index=False)
    print(df)

if __name__ == "__main__":
    main()

