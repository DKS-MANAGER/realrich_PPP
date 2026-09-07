import os
import sys
import runpy

# Ensure repository root is on sys.path
repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Target the main dashboard entrypoint
app_path = os.path.join(repo_root, "dashboard", "app.py")
runpy.run_path(app_path, run_name="__main__")
