# Script to read the dataset made available here:
# https://www.kaggle.com/datasets/rtatman/blog-authorship-corpus?resource=download

import pandas as pd
import random

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

def get_row_by_index(idx):
    if idx < 0 or idx >= len(df):
        return f"Position {idx} is out of range"
    
    row = df.iloc[idx]
    return row

def get_random_posts():
    idx = random.choice(df.index)
    return df.loc[idx]

if __name__ == '__main__':
    result = get_row_by_index(22)
    result_id = result.id
    posts = get_row_by_id(result_id)
    print(posts)