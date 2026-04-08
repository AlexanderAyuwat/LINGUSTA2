import subprocess
import sys

def run_git(args):
    result = subprocess.run(['git'] + args, capture_output=True, text=True)
    print(f"--- git {' '.join(args)} ---")
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

run_git(['status'])
run_git(['add', '.'])
run_git(['commit', '-m', 'Update for presentation'])
run_git(['push', '-u', 'origin', 'main'])
