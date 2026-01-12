"""Interactive initializer for customizing the project template."""

import atexit
import re
import shutil
import subprocess
from enum import Enum
from pathlib import Path


class Colors(str, Enum):
    """ANSI escape codes for consistent terminal prompts."""

    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"


status: list[str] = []


def colored_print(message: str, color: Colors) -> None:
    """Print a message with ANSI coloring.

    Parameters
    ----------
    message : str
        Text to display in the terminal.
    color : Colors
        Color enum describing the ANSI escape sequence to apply.
    """

    print(f"{color.value}{message}{Colors.RESET.value}")


def colored_input(prompt: str, color: Colors) -> str:
    """Prompt the user with colored text.

    Parameters
    ----------
    prompt : str
        Message displayed before reading input.
    color : Colors
        Color enum describing the ANSI escape sequence to apply.

    Returns
    -------
    str
        Raw input supplied by the user.
    """

    return input(f"{color.value}{prompt}{Colors.RESET.value}")


def print_summary() -> None:
    """Display a summary of the completed initialization steps."""

    colored_print("\nSummary of completed steps:", Colors.YELLOW)
    for step in status:
        colored_print(f"- {step}", Colors.YELLOW)


atexit.register(print_summary)


def get_project_name() -> str:
    """Prompt for and validate the project name.

    Returns
    -------
    str
        Repository name provided by the user.
    """
    while True:
        project_name = colored_input(
            "Enter the PROJECT_NAME (repository name, e.g., 'my-awesome-project'): ",
            Colors.MAGENTA,
        ).strip()
        if project_name:
            return project_name
        else:
            colored_print("Project name cannot be empty.", Colors.YELLOW)


def get_pkg_name() -> str:
    """Prompt for and validate the Python package name.

    Returns
    -------
    str
        Package name that satisfies standard Python module rules.
    """
    while True:
        pkg_name = colored_input(
            "Enter the PKG_NAME (Python package name, e.g., 'my_awesome_project'): ",
            Colors.MAGENTA,
        ).strip()
        if pkg_name:
            # Validate it's a valid Python package name
            if re.match(r"^[a-z_][a-z0-9_]*$", pkg_name):
                return pkg_name
            else:
                colored_print(
                    "Package name must be lowercase, start with a letter or underscore, "
                    + "and contain only letters, numbers, and underscores.",
                    Colors.YELLOW,
                )
        else:
            colored_print("Package name cannot be empty.", Colors.YELLOW)


def get_project_description() -> str:
    """Prompt for the single-line project description.

    Returns
    -------
    str
        Description entered by the user.
    """
    while True:
        description = colored_input(
            "Enter the PROJECT_DESCRIPTION (one-line description): ", Colors.MAGENTA
        ).strip()
        if description:
            return description
        else:
            colored_print("Project description cannot be empty.", Colors.YELLOW)


def get_authors() -> list[dict[str, str]]:
    """Collect author metadata for pyproject and pixi files.

    Returns
    -------
    list[dict[str, str]]
        List of dictionaries containing ``name`` and ``email`` keys.
    """
    while True:
        try:
            num_authors = int(colored_input("How many authors? ", Colors.MAGENTA).strip())
            if num_authors > 0:
                break
            else:
                colored_print("Number of authors must be at least 1.", Colors.YELLOW)
        except ValueError:
            colored_print("Please enter a valid number.", Colors.YELLOW)

    authors: list[dict[str, str]] = []
    for i in range(num_authors):
        colored_print(f"\nAuthor {i + 1}:", Colors.YELLOW)
        while True:
            name = colored_input("  Name: ", Colors.MAGENTA).strip()
            if name:
                break
            colored_print("  Name cannot be empty.", Colors.YELLOW)

        while True:
            email = colored_input("  Email: ", Colors.MAGENTA).strip()
            if email and "@" in email:
                break
            colored_print("  Please enter a valid email address.", Colors.YELLOW)

        authors.append({"name": name, "email": email})

    return authors


