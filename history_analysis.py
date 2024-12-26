import os, shutil
import subprocess
import time

from concurrent.futures import ThreadPoolExecutor

import git
from git import GitCommandError
from pydriller import Repository, ModificationType


output_time = str(time.time())
def run_code_smile(project, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = os.path.abspath(output_path) + "/"
    project = project + "/"
    command = ["python3", os.path.join("./","code_smile","controller","analyzer.py"),
               "--input", project, "--output", output_path]
    p = subprocess.run(command)
    p.check_returncode()
    print("Code_smile executed successfully")

def reset_repo_to_head(repo):

    repo = git.Repo(repo)
    repo.git.reset('--hard','HEAD')
    try:
        repo.git.checkout('master')
        repo.git.pull('origin','master')
    except GitCommandError:

        #try main
        try:
            repo.git.checkout('main')
            repo.git.pull('origin','main')
        except GitCommandError:
            print("Error in reset_repo_to_head")
    return

def get_list_of_commits(repo):
    reset_repo_to_head(repo)
    commits = []
    for commit in Repository(repo).traverse_commits():
        commits.append(commit)
    return commits


def set_working_directories(repo,commit,replace=False):
    repo = git.Repo(repo)
    try:
        repo.git.checkout(commit.hash)
    except:
        print("Error in checkout")
        return None
    repo_name = os.path.basename(repo.working_dir)


    if replace:
        if os.path.exists(os.path.join("output_analysis",f'{repo.working_dir}_analysis')):
            shutil.rmtree(os.path.join("output_analysis",f'{repo.working_dir}_analysis'))
    # get all_added_deleted and modified_files
    os.makedirs(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','input'))
    os.makedirs(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','output'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','input', 'added'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','input', 'deleted'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','input', 'modified'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','output', 'added'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','output', 'deleted'))
    os.mkdir(os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}','output', 'modified'))
    return os.path.join("output_analysis",output_time,f'{repo_name}_analysis', f'{commit.hash}')



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
    if results_path is None:
        return None
    for modified_file in modified_files:
        if modified_file.filename.endswith(".py"):
            #get folder path of the modified file without filename
            new_path = ""
            if modified_file.change_type == ModificationType.MODIFY or modified_file.change_type == ModificationType.ADD:
                new_path = os.path.dirname(modified_file.new_path)
            elif modified_file.change_type == ModificationType.DELETE:
                new_path = os.path.dirname(modified_file.old_path)
            if modified_file.change_type == ModificationType.MODIFY:

                #create folders for the new modified file to modified_file.newpath
                if not os.path.exists(os.path.join(results_path,"input",f'modified',f'{new_path}')):
                    os.makedirs(os.path.join(results_path,"input",f'modified',f'{new_path}'))
                file = open(os.path.join(results_path,"input",f'modified',f'{modified_file.new_path}'), "w",encoding="utf-8")
                if modified_file.source_code is not None:
                    file.write(modified_file.source_code)
                file.close()
            elif modified_file.change_type == ModificationType.ADD:
                if not os.path.exists(os.path.join(results_path,"input", f'added', f'{new_path}')):
                    os.makedirs(os.path.join(results_path,"input", f'added', f'{new_path}'))
                file = open(os.path.join(results_path,"input", f'added', f'{modified_file.new_path}'), "w",encoding="utf-8")
                try:
                    if modified_file.source_code is not None:
                        file.write(modified_file.source_code)
                except AttributeError:
                    print("Error NoneType")
                file.close()
            elif modified_file.change_type == ModificationType.DELETE:
                if not os.path.exists(os.path.join(results_path,"input", f'deleted', f'{new_path}')):
                    os.makedirs(os.path.join(results_path,"input", f'deleted', f'{new_path}'))
                try:
                    if modified_file.source_code_before is not None:
                        file = open(os.path.join(results_path,"input", f'deleted', f'{modified_file.old_path}'), "w",encoding="utf-8")
                        file.write(modified_file.source_code_before)
                        file.close()
                except AttributeError:
                    print("Error NoneType")

    return results_path

def cleaning():

    if os.path.exists("output_analysis"):
        shutil.rmtree("output_analysis")
    os.mkdir("output_analysis")


def create_output_folder(base_path,project_name,output_time=str(time.time())):
    if not os.path.exists(os.path.join(base_path,output_time)):
        os.makedirs(os.path.join(base_path,output_time))
    base_path = os.path.join(base_path,output_time)
    if not os.path.exists(os.path.join(base_path,project_name)):
        os.makedirs(os.path.join(base_path,project_name))
    return os.path.join(base_path,project_name)

def logging(project_name):
    with open("execution_log.txt","a") as f:
        f.write(project_name)
        f.write("\n")
    with open("detailed_log.txt","a") as f:
        f.write(project_name)
        f.write(f"Analyzed in run {output_time}")
        f.write("\n")


def clean_log():
    with open("execution_log.txt","w") as f:
        f.write("")
    with open("detailed_log.txt","w") as f:
        f.write("")




def get_log_projects():
    projects = []
    with open("execution_log.txt","r") as f:
        projects = f.readlines()
    return projects

def start_analysis(project_path, replace=False, start_index=0, end_index=0, restart=False, workers=16):
    """
    Start analysis of projects, distributing files among workers.
    """
    output_path = './output_analysis/'

    if restart:
        clean_log()

    print("Analysis Start Now!")

    # Get list of all project files
    analyzed_projects = get_log_projects()
    for i in range(len(analyzed_projects)):
        analyzed_projects[i] = analyzed_projects[i].replace("\n","")
    files = [
        file for file in os.listdir(project_path)
        if file.replace("\n","") not in analyzed_projects
    ]

    # Optionally slice the files based on start and end indices
    if end_index > 0:
        files = files[start_index:end_index]

    print(f"Found {len(files)} files to analyze.")

    # Use ThreadPoolExecutor for parallel analysis
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(lambda file: analyze_single_project(project_path, file), files)

    print("Analysis completed for all files.")


def analyze_single_project(project_path, file):
    """
    Analyzes a single project.
    """
    output_path = './output_analysis/'
    try:
        print(f"Starting analysis for {file}...")

        # Get the list of commits
        commits = get_list_of_commits(os.path.join(project_path, file))
        if not commits:
            print(f"No commits found for {file}. Skipping.")
            return

        # Create output folder
        project_output_path = create_output_folder(output_path, f'{file}_analysis', output_time)

        # Process each commit
        for commit in commits:
            commit_version = get_commit_version(os.path.join(project_path, file), commit)
            if commit_version is None:
                continue

            # Analyze added, deleted, and modified paths
            add_path = os.path.join(commit_version, "input", "added")
            delete_path = os.path.join(commit_version, "input", "deleted")
            modify_path = os.path.join(commit_version, "input", "modified")
            run_code_smile(add_path, os.path.join(project_output_path, commit.hash, "output", "added"))
            run_code_smile(delete_path, os.path.join(project_output_path, commit.hash, "output", "deleted"))
            run_code_smile(modify_path, os.path.join(project_output_path, commit.hash, "output", "modified"))

        print(f"Analysis of {file} completed.")
        logging(file)
    except Exception as e:
        print(f"Error analyzing project {file}: {e}")

def main():
    start_analysis(os.path.join(str('./'),'code_smile','input','projects'),replace=True,start_index=0,end_index=600,restart=False)

if __name__ == "__main__":
    main()