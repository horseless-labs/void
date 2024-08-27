# Script to read the dataset made available here:
# https://www.kaggle.com/datasets/rtatman/blog-authorship-corpus?resource=download

import pandas as pd
import random

df = pd.read_csv("blog_archive/blogtext.csv")

# NOTE: IDs are ascribed to posters like names, not posts. A single ID
# might be connected to a number of actual posts.
def get_row_by_id(row_id):
    if 'id' not in df.columns:
        return ValueError("The 'id' column is not present in the CSV file")
    
    row = df[df['id'] == row_id]

    if row.empty:
        return f"No row found with id {row_id}"
    
    return row

# NOTE: Gets a post based on its position in the pandas DataFrame
def get_row_by_index(idx):
    if idx < 0 or idx >= len(df):
        return f"Position {idx} is out of range"
    
    row = df.iloc[idx]
    return row

def get_random_posts():
    idx = random.choice(df.index)
    return df.loc[idx]

def get_unique_topics():
    topic_counts = df['topic'].value_counts()
    topic_counts = topic_counts.to_dict()
    return topic_counts

if __name__ == '__main__':
    # result = get_row_by_index(22)
    # result_id = result.id
    # posts = get_row_by_id(result_id)
    # print(posts)

    topics = get_unique_topics()
    print("Unique topics")
    print(topics)