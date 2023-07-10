import os
import subprocess

import pandas as pd
import git
from pydriller import Repository
import logging


def get_all_directory_projects(project_path):
    projects = []
    for dir in os.listdir(project_path):
        if dir != ".DS_Store" and os.path.isdir(os.path.join(project_path, dir)):
            projects.append(dir)
    return projects


def get_list_of_releases(repo):
    releases = []
    for commit in Repository(repo, only_releases=True).traverse_commits():
        releases.append(commit)
    return releases


def get_hash_from_project_name(project):
    return project.split("___")[1]


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
    try:
        repo = git.Repo(project)
        repo.git.checkout(commit.hash)
        print("Checkout to commit " + commit.hash + " successfully")
        return True

    except:
        print("Error checking out commit " + commit.hash)
        return False


def run_code_smile(project, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = os.path.abspath(output_path) + "/"
    project = project + "\\"
    command = ["python", "C:\\Users\\pc\\Desktop\\wrapper_code_smile\\code_smile\\controller\\analyzer.py",
               "--input", project, "--output", output_path]
    p = subprocess.run(command)
    p.check_returncode()
    print("Code_smile executed successfully")


def analyze_commit_by_commit(path_with_releases, commit_i, commit_j, project, base_dir):
    path_without_release = os.path.dirname(path_with_releases)
    commit_i_without_proj_name = get_hash_from_project_name(commit_i)
    commit_j_without_proj_name = get_hash_from_project_name(commit_j)
    commits = get_list_of_commits_between_two_releases(base_dir + project, commit_i_without_proj_name,
                                                       commit_j_without_proj_name)
    project += "\\"
    for commit in commits:
        commit_path = path_without_release + "\\internal_commits\\" + "between_commits___from" + commit_i_without_proj_name + "___to" + commit_j_without_proj_name + "\\" + commit.hash + "\\"
        if not os.path.exists(commit_path):
            os.makedirs(commit_path)
            checkout_to_commit(base_dir + project, commit)
            run_code_smile(base_dir + project, commit_path)


def reorganize_output_code_smile(code_smile_dir_out):
    if not os.path.exists(code_smile_dir_out + "\\releases\\"):
        os.makedirs(code_smile_dir_out + "\\releases\\")

    list_directory = get_all_directory_projects(code_smile_dir_out)
    list_directory.remove("releases")
    for sub_project in list_directory:
        os.rename(code_smile_dir_out+"\\"+sub_project,code_smile_dir_out+"\\releases\\"+sub_project)


def get_project_name(project):
    return project.split("\\")[-2]


def check_and_save_differences(input_directory, project):
    project_name = get_project_name(project)
    differences_directory = "differences\\" + project_name + "\\"
    if not os.path.exists(differences_directory):
        os.makedirs(differences_directory)
    if not os.path.exists(project):
        os.makedirs(project)
    list_of_dirs = get_all_directory_projects(project)
    for i in range(len(list_of_dirs) - 1):
        commit_i = list_of_dirs[i]
        commit_j = list_of_dirs[i + 1]
        commit_i_only_sha = get_hash_from_project_name(commit_i)
        commit_j_only_sha = get_hash_from_project_name(commit_j)
        df_i = pd.read_csv(os.path.join(project, commit_i, "to_save.csv"))
        df_j = pd.read_csv(os.path.join(project, commit_j, "to_save.csv"))
        df_only_i = df_i[~df_i.isin(df_j)].dropna()
        df_only_j = df_j[~df_j.isin(df_i)].dropna()
        df_only_i['commit'] = commit_i
        df_only_j['commit'] = commit_j
        smelliness_commit_i = df_i['smell'].sum()
        smelliness_commit_j = df_j['smell'].sum()
        if smelliness_commit_i > smelliness_commit_j:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Increase'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Decrease'
            analyze_commit_by_commit(input_directory, commit_i_only_sha, commit_j_only_sha)
        elif smelliness_commit_i < smelliness_commit_j:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Decrease'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Increase'
            analyze_commit_by_commit(input_directory, commit_i_only_sha, commit_j_only_sha)
        else:
            df_only_i['smelliness___' + commit_i + "___" + commit_j] = 'Stable'
            df_only_j['smelliness___' + commit_i + "___" + commit_j] = 'Stable'

        df_only_i.to_csv(os.path.join(differences_directory, commit_i + "___" + commit_j + ".csv"), index=False)
        df_only_j.to_csv(os.path.join(differences_directory, commit_j + "___" + commit_i + ".csv"), index=False)


def estimate_smelliness_between_two_stable_versions(df1, df2):
    df1_dropped = df1.drop(columns=['filename'])
    df2_dropped = df2.drop(columns=['filename'])
    if df1_dropped.equals(df2_dropped):
        return "stable"
    else:
        if df1["smell"].sum() > df2["smell"].sum():
            return "increase"
        elif df1["smell"].sum() < df2["smell"].sum():
            return "decrease"
        else:
            return "different_smells_but_same_smelliness"


def start_analysis(project_path, dir,output_dir,base_dir):
    print("*******************Starting analysis of project " + dir + "*******************")
    output_dir_code_smile = "code_smile/output/projects_analysis/" + dir + "/"
    output_dir_code_smile = os.path.abspath(output_dir_code_smile) + "\\"
    list_of_releases = get_list_of_releases(project_path)
    for release in list_of_releases:
        project_path_and_hash = project_path + "___" + release.hash
        os.rename(project_path, project_path_and_hash)
        if checkout_to_commit(project_path_and_hash, release):
            dir_output = output_dir_code_smile + dir + "___" + release.hash
            run_code_smile(project_path_and_hash, dir_output)
            os.rename(project_path + "___" + release.hash, project_path)
            print("Release " + release.hash + " analyzed")
        else:
            print("Release " + release.hash + " not analyzed")
            os.rename(project_path + "___" + release.hash, project_path)

    # check_and_save_differences(project_path, output_dir_code_smile)
    reorganize_output_code_smile(output_dir+"\\"+dir)
    verify_project(output_dir,dir,base_dir)

    print("*******************Analysis of project " + dir + " finished*******************")


def verify_differencies(input_projects_analysis, base_dir):
    projects = get_all_directory_projects(input_projects_analysis)
    if not os.path.exists("log/differences.csv"):
        df = pd.DataFrame(columns=['project','status'])
        df.to_csv("log/differences.csv", index=False)
    df = pd.read_csv("log/differences.csv")
    for i in range(len(projects)):
        if projects[i] not in df['project'].values:
            verify_project(input_projects_analysis, projects[i],base_dir)
            df.iloc[i] = [projects[i], "done"]
            df.to_csv("log/differences.csv", index=False)
        else:
            print("Project " + projects[i] + " already analyzed")
def verify_project(input_projects_analysis, project_name,base_dir):
    list_releases = get_all_directory_projects(input_projects_analysis + "\\" + project_name + "\\releases")
    for j in range(len(list_releases) - 1):
        df_i = pd.read_csv(
            input_projects_analysis + "\\" + project_name + "\\releases\\" + list_releases[j] + "\\to_save.csv")
        df_j = pd.read_csv(
            input_projects_analysis + "\\" + project_name + "\\releases\\" + list_releases[j + 1] + "\\to_save.csv")
        if estimate_smelliness_between_two_stable_versions(df_i, df_j) != "stable":
            print("Project: " + project_name + " Release: " + list_releases[j] + " and " + list_releases[
                j + 1] + " are different")
            analyze_commit_by_commit(input_projects_analysis + "\\" + project_name + "\\releases", list_releases[j],
                                     list_releases[j + 1], project_name, base_dir)


if __name__ == '__main__':
    base_dir = "D:\\ai_code_smells\\machine_learning_projects\\a_test\\"
    output_dir ="C:\\Users\\pc\\Desktop\\wrapper_code_smile\\code_smile\\output\\projects_analysis"
    list_dir = get_all_directory_projects(base_dir)
    print(list_dir)
    for dir in list_dir:
        try:
            start_analysis(base_dir + dir, dir,output_dir)
        except:
            logging.basicConfig(filename='log/log.txt', level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s')
            logging.error("project: " + dir + "skipped")



