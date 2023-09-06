# Contributing

Thank you for investing your time in contributing to our project! Any contribution you make will be reflected in this repository's [README](README.md) file.

## New contributor guide

See the [README](README.md) to get an overview of the project. Ideas for improvement are in [TODO](TODO.md). We're operating under the MIT Open Source [license](LICENSE) so you can still use anything you contribute (but so can the rest of us).

## Getting started

### Issues

#### Create a new issue

If you spot a problem with the docs, [search if an issue already exists](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments). If a related issue doesn't exist, you can open a [new issue](https://github.com/hammer-mt/thumb/issues/new).

#### Solve an issue

Scan through our [existing issues](https://github.com/hammer-mt/thumb/issues) to find one that interests you. Leave a comment on the issue asking if you can pick up the issue so maintainers knowing you want to work on it.

### Make Changes

#### Prerequisites

Make sure you have the following installed in your development environment:

- [Python](https://www.python.org/downloads/)

#### Development Workflow

Follow these steps below to get the package working locally:

1. Create a personal fork of the project on GitHub and clone locally

```shell
# Using HTTPS
git clone https://github.com/your-username/thumb.git

# Or using SSH
git clone git@github.com:your-username/thumb.git
```

2. Add the original repository as a remote called `upstream`

```shell
git remote add upstream https://github.com/hammer-mt/thumb.git
```

3. Make sure to pull upstream changes into your local repository

```shell
git fetch upstream
```

4. Create a new branch to work from

```shell
git checkout -b branchname
```

5. Activate a virtual environment

```shell
python -m venv venv

# Using Windows
`venv\Scripts\activate`

# Using Mac
`source ./venv/bin/activate`
```

6. Install the package as editable

```shell
# Install from the cloned repo:
%pip install -e your/local/path
```
Alternatively if working from a Jupyter Notebook, you can set the module to auto-reload on every saved change to your local package.
```
%load_ext autoreload
%autoreload 2
```

7. Make your changes / contributions

Make sure to follow the code style of the project, run any tests (if available) and add / update the documentation as needed.

Squash your commits with git's [interactive rebase](http://git-scm.com/docs/git-rebase) (create a new branch if necessary). Write your commit messages in the present tense (what does it does to the code?). Push your changes to your fork on GitHub, the remote `origin`.

```shell
# Squash commits, fix up commit messages etc.
git rebase -i origin/main

# Push to your fork on GitHub
git push origin main
```

### Pull Request

When you're done making the changes, open a pull request, often referred to as a PR. You do this in GitHub from your Fork of the project. Target the `develop` branch if there is one, else go for `main`.

- Fill out the PR description summarizing your changes so we can review your PR. This template helps reviewers understand your changes and the purpose of your pull request.
- Don't forget to [link PR to issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) if you are solving one.
- Enable the checkbox to [allow maintainer edits](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/allowing-changes-to-a-pull-request-branch-created-from-a-fork) so the branch can be updated for a merge. Once you submit your PR, a Docs team member will review your proposal. We may ask questions or request for additional information.
- We may ask for changes to be made before a PR can be merged, either using [suggested changes](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/incorporating-feedback-in-your-pull-request) or pull request comments. You can apply suggested changes directly through the UI. You can make any other changes in your fork, then commit them to your branch.
- As you update your PR and apply changes, mark each conversation as [resolved](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request#resolving-conversations).
- If you run into any merge issues, checkout this [git tutorial](https://lab.github.com/githubtraining/managing-merge-conflicts) to help you resolve merge conflicts and other issues.
- Once the pull request is approved and merged you can pull the changes from upstream to your local repo and delete your extra branch(es).

### Your PR is merged!

Congratulations :tada::tada: The `thumb` team thanks you!

Once your PR is merged, we will add you to the All Contributors Table in the [`README.md`](./README.md#all-contributors)

### Publishing to PyPi

This is more a note to self, because I keep forgetting.

1. `pip install twine`
2. `cd codes/projects/thumb`
3. update the version number in `setup.py`
4. `python setup.py sdist bdist_wheel`
5. delete old versions in the `dist` folder
6. `python -m twine check dist/*`
7. `git commit -m "release v0.2"`
7. `git tag v0.2` and `git push origin v0.2`

Resources:

- [Using TestPyPi](https://packaging.python.org/guides/using-testpypi/)
- [Building a Python Package and Publishing on PyPi (The Python Package Index)](https://www.section.io/engineering-education/building-a-python-package-and-publishing-on-pypi/)
- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
- [Publishing package distribution releases using GitHub Actions CI/CD workflows](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)