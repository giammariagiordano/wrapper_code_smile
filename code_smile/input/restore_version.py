import os
from main import reorganize_output_code_smile

def restore(path):
    os.chdir(path)
    os.system("git pull")
    os.chdir("../..")


def main():
    for dir in os.listdir("./projects"):
        restore(os.path.join(os.path.abspath("./projects"), dir))

if __name__ == "__main__":
    main()
