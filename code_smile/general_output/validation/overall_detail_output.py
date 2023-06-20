import os

import pandas as pd

# this function creates a unique file for each smell report identified in the output folder
smells_names=['deterministic_algorithm_option_not_used','merge_api_parameter_not_explicitly_set','columns_and_datatype_not_explicitly_set','empty_column_misinitialization','nan_equivalence_comparison_misused','in_place_apis_misused','memory_not_freed','Chain_Indexing','dataframe_conversion_api_misused','matrix_multiplication_api_misused','gradients_not_cleared_before_backward_propagation','tensor_array_not_used','pytorch_call_method_misused','unnecessary_iteration','broadcasting_feature_not_used']
def merge_detail_files(input_path,output_path):
    with open(output_path + "overall_detail_output.csv", "w") as f:
        f.write("filename,function_name,smell_name,line\n")
        for dir in os.listdir(input_path):
            #get list of file of each dir
            for file in os.listdir(input_path + dir):
                #open each csv file
                if file.endswith(".csv") and file.split(".")[0] in smells_names:

                    report = pd.read_csv(input_path + dir+"/"+file)
                    for index, row in report.iterrows():
                        f.write(row["filename"] + "," + row["function_name"] + "," + row["smell_name"] + "," + str(row["line"]) + "\n")
        f.close()
        return

def diff_files():
    df = pd.read_csv("overall_detail_output.csv")
    df2 = pd.read_csv("../overview_output.csv")
    df3 = pd.merge(df, df2, on=['filename', 'function_name'], how='outer', indicator=True)
    df3 = df3[df3['_merge'] == 'left_only']
    df3.to_csv("diff.csv", index=False)
def main():
    input_path = "F:/output/test/project_analysis18-05/"
    output_path ="./"
    merge_detail_files(input_path,output_path)


if __name__ == '__main__':
    diff_files()