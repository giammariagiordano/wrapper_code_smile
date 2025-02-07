import os

from pydriller import Repository

def get_list_of_commits_between_two_releases(repo, initial_release, final_release):
    commits = []


    for commit in Repository(repo, from_commit=initial_release, to_commit=final_release).traverse_commits():
        commits.append(commit)
    return commits
print(get_list_of_commits_between_two_releases('F:\\projects\\microsoftEdgeML\\','e4d525551088d468db6989f3082429747edccd9b','46320ca8b48d4839f4127e6e1faba120f557f2e1'))