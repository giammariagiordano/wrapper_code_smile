import pandas as pd
# take the whole set and create a randomized set of 95% confidence level and 5% error
import math
from datetime import datetime

import os

smells_names=['deterministic_algorithm_option_not_used','merge_api_parameter_not_explicitly_set','columns_and_datatype_not_explicitly_set','empty_column_misinitialization','nan_equivalence_comparison_misused','in_place_apis_misused','memory_not_freed','Chain_Indexing','dataframe_conversion_api_misused','matrix_multiplication_api_misused','gradients_not_cleared_before_backward_propagation','tensor_array_not_used','pytorch_call_method_misused','unnecessary_iteration','broadcasting_feature_not_used']


def get_scoring(confidence_level):
    # Calcola il valore Z corrispondente al livello di confidenza
    z_value = 0.0
    if confidence_level == 0.90:
        z_value = 1.645
    elif confidence_level == 0.95:
        z_value = 1.96
    elif confidence_level == 0.99:
        z_value = 2.576
    return z_value


def calculate_sample_size(population_size, confidence_level, margin_error, population_std=None):
    z_value = get_scoring(confidence_level)

    # Champion set size
    sample_size = 0
    if population_std:
        sample_size = ((z_value ** 2) * (population_std ** 2)) / (
                (margin_error ** 2) * ((population_size - 1) / population_size) + (z_value ** 2) * (
                population_std ** 2))

    else:
        sample_size = (z_value ** 2 * 0.25) / (margin_error ** 2)
        dimension_factor = 1 + ((z_value ** 2 * 0.25) / (margin_error ** 2 * population_size))
        sample_size = sample_size / dimension_factor
    return math.ceil(sample_size)


def stratifying(input_dataset, smell_name, confidence_level=0.95, margin_error=0.05):
    df = pd.read_csv(input_dataset)
    df = df[df['smell_name'] == smell_name]

    # Parametri di esempio
    population_size = len(df)
    if population_size == 0:
        return 0, None
    # Dimensione della popolazione

    # Calcola la dimensione del campione
    sample_size = calculate_sample_size(population_size, confidence_level, margin_error)

    return sample_size, df


def champion_set(sample_size, df, smell_name, output_path):
    return df.sample(n=sample_size).to_csv(f'{output_path}/champion_set_{smell_name}.csv', index=False)


def create_stratified_folder():
    try:
        time_a = str(datetime.now()).replace(":", "-").replace(" ", "_")
        os.mkdir(time_a)
        return time_a
    except:
        pass


def main():
    # create_stratified_folder()
    folder_name = create_stratified_folder()
    input_dataset = 'overall_detail_output.csv'
    for smell_name in smells_names:
        sample_size, df = stratifying(input_dataset, smell_name)
        if sample_size == 0:
            continue
        champion_set(sample_size, df, smell_name, folder_name)


if __name__ == '__main__':
    main()
