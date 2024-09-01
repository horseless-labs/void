"""
This is a provisional helper script to parse the processed output from the
blogtext dataset. Currently, those have the format

YYYY-MM-DD H:M:S
This is an example journal entry, which would all be written on a single line

YYYY-MM-DD H:M:S
This is another example entry

Currently, each of these will go on to become their own Conversation in the
SQLite database, and get ingested into the user's FAISS index.

It isn't expected that this is how it will work once there are actual customers
who want to upload their own journals, but that will be a project unto itself.
As such, this is mostly so we can start running experiments on real-world data
with ChatGPT.
"""

def read_journal_file(file_path):
    entries = []
    
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Ensure there's at least one entry (two lines)
    if len(lines) < 2:
        raise ValueError("The file is too short to contain valid entries.")

    # Iterate over the lines in pairs
    for i in range(0, len(lines) - 1, 2):
        date_time = lines[i]
        entry = lines[i + 1] if i + 1 < len(lines) else ''
        entries.append([date_time, entry])
    
    return entries


def read_journal_string(journal_string):
    entries = []
    lines = [line.strip() for line in journal_string.strip().splitlines() if line.strip()]

    if len(lines) < 2:
        raise ValueError("The input string is too short to contain valid entries.")

    for i in range(0, len(lines) - 1, 2):
        date_time = lines[i]
        entry = lines[i + 1] if i + 1 < len(lines) else ''
        entries.append([date_time, entry])
    
    return entries