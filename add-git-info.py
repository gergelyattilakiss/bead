#!/usr/bin/env python3
"""
Generate git_info.py with current git repository information.
Cross-platform replacement for add-git-info.sh
"""
import subprocess
import sys
import os

def run_git_command(cmd):
    """Run a git command and return its output, or empty string if it fails."""
    try:
        result = subprocess.run(
            ['git'] + cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

def check_dirty():
    """Check if the repository has uncommitted changes (ignoring untracked and git_info.py)."""
    try:
        # Get porcelain status
        result = subprocess.run(
            ['git', 'status', '--porcelain=1'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True, 
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if not line:  # empty line
                continue
            if line.startswith('??'):  # untracked files
                continue
            if ' bead_cli/git_info.py' in line:  # ignore changes in git_info.py
                continue
            # If we get here, there are uncommitted changes
            return True
            
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    # Collect git information
    git_repo = run_git_command(['config', '--get', 'remote.origin.url'])
    git_branch = run_git_command(['branch', '--show-current'])
    git_date = run_git_command(['show', 'HEAD', '--pretty=tformat:%cI', '--no-patch'])
    git_hash = run_git_command(['show', 'HEAD', '--pretty=tformat:%H', '--no-patch'])
    tag_version = run_git_command(['describe', '--tags'])
    
    dirty = check_dirty()
    
    # Generate the git_info.py file
    git_info_content = f'''# generated - do not edit
GIT_REPO    = "{git_repo}"
GIT_BRANCH  = "{git_branch}"
GIT_DATE    = "{git_date}"
GIT_HASH    = "{git_hash}"
TAG_VERSION = "{tag_version}"
DIRTY       = {dirty}
'''
    
    # Ensure the directory exists
    os.makedirs('bead_cli', exist_ok=True)
    
    # Write the file
    with open('bead_cli/git_info.py', 'w') as f:
        f.write(git_info_content)
    
    print("Generated bead_cli/git_info.py")

if __name__ == '__main__':
    main()