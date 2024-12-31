import ast

import pandas as pd


def search_pandas_library(libraries):
    for lib in libraries:
        if 'pandas' in lib:
            short = extract_lib_object(lib)
            if short is None:
                short = 'pandas'
            return short
    return None

def load_dataframe_dict(path):
    return pd.read_csv(path, dtype={'id': 'string', 'library': 'string', 'method': 'string'})

def dataframe_check(fun_node, libraries,df_dict):
    short = search_pandas_library(libraries)
    list = [short]
    if short is None:
        return None
    return recursive_search_variables(fun_node,list,df_dict)
 



def dataframe_check_at_line(fun_node, libraries, df_dict, target_line):
    """
    Check the state of variables as of the specified target line, including intermediate variables,
    while explicitly tracking their types.
    """
    short = search_pandas_library(libraries)
    if short is None:
        return []

    # Initialize the variable state with the library alias
    variable_states = {short: {'type': 'DataFrame', 'line': 0}}

    # Walk through the AST and track variable assignments up to target_line
    for node in ast.walk(fun_node):
        if hasattr(node, 'lineno') and node.lineno >= target_line:
            continue  # Skip nodes beyond the target line

        if isinstance(node, ast.Assign):
            target_id = None
            if isinstance(node.targets, list) and hasattr(node.targets[0], 'id'):
                target_id = node.targets[0].id

            # Analyze the right-hand side of the assignment
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                func_name = node.value.func.attr
                obj_name = (
                    node.value.func.value.id
                    if isinstance(node.value.func.value, ast.Name)
                    else None
                )

                # Check if derived from a DataFrame variable
                if obj_name in variable_states and func_name in df_dict['method'].tolist():
                    variable_states[target_id] = {'type': 'DataFrame', 'line': node.lineno}

            elif isinstance(node.value, ast.Name) and node.value.id in variable_states:
                # Variable is assigned another variable's value
                if target_id:
                    variable_states[target_id] = variable_states[node.value.id]

            elif isinstance(node.value, ast.List):
                # Variable is explicitly assigned a list
                if target_id:
                    variable_states[target_id] = {'type': 'List', 'line': node.lineno}

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # Track intermediate objects from method calls on DataFrames
            obj_name = node.func.value.id if isinstance(node.func.value, ast.Name) else None
            func_name = node.func.attr

            if obj_name in variable_states and func_name == "groupby":
                # Derive intermediate variables from groupby
                if hasattr(node, 'lineno'):
                    variable_states[obj_name] = {'type': 'DataFrame', 'line': node.lineno}

    # Filter only DataFrame variables that exist before the target line
    dataframe_vars = [
        var for var, state in variable_states.items()
        if state['type'] == 'DataFrame' and state['line'] < target_line
    ]
    return dataframe_vars



def recursive_search_variables(fun_node,init_list,df_dict):
    list = init_list.copy()
    for node in ast.walk(fun_node):
        if isinstance(node, ast.Assign):
            # check if the right side contains a dataframe
            if isinstance(node.value, ast.Expr):
                expr = node.value
                if isinstance(expr.value, ast.Name):
                    name = expr.value
                    if name.id in list:
                        if hasattr(node.targets[0], 'id'):
                            if node.targets[0].id not in list:
                                list.append(node.target.id)
            if isinstance(node.value, ast.Name):

                name = node.value
                if name.id in list:
                    if hasattr(node.targets[0], 'id'):
                        if node.targets[0].id not in list:
                            list.append(node.targets[0].id)

            if isinstance(node.value, ast.Call):
                name_func = node.value.func
                if isinstance(name_func, ast.Attribute):
                    id = name_func.value
                    if isinstance(name_func.value, ast.Subscript):
                        if isinstance(name_func.value.value, ast.Name):
                            id = name_func.value.value.id
                    else:
                        if(isinstance(name_func.value,ast.Name)):
                            id = name_func.value.id
                        else:
                            continue
                    if id in list:
                        if name_func.attr in df_dict['method'].tolist():
                            if hasattr(node.targets[0], 'id'):
                                if node.targets[0].id not in list:
                                    list.append(node.targets[0].id)
            else:
                if isinstance(node.value, ast.Subscript):
                    if isinstance(node.value.value, ast.Name):
                        if node.value.value.id in list:
                            if hasattr(node.targets[0], 'id'):
                                if node.targets[0].id not in list:
                                    list.append(node.targets[0].id)
    if list == init_list:
        return list
    else:
        return recursive_search_variables(fun_node,list,df_dict)

def extract_lib_object(lib):
    try:
        split_lib = lib.split(" as ")
        if split_lib[1] is not None and split_lib[1] != "": # this because some libraries are imported with and endwith as
            short = split_lib[1]
            return short
        else:
            return None
    except:
        return None


def extract_variables(list_variables):
    pass
