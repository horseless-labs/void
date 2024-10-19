import subprocess
import re

def get_git_status_output():
    result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, text=True)
    return result.stdout

def get_files_to_commit(git_status_output):
    files_to_commit = []
    lines = git_status_output.splitlines()
    pattern = re.compile(r'\s*modified:\s*(.*)')

    for line in lines:
        match = pattern.match(line)
        if match:
            files_to_commit.append(match.group(1))

    return files_to_commit

def main():
    git_status_output = get_git_status_output()
    files_to_commit = get_files_to_commit(git_status_output)

    if files_to_commit:
        print("Files with changes to commit:")
        for file in files_to_commit:
            print(file)
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    main()