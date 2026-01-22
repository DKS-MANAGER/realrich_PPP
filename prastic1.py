
import subprocess
import sys

def update_python_via_conda():
    try:
        print("Attempting to update Python via Conda...")
        # This assumes 'conda' is in your system PATH
        subprocess.check_call(["conda", "update", "python", "-y"])
        print("Update command finished.")
    except FileNotFoundError:
        print("Error: 'conda' command not found. Please run this in Anaconda Prompt.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during update: {e}")

if __name__ == "__main__":
    update_python_via_conda()