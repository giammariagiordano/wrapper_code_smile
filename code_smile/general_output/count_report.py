import pandas as pd




def smell_report():
    df = pd.read_csv('overview_output.csv')
    #filter dataframe with only the columns we need
    df = df[[ 'name_smell', 'smell']]
    a = df.groupby('name_smell').sum()
    a.to_csv('general_overview.csv')

def project_report():
    df = pd.read_csv('overview_output.csv')
    #filter dataframe with only the columns we need
    df = df[['filename', 'name_smell', 'smell']]
    #cut first part of filename to get project name
    df['project_name'] = df['filename'].str.split('\\').str[2]
    df = df[['project_name', 'smell']]
    # set dtype of smell as int
    df['smell'] = df['smell'].astype(int)
    a = df.groupby('project_name').sum()
    a.to_csv('project_overview.csv')
def main():
    project_report()
    smell_report()

if __name__ == '__main__':
    main()
