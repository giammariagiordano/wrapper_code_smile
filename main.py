import os
import subprocess
import pandas as pd
import git
from pydriller import Repository, ModificationType


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
    repo = git.Repo(project)
    repo.git.checkout(commit.hash)
    print("Checkout to commit " + commit.hash + " successfully")
    return True


def checkout_to_commit_modifications(commit):
    modified_list = []
    for modified_file in commit.modified_files:
        # filter is modifications is on python files
        if modified_file.filename.endswith(".py"):
            modified_list.append(modified_file.filename)
    return modified_list


def run_code_smile(project, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = os.path.abspath(output_path) + "/"
    project = project + "/"
    command = ["python", "code_smile/controller/analyzer.py",
               "--input", project, "--output", output_path]
    p = subprocess.run(command)
    p.check_returncode()
    print("Code_smile executed successfully")


def clear_temp():
    if os.path.exists("./temp/"):
        os.system("rm -rf ./temp/")


def create_modification_project(commit):
    clear_temp()
    os.makedirs("./temp/")
    os.makedirs("./temp/before_commit/")
    os.makedirs("./temp/commit/")
    added = []
    modified = []
    deleted = []
    for modified_file in commit.modified_files:
        if modified_file.filename.endswith(".py"):
            # get file
            if modified_file.change_type == ModificationType.DELETE:
                file = open("./temp/before_commit/" + modified_file.filename, "w")
                file.write(str(modified_file.source_code_before))
                file.close()
                deleted.append(modified_file.filename)
            elif modified_file.change_type == ModificationType.ADD or modified_file.change_type == ModificationType.MODIFY:
                file = open("./temp/commit/" + modified_file.filename, "w")
                file.write(str(modified_file.source_code))
                file.close()
                if modified_file.change_type == ModificationType.ADD:
                    added.append(modified_file.filename)
                elif modified_file.change_type == ModificationType.MODIFY:
                    modified.append(modified_file.filename)
                    file = open("./temp/before_commit/" + modified_file.filename, "w")
                    file.write(str(modified_file.source_code_before))
                    file.close()
    return './temp/commit', './temp/before_commit'


def analyze_commit_by_commit(path_with_releases, release_i, release_j, project, base_dir):
    path_without_release = os.path.dirname(path_with_releases)
    commit_i_without_proj_name = get_hash_from_project_name(release_i)
    commit_j_without_proj_name = get_hash_from_project_name(release_j)
    commits = get_list_of_commits_between_two_releases(base_dir + project, commit_i_without_proj_name,
                                                       commit_j_without_proj_name)
    project += "/"

    for commit in commits:
        commit_path = path_without_release + "/internal_commits/" + "between_commits___from" + commit_i_without_proj_name + "___to" + commit_j_without_proj_name + "/" + commit.hash + "/"
        if not os.path.exists(commit_path):
            modifications = checkout_to_commit_modifications(commit)
            if len(modifications) > 0:
                commit_project, before_commit_project = create_modification_project(commit)
                # it skips all modifications that are not related to python files
                os.makedirs(commit_path)
                run_code_smile(commit_project, commit_path)
                run_code_smile(before_commit_project, commit_path + "/before_commit/")
                analyze_differences(commit_path, commit)



def analyze_differences(commit_path, commit):
    before_commit_path = commit_path + "/before_commit/"
    before_overview = before_commit_path + "to_save.csv"
    before_overview = pd.read_csv(before_overview)
    after_overview = commit_path + "to_save.csv"
    after_overview = pd.read_csv(after_overview)
    difference = pd.DataFrame(columns=["file", "smell", "before", "after", "difference", "modification"])
    for index, row in after_overview.iterrows():
        file = row["filename"]
        function = row["function_name"]
        smell = row["smell_name"]
        after_value = row["smell"]
        # if is in after and not in before
        if before_overview.loc[before_overview["filename"] == file
                               and before_overview["function_name"] == function
                               and before_overview["smell_name"] == smell].empty:
            difference = difference.append(
                {"file": file, "smell": smell, "before": 0, "after": after_value, "difference": after_value,
                 "modification": commit.hash}, ignore_index=True)
        before_value = before_overview.loc[before_overview["filename"] == file
                                           and before_overview["function_name"] == function
                                           and before_overview["smell_name"] == smell]["smell"]
        if before_value != after_value:
            difference = difference.append({"file": file, "smell": smell, "before": before_value, "after": after_value,
                                            "difference": after_value - before_value, "modification": commit.hash},
                                           ignore_index=True)
    for index, row in before_overview.iterrows():
        file = row["filename"]
        function = row["function_name"]
        smell = row["smell_name"]
        before_value = row["smell"]
        # if is in before and not in after
        if after_overview.loc[after_overview["filename"] == file
                              and after_overview["function_name"] == function
                              and after_overview["smell_name"] == smell].empty:
            difference = difference.append(
                {"file": file,
                 "smell": smell,
                 "before": before_value,
                 "after": 0,
                 "difference": 0-before_value,
                 "modification": commit.hash},
                ignore_index=True)


def reorganize_output_code_smile(destination_path, code_smile_dir_out):
    if not os.path.exists(code_smile_dir_out + "/releases/"):
        os.makedirs(code_smile_dir_out + "/releases/")
    list_directory = get_all_directory_projects(code_smile_dir_out)
    list_directory.remove("releases")
    for sub_project in list_directory:
        os.rename(code_smile_dir_out + "/" + sub_project, code_smile_dir_out + "/releases/" + sub_project)
    os.rename(code_smile_dir_out, destination_path)

def get_project_name(project):
    return project.split("/")[-2]

def check_and_save_differences(input_directory, project):
    project_name = get_project_name(project)
    differences_directory = "differences/" + project_name + "/"
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

def start_analysis(project_path, dir, output_dir, base_dir):
    print("*******************Starting analysis of project " + dir + "*******************")
    output_dir_code_smile = "code_smile/output/projects_analysis/" + dir + "/"
    output_dir_code_smile = os.path.abspath(output_dir_code_smile) + "/"
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
    reorganize_output_code_smile(output_dir + "/" + dir, output_dir_code_smile)
    print("*******************Analysis of project " + dir + " finished*******************")

def verify_differencies(input_projects_analysis, base_dir):
    projects = get_all_directory_projects(input_projects_analysis)
    if not os.path.exists("log/differences.csv"):
        df = pd.DataFrame(columns=['project', 'status'])
        df.to_csv("log/differences.csv", index=False)
    df = pd.read_csv("log/differences.csv")
    for i in range(len(projects)):
        if projects[i] not in df['project'].values:
            verify_project(input_projects_analysis, projects[i], base_dir)
            df.iloc[i] = [projects[i], "done"]
            df.to_csv("log/differences.csv", index=False)
        else:
            print("Project " + projects[i] + " already analyzed")


def get_release_directory_list(project_path, output_path):
    # order releases by date
    list_of_releases = get_all_directory_projects(output_path)
    release_list = {}
    for release in list_of_releases:
        release_list[release.split("___")[1]] = ""

    for commit_hash in release_list:
        # get date of release with pydriller
        release_list[commit_hash] = get_date_of_release(project_path, commit_hash)
    # sort releases by date
    release_list = {k: v for k, v in sorted(release_list.items(), key=lambda item: item[1])}
    return release_list


def get_date_of_release(project_path, hash):
    repo = Repository(project_path, single=hash)
    for commit in repo.traverse_commits():
        if commit.hash == hash:
            return commit.committer_date


def sort_releases(base_path, output_path, list_releases):
    order = get_release_directory_list(base_path, output_path)
    sorted_list = []
    for key in order:
        for release in list_releases:
            if key == release.split("___")[1]:
                sorted_list.append(release)
    return sorted_list


def verify_project(input_projects_analysis, project_name, base_dir):
    list_releases = get_all_directory_projects(input_projects_analysis + "/" + project_name + "/releases")
    list_releases = sort_releases(base_dir + "/" + project_name,
                                  input_projects_analysis + "/" + project_name + "/releases", list_releases)
    for j in range(len(list_releases) - 1):
        df_i = pd.read_csv(
            input_projects_analysis + "/" + project_name + "/releases/" + list_releases[j] + "/to_save.csv")
        df_j = pd.read_csv(
            input_projects_analysis + "/" + project_name + "/releases/" + list_releases[j + 1] + "/to_save.csv")
        if estimate_smelliness_between_two_stable_versions(df_i, df_j) != "stable":
            print("Project: " + project_name + " Release: " + list_releases[j] + " and " + list_releases[
                j + 1] + " are different")
            analyze_commit_by_commit(input_projects_analysis + "/" + project_name + "/releases", list_releases[j],
                                     list_releases[j + 1], project_name, base_dir)


if __name__ == '__main__':
    base_dir = "code_smile/input/projects/"
    output_dir = "output/projects_analysis"
    list_dir = get_all_directory_projects(base_dir)
    for dir in list_dir:
        verify_project(output_dir, dir, base_dir)
