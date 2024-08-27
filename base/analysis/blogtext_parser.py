# Script to read the dataset made available here:
# https://www.kaggle.com/datasets/rtatman/blog-authorship-corpus?resource=download

import pandas as pd

df = pd.read_csv("blog_archive/blogtext.csv")

def get_row_by_id(row_id):
    if 'id' not in df.columns:
        return ValueError("The 'id' column is not present in the CSV file")
    
    row = df[df['id'] == row_id]

    # NOTE: IDs are ascribed to posters like names, not posts. A single ID
    # might be connected to a number of actual posts.
    if row.empty:
        return f"No row found with id {row_id}"
    
    return row

if __name__ == '__main__':
    row_id = 2059027
    result = get_row_by_id(row_id)
    print(result)