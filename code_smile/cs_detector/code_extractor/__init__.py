
import ast

from code_smile.cs_detector.code_extractor.libraries import extract_libraries
from code_smile.cs_detector.code_extractor.dataframe_detector import dataframe_check
def analyze_example(filename):
    with open(filename, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    libraries = extract_libraries(tree)
    print(libraries)
    df_dict = {'loc': 'loc', 'iloc': 'iloc', 'at': 'at', 'iat': 'iat', 'xs': 'xs', 'ix': 'ix', 'irow': 'irow','concat':'concat','DataFrame':'DataFrame'}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            print(dataframe_check(node, libraries))


def main():
    analyze_example("../../examples/Code_Smell_Examples.py")


if __name__ == "__main__":
    main()