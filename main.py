import os
import shutil
import subprocess

import pandas as pd
import git
from pydriller import Repository


def get_all_directory_projects(project_path):
    projects = []
    for dir in os.listdir(project_path):
        if os.path.isdir(project_path + dir):
            projects.append(dir)
    return projects


def get_list_of_releases(repo):
    releases = []
    for commit in Repository(repo, only_releases=True).traverse_commits():
        releases.append(commit)
    return releases


def get_list_of_commits_between_two_releases(repo, initial_release, final_release):
    commits = []
    for commit in Repository(repo, from_commit=initial_release, to_commit=final_release).traverse_commits():
        commits.append(commit)
    return commits


def get_list_of_commits_between_two_releases_with_hash(repo, initial_release, final_release):
    commits = []
    for commit in Repository(repo, from_commit=initial_release, to_commit=final_release).traverse_commits():
        commits.append(commit.hash)
    return commits


def checkout_to_commit(project, commit):
    repo = git.Repo(project)
    repo.git.checkout(commit.hash,)
    print("Checkout to commit " + commit.hash + " successfully")


def run_code_smile(project,output_path):
    print(output_path)
    command = ["python3", "/Users/broke31/PycharmProjects/wrapper_code_smile/code_smile/controller/analyzer.py",
               "--input", project, "--output",
               output_path]
    print(subprocess.run(command))
    print("Code_smile executed successfully")




def analyze_commit_by_commit(project, commit_i, commit_j):
    commits = get_list_of_commits_between_two_releases(project, commit_i, commit_j)
    for commit in commits:
        os.rename(project,
                  project + "internal_commit" + "___" + commit + "___between_commits" + commit_i.hash +
                  "___" + commit_j.hash)

        checkout_to_commit(
            project + "internal_commit" + "___" + commit + "___between_commits" + commit_i.hash + "___"
            + commit_j.hash,
            commit)

        run_code_smile(
            project + "internal_commit" + "___" + commit + "___between_commits" + commit_i.hash + "___"
            + commit_j.hash)


def reorganize_output_code_smile(code_smile_dir_out):
    list_projects = os.listdir(code_smile_dir_out)
    for project in list_projects:
        parent_dir, commit = project.split('___')[0], project.split('___')[1]
        os.makedirs(code_smile_dir_out + parent_dir + "/", exist_ok=True)
        shutil.move(code_smile_dir_out + project, code_smile_dir_out + parent_dir + "/" + commit)


def check_and_save_differences(project):
    #code_smile_dir_out = "output/"
    os.makedirs("differences/" + project, exist_ok=True)
    path =  project
    list_of_commits = os.listdir(path)
    for i in range(len(list_of_commits) - 1):
        commit_i = list_of_commits[i]
        commit_j = list_of_commits[i + 1]
        df_i = pd.read_csv(path + commit_i + "/to_save.csv")
        df_j = pd.read_csv(path + commit_j + "/to_save.csv")
        df_only_i = df_i[~df_i.isin(df_j)].dropna()
        df_only_j = df_j[~df_j.isin(df_i)].dropna()
        df_only_i['commit'] = commit_i
        df_only_j['commit'] = commit_j
        smelliness_commit_i = df_i['smell'].sum()
        smelliness_commit_j = df_j['smell'].sum()
        if smelliness_commit_i > smelliness_commit_j:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Increase'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Decrease'
            analyze_commit_by_commit(project, commit_i, commit_j)
        elif smelliness_commit_i < smelliness_commit_j:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Decrease'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Increase'
            analyze_commit_by_commit(project, commit_i, commit_j)
        else:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Stable'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Stable'

        df_only_i.to_csv("differences/" + project + "/" + commit_i + "___" + commit_j + ".csv", index=False)
        df_only_j.to_csv("differences/" + project + "/" + commit_j + "___" + commit_i + ".csv", index=False)


def start_analysis(project_path,dir):
    output_dir_code_smile = "code_smile/output/projects_analysis/torchani/"
    print(project_path)

    list_of_releases = get_list_of_releases(project_path)
    for release in list_of_releases:
        os.rename(project_path, project_path + "___" + release.hash)
        checkout_to_commit(project_path + "___" + release.hash, release)
        run_code_smile(project_path + "___" + release.hash,output_dir_code_smile+dir+"___"+release.hash)
        print("Release " + release.hash + " analyzed")
   #reorganize_output_code_smile(output_dir_code_smile)
    check_and_save_differences(output_dir_code_smile)


if __name__ == '__main__':
    base_dir = "/Users/broke31/Desktop/test_dovidify/"
    list_dir = get_all_directory_projects(base_dir)
    print(list_dir)
    for dir in list_dir:
        start_analysis(base_dir+dir,dir)
