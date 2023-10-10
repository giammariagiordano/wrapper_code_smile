import os, shutil
import subprocess
import time

import git
from pydriller import Repository, ModificationType

def run_code_smile(project, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = os.path.abspath(output_path) + "/"
    project = project + "/"
    command = ["python", os.path.join("./","code_smile","controller","analyzer.py"),
               "--input", project, "--output", output_path]
    p = subprocess.run(command)
    p.check_returncode()
    print("Code_smile executed successfully")


def reset_repo_to_head(repo):
    repo = git.Repo(repo)
    repo.git.reset('--hard')
    repo.git.clean('-fd')
    actual_path = os.getcwd()
    os.chdir(repo.working_dir)

    sys_command = "git remote show origin | findstr \"HEAD branch:\""

    branch_name = subprocess.check_output(sys_command, shell=True).decode("utf-8").split(":")[1].split("\n")[0].strip()
    print(branch_name)
    repo.git.checkout(branch_name)
    os.chdir(actual_path)
def get_list_of_commits(repo):
    reset_repo_to_head(repo)
    commits = []
    for commit in Repository(repo).traverse_commits():
        commits.append(commit)
    return commits


def set_working_directories(repo,commit,replace=False):
    repo = git.Repo(repo)
    repo.git.checkout(commit.hash)
    repo_name = repo.working_dir.split("\\")[-1]
    if replace:
        if os.path.exists(os.path.join("output_analysis",f'{repo.working_dir}_analysis')):
            shutil.rmtree(os.path.join("output_analysis",f'{repo.working_dir}_analysis'))
    # get all_added_deleted and modified_files
    os.makedirs(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','input'))
    os.makedirs(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','output'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','input', 'added'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','input', 'deleted'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','input', 'modified'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','output', 'added'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','output', 'deleted'))
    os.mkdir(os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}','output', 'modified'))
    return os.path.join("output_analysis",f'{repo_name}_analysis', f'{commit.hash}')



def filter_modified_files(modified_files):
    #filter modified files for type of changes
    modified_files = [modified_file for modified_file in modified_files if modified_file.change_type == ModificationType.MODIFY or modified_file.change_type == ModificationType.ADD or modified_file.change_type == ModificationType.DELETE]
    #filter modified files for type of files
    modified_files = [modified_file for modified_file in modified_files if modified_file.filename.endswith(".py")]
    return modified_files


#get all_added_deleted and modified_files
def get_commit_version(repo, commit,replace=False):
    modified_files = filter_modified_files(commit.modified_files)
    if len(modified_files) == 0:
        return None
    results_path = set_working_directories(repo, commit,replace)

    for modified_file in modified_files:
        if modified_file.filename.endswith(".py"):
            if modified_file.change_type == ModificationType.MODIFY:
                file = open(os.path.join(results_path,"input",f'modified',f'{modified_file.filename}'), "w",encoding="utf-8")
                if modified_file.source_code is not None:
                    file.write(modified_file.source_code)
                file.close()
            elif modified_file.change_type == ModificationType.ADD:
                file = open(os.path.join(results_path,"input", f'added', f'{modified_file.filename}'), "w",encoding="utf-8")
                try:
                    if modified_file.source_code is not None:
                        file.write(modified_file.source_code)
                except AttributeError:
                    print("Error NoneType")
                file.close()
            elif modified_file.change_type == ModificationType.DELETE:
                file = open(os.path.join(results_path,"input", f'deleted', f'{modified_file.filename}'), "w",encoding="utf-8")
                file.close()

    return results_path

def cleaning():
    if os.path.exists("output_analysis"):
        shutil.rmtree("output_analysis")
    os.mkdir("output_analysis")

def start_analysis(project_path,replace=False):
    cleaning()
    output_time = time.time()
    for file in os.listdir(project_path):
        print("Analysing "+file)
        commits = get_list_of_commits(project_path + file)
        for commit in commits:
            commit_version = get_commit_version(project_path + file, commit,replace)
            if commit_version is None:
                continue
            add_path = os.path.join(commit_version,"input", "added")
            delete_path = os.path.join(commit_version,"input", "deleted")
            modify_path = os.path.join(commit_version,"input", "modified")
            run_code_smile(add_path, os.path.join(add_path.replace("input","output")))
            run_code_smile(delete_path, os.path.join(delete_path.replace("input","output")))
            run_code_smile(modify_path, os.path.join(modify_path.replace("input","output")))
        print(f"Analysis of {file} completed")
        #backup in another folder
        shutil.copytree(f"output_analysis/{file}_analysis",f"output_analysis_{output_time}/{file}")

def main():
    start_analysis("F://input//test//",replace=True)

if __name__ == "__main__":
    main()