import subprocess

def get_git_status_output():
    result = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
    return result.stdout

def get_files_to_commit(git_status_output):
    files_to_commit = []
    untracked_files = []
    lines = git_status_output.splitlines()

    status_codes = {
        ' M': 'Modified',
        'A ': 'Added',
        'D ': 'Deleted',
        'R ': 'Renamed',
        'C ': 'Copied',
        'U ': 'Updated but unmerged',
        '??': 'Untracked'
    }

    for line in lines:
        code = line[:2]
        file_path = line[3:].strip()
        if code in status_codes:
            if code == '??':
                untracked_files.append(file_path)
            else:
                files_to_commit.append(file_path)

    return files_to_commit, untracked_files

# Written for the output to be interpolated into an scp command
def main():
    git_status_output = get_git_status_output()
    files_to_commit, untracked_files = get_files_to_commit(git_status_output)
    files_to_commit += untracked_files

    output = ""
    if files_to_commit:
        for f in files_to_commit:
            output += f + " "
        print(output)

if __name__ == "__main__":
    main()