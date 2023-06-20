from cs_detector.code_extractor.models import check_model_method, load_model_dict
from cs_detector.code_extractor.libraries import *
import ast

def test_model_list():
    dict = load_model_dict()
    print(check_model_method('Sequential()', dict, ['tensorflow']) == True)

def get_lib_test():
    with open('../../../examples/Code_Smell_Examples.py', 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    libraries = extract_libraries(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            n = node.func
            method_name = ""
            while(isinstance(n,ast.Attribute)):
                method_name += "."+str(node.func.attr)
                n = n.value
            if isinstance(n, ast.Name):
                method_name = n.id+method_name
            else:
                method_name = ""
            print(get_library_of_node(node,libraries),"for method",method_name)

def main():
    get_lib_test()




if __name__ == "__main__":
    main()
