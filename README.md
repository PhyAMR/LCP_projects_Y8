# Final Projects for Laboratory of Computational Physics

In each of the branches of this repo you find all the necessary to complete your final project.
In particular the file Project.ipynb describes the projects and provides guidance to its development.
Other files could be present if needed.

Each branch is named after the group of students a given project is assigned to.
The groups compositions are listed [here](https://docs.google.com/spreadsheets/d/10GamYNyq7fjBw5ZsYCz3GmkhrrKCutprQArEKzgjVyw/)

Students are supposed to work together to produce a short report on the assigned task. The preferred format for the latter is a jupyter notebook, with the proper description, the code implemented for the purpose and the actual results (plots, tables, etc.). The notebook has to be delivered with all the cells executed and should live in a GitHib repository. There is no need to make a pull request to the central repository.

### Computing Resources

A Virtual Machine within [CloudVeneto](http://cloudveneto.it/) can be created for each group. Note that, by default, they are not. For some projects though, large datasets are needed, in those cases a VM has been (are being) created to store those files. Refer to ClouldInstructions.md for the steps to take in order to use those resources.

Alternatively, students can use [colab](https://colab.research.google.com/) (for which though no instructions are provided here).

Here is the complete, expanded **`README.md`** file. It combines the setup instructions, the workflow, and a new troubleshooting section to handle the most common "Git headaches" your friends might encounter.

---

# 🚀 Project Name: [Insert Project Title]

This repository is a focused fork of **[Original Creator/Project Name]**. To keep our collaboration clean, we are working exclusively on the **`Group17`** branch.

---

## 🛠 Setup Instructions

Follow these steps to ensure your local environment only tracks our active branch and stays synced with the original source.

### 1. Clone the Specific Branch

This command clones *only* our working branch, saving you from downloading unnecessary history.

```bash
git clone --branch Group17 --single-branch git@github.com:PhyAMR/LCP_projects_Y8.git
cd LCP_projects_Y8

```

### 2. Connect to the "Upstream" (Original Project)

To pull in core updates from the original repository, add it as a remote:

```bash
git remote add upstream git@github.com:PhysicsOfData/LCP_projects_Y8.git

```

### 3. Lockdown the Remote

Run this to ensure your Git doesn't try to fetch other branches from the fork:

```bash
git remote set-branches origin Group17
git fetch --prune origin

```

---

## 🔄 Daily Workflow

To avoid merge conflicts, follow this "Loop":

1. **Update your local code:**
```bash
git pull origin Group17

```


2. **Work and Commit:**
```bash
git add .
git commit -m "Brief description of what you changed"

```


3. **Push to the fork:**
```bash
git push origin Group17

```



---

## ⚠️ Troubleshooting & Common Fixes

### "I see branches I don't want"

If `git branch -a` still shows old branches from the original repo, force a cleanup:

```bash
git fetch --prune origin

```

### "Automatic merge failed" (Merge Conflicts)

If you and a friend edit the same line, Git will get confused.

1. Open the files listed in the error.
2. Look for `<<<<<<< HEAD` and `>>>>>>>`.
3. Delete the markers and keep the code you want.
4. `git add <file>` and `git commit`.

### "Updates were rejected" (Non-fast-forward)

This happens if someone pushed changes while you were working.

* **Fix:** Run `git pull origin Group17` first, resolve any conflicts, then push again.

---

## 📬 Coordination

* **Lead:** [Your Name/Handle]
* **Chat:** [Insert Discord/Slack Link]

---

