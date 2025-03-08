import os
import sys
import subprocess
import git  # Ensure GitPython is installed before running the script

# Get the current directory (assumes the script is inside the project folder)
project_path = os.getcwd()
print(f"🔄 Detected project directory: {project_path}")

# Function to check if Git is installed
def check_git_installed():
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("❌ Git is not installed. Please install Git and try again.")
        sys.exit(1)

# Check if Git is installed
check_git_installed()

# Check if it's a valid Git repository, initialize if missing
if not os.path.exists(os.path.join(project_path, ".git")):
    print("⚠️ This directory is not a Git repository. Initializing Git...")
    subprocess.run(["git", "init"], check=True)
    print("✅ Git repository initialized.")

try:
    # Load the Git repository
    repo = git.Repo(project_path)

    # Auto-update .gitignore to ignore .vs directory
    gitignore_path = os.path.join(project_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(".vs/\n")
        print("📝 Created .gitignore and added '.vs/' to ignore Visual Studio files.")
    else:
        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()
        if ".vs/" not in gitignore_content:
            with open(gitignore_path, "a") as f:
                f.write("\n.vs/\n")
            print("📝 Added '.vs/' to .gitignore.")

    # Initialize remote_url variable
    remote_url = None

    # Ensure a remote repository exists
    if "origin" not in [remote.name for remote in repo.remotes]:
        remote_url = input("🌍 Enter the GitHub repository URL (e.g., https://github.com/yourusername/yourrepo.git): ").strip()
        if remote_url:
            repo.create_remote("origin", remote_url)
            print(f"✅ Remote repository added: {remote_url}")
        else:
            print("⚠️ No remote repository configured. Push skipped.")
            sys.exit(1)
    else:
        remote_url = repo.remotes.origin.url  # Assign existing remote URL

    # Verify the remote URL matches
    origin_url = repo.remotes.origin.url
    print(f"🔍 Current remote URL: {origin_url}")

    # If the entered remote URL is different, update it
    if remote_url and origin_url != remote_url:
        print("⚠️ Remote URL mismatch. Updating to the new repository URL...")
        repo.delete_remote("origin")
        repo.create_remote("origin", remote_url)
        print(f"✅ Remote URL updated to: {remote_url}")

    # Fetch latest changes from remote
    print("🔄 Fetching latest changes from GitHub...")
    repo.git.fetch()

    # Show git status
    print("🔍 Checking for changes...")
    print(repo.git.status())

    # Ensure there is at least one commit
    if not repo.head.is_valid():
        print("📌 Creating initial commit...")
        repo.git.commit("--allow-empty", m="Initial commit")

    # Rename master to main if needed
    current_branch = repo.active_branch.name
    if current_branch != "main":
        print(f"🔄 Renaming branch '{current_branch}' to 'main'...")
        repo.git.branch("-M", "main")

    # Pull latest changes before pushing
    print("🔄 Pulling latest changes from GitHub...")
    try:
        repo.git.pull("origin", "main", "--rebase")
    except git.exc.GitCommandError:
        print("⚠️ Pull failed, likely due to no existing main branch. Continuing with the push.")

    # Check if there are any modifications (including untracked files)
    if not repo.is_dirty(untracked_files=True):
        print("✅ No modifications detected. Nothing to commit.")
        sys.exit(0)

    # Stage all changes
    print("📌 Staging all changes...")
    repo.git.add(all=True)

    # Ask for commit message
    commit_message = input("✍️  Enter your commit message: ").strip()
    if not commit_message:
        print("❌ Commit message cannot be empty. Please run the script again with a valid message.")
        sys.exit(1)

    # Commit changes
    repo.git.commit(m=commit_message)

    # Push changes to GitHub
    print("📤 Pushing changes to GitHub...")
    repo.git.push("-u", "origin", "main")

    print("✅ Push completed successfully!")

except git.exc.GitCommandError as e:
    print(f"❌ Push failed! Error: {e}")
    print("Try running 'git pull origin main --rebase' first.")
    sys.exit(1)
