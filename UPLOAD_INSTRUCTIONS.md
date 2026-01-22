# How to Upload Your Project to GitHub

Since I cannot directly execute git commands in your environment (git is not found in the path), please run the following commands in your terminal **(Git Bash or PowerShell)**.

### 1. Initialize the Repository
Run this in the folder `c:\Users\DKS\Desktop\VSC\Dec25\python` (your current workspace):

```bash
git init
```

### 2. Configure the Remote
Link your local folder to the GitHub repository you created:

```bash
git remote add origin https://github.com/DKS-MANAGER/realrich_PPP.git
```
*(If it says remote origin already exists, run `git remote set-url origin https://github.com/DKS-MANAGER/realrich_PPP.git`)*

### 3. Add Your Project Files
Add the Dashboard and the Analysis Notebook:

```bash
git add wealth_dashboard/
git add richest_listPPP.ipynb
git add .gitignore
```
*(You can use `git add .` to add everything, but be careful not to upload unnecessary files like large datasets or venv folders if they aren't ignored).*

### 4. Commit and Push
Save your changes and upload them:

```bash
git commit -m "Initial commit: Wealth Dashboard and PPP Analysis"
git branch -M main
git push -u origin main
```

---
**Note:** You may be asked to sign in to GitHub via the browser or enter a Personal Access Token.
