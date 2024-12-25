import os
import csv
import subprocess


def clone_repos(csv_file, column_name, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)

        # Check if the column name exists in the CSV
        if column_name not in reader.fieldnames:
            print(f"Error: Column '{column_name}' not found in the CSV file.")
            return

        for row in reader:
            repo_path = row[column_name]

            # Ensure the column value is valid
            if not repo_path or '/' not in repo_path:
                print(f"Invalid repository format: {repo_path}")
                continue

            # Create the subfolder name by removing the slash
            author, repo_name = repo_path.split('/')
            subfolder_name = f"{author}{repo_name}"
            clone_path = os.path.join(output_folder, subfolder_name)

            # Check if the repo is already cloned
            if os.path.exists(clone_path):
                print(f"Repository already cloned: {repo_path}")
                continue

            # Clone the repository
            repo_url = f"https://github.com/{repo_path}.git"
            print(f"Cloning repository: {repo_url} into {clone_path}")
            try:
                subprocess.run(["git", "clone", repo_url, clone_path], check=True)
                print(f"Successfully cloned: {repo_path}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone {repo_path}: {e}")


if __name__ == "__main__":
    # Define input CSV file, column name, and output folder
    csv_file = "NICHE.csv"
    column_name = "Github Repo"
    output_folder = "project_history_analysis"

    # Run the cloning script
    clone_repos(csv_file, column_name, output_folder)