def get_github_owner_from_remote() -> str | None:
    """Attempt to extract GitHub owner from git remote origin.

    Returns
    -------
    str | None
        GitHub owner/organization name if detected, None otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Match SSH format: git@github.com:owner/repo.git
        ssh_match = re.match(r"git@github\.com:([^/]+)/", remote_url)
        if ssh_match:
            return ssh_match.group(1)

        # Match HTTPS format: https://github.com/owner/repo.git
        https_match = re.match(r"https://github\.com/([^/]+)/", remote_url)
        if https_match:
            return https_match.group(1)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None


def get_github_owner() -> str:
    """Get GitHub owner, auto-detecting from remote or prompting user.

    Returns
    -------
    str
        GitHub owner/organization name.
    """
    detected_owner = get_github_owner_from_remote()

    if detected_owner:
        colored_print(f"Detected GitHub owner from git remote: {detected_owner}", Colors.YELLOW)
        use_detected = colored_input(
            f"Use '{detected_owner}' as GitHub owner? (yes/no): ", Colors.MAGENTA
        ).lower()
        if use_detected in ["yes", "y"]:
            return detected_owner

    while True:
        owner = colored_input(
            "Enter the GITHUB_OWNER (GitHub username or organization): ",
            Colors.MAGENTA,
        ).strip()
        if owner:
            return owner
        colored_print("GitHub owner cannot be empty.", Colors.YELLOW)


def format_authors_toml(authors: list[dict[str, str]]) -> str:
    """Convert author dictionaries into a TOML array string.

    Parameters
    ----------
    authors : list[dict[str, str]]
        Author records with ``name`` and ``email`` keys.

    Returns
    -------
    str
        TOML formatted array suitable for ``pyproject.toml``.
    """
    author_strs: list[str] = []
    for author in authors:
        author_strs.append(f'{{name = "{author["name"]}", email = "{author["email"]}"}}')
    return "[" + ", ".join(author_strs) + "]"


def format_authors_pixi(authors: list[dict[str, str]]) -> str:
    """Convert author dictionaries into Pixi metadata format.

    Parameters
    ----------
    authors : list[dict[str, str]]
        Author records with ``name`` and ``email`` keys.

    Returns
    -------
    str
        Pixi-compatible string with ``Name <email>`` entries.
    """
    author_strs: list[str] = []
    for author in authors:
        author_strs.append(f'"{author["name"]} <{author["email"]}>"')
    return "[" + ", ".join(author_strs) + "]"


def update_file(filepath: Path, replacements: dict[str, str], description: str) -> None:
    """Apply string replacements to a file and record the status.

    Parameters
    ----------
    filepath : Path
        File to update.
    replacements : dict[str, str]
        Mapping of ``old`` -> ``new`` substrings to replace.
    description : str
        Status message appended to the global tracker.
    """
    colored_print(f"\nUpdating {filepath}...", Colors.YELLOW)
    content = filepath.read_text()

    for old, new in replacements.items():
        content = content.replace(old, new)

    filepath.write_text(content)
    status.append(description)
    colored_print(f"✓ Updated {filepath}", Colors.YELLOW)


def rename_directory(old_path: Path, new_path: Path, description: str) -> None:
    """Rename a directory and log the outcome.

    Parameters
    ----------
    old_path : Path
        Source directory path.
    new_path : Path
        Destination directory path.
    description : str
        Status message appended to the global tracker.
    """
    colored_print(f"\nRenaming {old_path} to {new_path}...", Colors.YELLOW)
    if old_path.exists():
        shutil.move(str(old_path), str(new_path))
        status.append(description)
        colored_print("✓ Renamed directory", Colors.YELLOW)
    else:
        colored_print(f"⚠ Directory {old_path} does not exist, skipping", Colors.YELLOW)


def main() -> None:
    """Interactively gather template values and update project files."""

    steps = [
        "Gather project information",
        "Update pyproject.toml",
        "Update pixi.toml",
        "Rename src/template_project/ directory",
        "Update .github/ISSUE_TEMPLATE/bug_report.yml",
        "Update .github/ISSUE_TEMPLATE/feature_request.yml",
        "Update README.md",
        "Update .config/tbump.toml",
        "Update scripts/PROMPT.md",
        "Complete initialization",
    ]

    colored_print("=" * 70, Colors.YELLOW)
    colored_print("Repository Template Initialization", Colors.YELLOW)
    colored_print("=" * 70, Colors.YELLOW)
    colored_print("\nThis script will initialize your repository template.", Colors.YELLOW)
    colored_print("You will be prompted for the following information:\n", Colors.YELLOW)
    for i, step in enumerate(steps, 1):
        colored_print(f"{i}. {step}", Colors.YELLOW)

    colored_print("\n" + "=" * 70 + "\n", Colors.YELLOW)

    try:
        # Step 1: Gather project information
        colored_print("Step 1: Gathering project information...\n", Colors.YELLOW)
        project_name = get_project_name()
        pkg_name = get_pkg_name()
        project_description = get_project_description()
        authors = get_authors()
        authors_toml = format_authors_toml(authors)
        authors_pixi = format_authors_pixi(authors)
        github_owner = get_github_owner()

        colored_print("\n" + "=" * 70, Colors.YELLOW)
        colored_print("Configuration Summary:", Colors.YELLOW)
        colored_print("=" * 70, Colors.YELLOW)
        colored_print(f"PROJECT_NAME: {project_name}", Colors.MAGENTA)
        colored_print(f"PKG_NAME: {pkg_name}", Colors.MAGENTA)
        colored_print(f"PROJECT_DESCRIPTION: {project_description}", Colors.MAGENTA)
        colored_print(f"AUTHORS (pyproject.toml): {authors_toml}", Colors.MAGENTA)
        colored_print(f"AUTHORS (pixi.toml): {authors_pixi}", Colors.MAGENTA)
        colored_print(f"GITHUB_OWNER: {github_owner}", Colors.MAGENTA)
        colored_print("=" * 70 + "\n", Colors.YELLOW)

        confirm = colored_input("Proceed with these settings? (yes/no): ", Colors.MAGENTA).lower()
        if confirm not in ["yes", "y"]:
            colored_print("Initialization cancelled.", Colors.YELLOW)
            return

        status.append("Gathered project information")

        # Get the repository root
        repo_root = Path(__file__).parent.parent.resolve()

        # Step 2: Update pyproject.toml
        colored_print("\nStep 2: Updating pyproject.toml...", Colors.YELLOW)
        pyproject_path = repo_root / "pyproject.toml"
        update_file(
            pyproject_path,
            {
                "authors = []": f"authors = {authors_toml}",
                "PROJECT_DESCRIPTION": project_description,
                "PROJECT_NAME": project_name,
                "src/template_project/_version.py": f"src/{pkg_name}/_version.py",
            },
            "Updated pyproject.toml",
        )

        # Step 3: Update pixi.toml
        colored_print("\nStep 3: Updating pixi.toml...", Colors.YELLOW)
        pixi_path = repo_root / "pixi.toml"
        content = pixi_path.read_text()

        # Replace all PKG_NAME occurrences
        content = content.replace('name = "template_project"', f'name = "{pkg_name}"')
        content = content.replace(
            "[feature.template_project.dependencies]", f"[feature.{pkg_name}.dependencies]"
        )
        content = content.replace(
            'template_project = { path = "." }', f'{pkg_name} = {{ path = "." }}'
        )
        content = content.replace('# "template_project"', f'"{pkg_name}"')
        content = content.replace('"template_project"', f'"{pkg_name}"')

        # Replace description
        content = re.sub(
            r'description = ".*?"', f'description = "{project_description}"', content, count=1
        )

        # Replace authors line using regex to handle any existing authors format
        content = re.sub(r"# AUTHORS_LIST", f"authors = {authors_pixi}", content, flags=re.DOTALL)

        pixi_path.write_text(content)
        status.append("Updated pixi.toml")
        colored_print(f"✓ Updated {pixi_path}", Colors.YELLOW)

        # Step 4: Rename src/PKG_NAME/ directory
        colored_print("\nStep 4: Renaming src/template_project/ directory...", Colors.YELLOW)
        old_pkg_dir = repo_root / "src" / "template_project"
        new_pkg_dir = repo_root / "src" / pkg_name
        rename_directory(old_pkg_dir, new_pkg_dir, f"Renamed directory to src/{pkg_name}/")

        # Step 5: Update .github/ISSUE_TEMPLATE/bug_report.yml
        colored_print("\nStep 5: Updating .github/ISSUE_TEMPLATE/bug_report.yml...", Colors.YELLOW)
        bug_report_path = repo_root / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"
        update_file(
            bug_report_path,
            {"PROJECT_NAME": project_name},
            "Updated .github/ISSUE_TEMPLATE/bug_report.yml",
        )

        # Step 6: Update .github/ISSUE_TEMPLATE/feature_request.yml
        colored_print(
            "\nStep 6: Updating .github/ISSUE_TEMPLATE/feature_request.yml...", Colors.YELLOW
        )
        feature_request_path = repo_root / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
        update_file(
            feature_request_path,
            {"PROJECT_NAME": project_name},
            "Updated .github/ISSUE_TEMPLATE/feature_request.yml",
        )

        # Step 7: Update README.md
        colored_print("\nStep 7: Updating README.md...", Colors.YELLOW)
        readme_path = repo_root / "README.md"
        update_file(
            readme_path,
            {"PROJECT_NAME": project_name},
            "Updated README.md",
        )

        # Step 8: Update tbump.toml
        colored_print("\nStep 8: Updating tbump.toml...", Colors.YELLOW)
        tbump_path = repo_root / ".config" / "tbump.toml"
        content = tbump_path.read_text()
        # Update the github_url to use the project name
        content = re.sub(
            r'github_url = "https://github\.com/([^/]+)/[^"]+"',
            f'github_url = "https://github.com/\\1/{project_name}"',
            content,
        )
        tbump_path.write_text(content)
        status.append("Updated tbump.toml")
        colored_print(f"✓ Updated {tbump_path}", Colors.YELLOW)

        # Step 9: Update scripts/PROMPT.md
        colored_print("\nStep 9: Updating scripts/PROMPT.md...", Colors.YELLOW)
        prompt_md_path = repo_root / "scripts" / "PROMPT.md"
        if prompt_md_path.exists():
            update_file(
                prompt_md_path,
                {
                    "GITHUB_OWNER": github_owner,
                    "PROJECT_NAME": project_name,
                },
                "Updated scripts/PROMPT.md",
            )
        else:
            colored_print(f"⚠ File {prompt_md_path} does not exist, skipping", Colors.YELLOW)

        # Step 10: Complete
        colored_print("\n" + "=" * 70, Colors.YELLOW)
        colored_print("✓ Initialization complete!", Colors.YELLOW)
        colored_print("=" * 70, Colors.YELLOW)
        status.append("Repository initialization completed successfully")

    except KeyboardInterrupt:
        colored_print("\n\nInitialization interrupted.", Colors.YELLOW)
    except Exception as e:
        colored_print(f"\n\nError during initialization: {e}", Colors.YELLOW)
        raise


if __name__ == "__main__":
    main()
