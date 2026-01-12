# PROJECT_NAME
This repository is to be used as a template for all repositories in the
organization.

## !! IMPORTANT !! Protection of Company Property
All files (source code, documentation, configuration) must contain the following
text at the very top:

```
Copyright (c) YKK AP Technologies Lab (NA) Inc. Proprietary and Confidential.
See LICENSE for use restrictions.
```

## Init Repository


First you must init the repository. Follow these steps.


### 1. Install Pixi Package Manager
**Linux & MacOS**

```bash
curl -fsSL https://pixi.sh/install.sh | sh
source ~/.bashrc
```

or with wget

```bash
wget -qO- https://pixi.sh/install.sh | sh
source ~/.bashrc
```

**Windows**


With powershel. Make sure you in administrator mode.
```bash
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

or there is an install [here](https://pixi.sh/latest/installation/#__tabbed_1_2)


### 2. Running the init task

With pixi installed you can now run the init task. This will prompt you through steps to record metadata information about the project like the `PROJECT_NAME`, `PKG_NAME`, `PROJECT_DESCRIPTION`, and `AUTHORS_LIST`. It will then modify these through out the repository.


```bash
pixi run init
```


## Post Init Information

### Github pre-commit hooks  (lefthook)
The template repository should now be setup with your configuration and you should be able to start coding.

It is highly recommend to run the `pre-commit-install` task. This will setup `pre-commit` and 
`pre-push` git-hooks. Git-hooks are a mechanism which will run a script before any git action such as committing or push. If there is an error, it will prevent you from doing the action until the issue is resolved. Sometimes it will automatically fix this error if it is simple, but other times you need to make the changes. In the terminal it should tell you exactly what the errors are when you `git commit` or `git push`. If it doensn't, you can check all the checks these hooks are performing in `lefthook.yaml`. You can then go investigate these. This features will help ensure you are correctly following the groups linting and formatting rules for python files and toml files. You will have to meet these commands checks anyway when you do a pull request.

```bash 
pixi run pre-commit-install
```

### Type checking

We are using `basedpyright` to enforce on pre-pushes. It is highly recommended to set up your IDE with the basedpyright extension so you can see these errors in your ide. Your ide will then tell you what is the issue by highlighting it. To resolve these I would listen to their suggestion to try to solve it yourself or try AI to help you solve it. This will feel annoying at first, but it help your write better code.

The configurations for `basedpyright` are found in `pyproject.toml`. For your repo, you are more than welcome to change these settings. Some issues just can't be resolved too easily (This is usually when a variable is a generic type of variable), so you can ignore them  by using `# type:ignore`. 


### Tasks

There are many other tasks that can be used to help with your package such as linting, tests, builds, bumping version, and releases. You can list them with `pixi task list` and execute them with `pixi run {TASK_NAME}`. These are defined in `pixi.toml`

Here are some notable ones:

| Task Name            | Description                                   | Example Usage            |
|----------------------|-----------------------------------------------|--------------------------|
| init                 | Initialize project with metadata prompt       | `pixi run init`          |
| release              | Run the project release script.               | `pixi run release`       |
| bump                 | Bump patch version                            | `pixi run bump`          |
| build-release        | Build a release with hatch                    | `pixi run build-release` |
| test                 | Run all tests                                 | `pixi run test`          |
| test-torch-gpu       | Check PyTorch GPU environment info            | `pixi run test-torch-gpu`|
| test-specific        | Run a specific test with pytest               | `pixi run test-specific` |
| test-specific        | Run a specific test with pytest               | `pixi run test-specific` |
| lint-fast            | Run all fast linters/formatters (pre-commit)  | `pixi run lint-fast`     |
| lint-slow            | Run all slow linters/formatters (pre-push)    | `pixi run lint-slow`     |
| lint                 | Run all fast linters/formatters (pre-commit)  | `pixi run lint-fast`     |
| ruff-format          | Format code with ruff                         | `pixi run ruff-format`   |
| ruff-lint            | Lint and fix Python code with ruff            | `pixi run ruff-lint`     |
| toml-format          | Format TOML files with taplo                  | `pixi run toml-format`   |
| toml-lint            | Lint TOML files with taplo                    | `pixi run toml-lint`     |
| typecheck-python     | Type check Python with basedpyright           | `pixi run typecheck-python` |
| typos                | Check for typos in the codebase               | `pixi run typos`         |
| get-version          | Gets the `local` pkg version (`0.12.1.dev72`) | `pixi run get-version`   |


### Environments

We have also defined a preset of virtual environments to use. These can be used with your choice of IDE. 

To you them in pixi:

```bash
# Installs the virtual environmennt to .pixi/envs/{ENV}
pixi install -e {ENV}

pixi run -e {ENV} python -m release.py

# Creates a terminal hell with the environemtn
pixi shell -e {ENV}
```

Here is the list of the virtual environments.


| Task Name            | Description                                   | Example Usage            |
|----------------------|-----------------------------------------------|--------------------------|
| default              | Contains only packages for the feaures `default`, `build`, `dev`, `pytest`     | `pixi run {task or python}`,`pixi run -e default {task or python}`, `pixi shell`, `pixi shell -e default`         |
| docs                 | Contains packages for the `docs` feature     | `pixi run -e dev {task or python}`, `pixi shell -e dev`          |
| lint                 | Contains packages for the features: `lint`, `rust`,`pytest`, `build`, `llm`      | `pixi run -e lint {task or python}`, `pixi shell -e lint`          |
| dev                  | Contains packages for the features: `lint`, `rust`,`pytest`, `build`, `llm`, `PKG_NAME`      | `pixi run -e dev {task or python}`, `pixi shell -e dev`          |

### Devcontainers

If you are working with vscode or cursor. We have Dev containers set up with a developer environment with useful extensions and packages install. To use it you will need Docker installed and then install the `Dev Containers` Extension. Then in the lower left corner of your ide you can press `open remote window` button and open the folder in the container.
