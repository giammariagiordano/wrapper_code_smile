import os

def restore(path):
    os.chdir(path)
    os.system("git pull origin main")
    os.chdir("../..")

def rename_folder(path):
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path, dir)):
            os.rename(os.path.join(path,dir), os.path.join(path,dir.split("___")[0]))
        return os.path.join(path,dir.split("___")[0])
def restore_projects(filepath="./projects"):
    for dir in os.listdir(filepath):
        new_path = rename_folder(os.path.abspath(filepath))
        restore(new_path)

if __name__ == "__main__":
    restore_projects("F:/input/projects22-06")

#export the main method as restore
