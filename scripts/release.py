"""Interactive helper for orchestrating the release workflow."""

import atexit
import os
import re
import subprocess
from enum import Enum
from pathlib import Path


class Colors(str, Enum):
    """ANSI escape codes for highlighting terminal prompts and messages."""

    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"


status: list[str] = []


def colored_print(message: str, color: Colors) -> None:
    """Print a message using the provided ANSI color.

    Parameters
    ----------
    message : str
        Text to display in the terminal.
    color : Colors
        Color enum describing the ANSI escape sequence to apply.
    """

    print(f"{color.value}{message}{Colors.RESET.value}")


def colored_input(prompt: str, color: Colors) -> str:
    """Prompt for user input using the provided ANSI color.

    Parameters
    ----------
    prompt : str
        Text shown to the user before the input cursor.
    color : Colors
        Color enum describing the ANSI escape sequence to apply.

    Returns
    -------
    str
        User-provided response as a raw string.
    """

    return input(f"{color.value}{prompt}{Colors.RESET.value}")


def run_command(command: list[str | Path], capture_stdout: bool = False) -> str | None:
    """Execute a shell command and optionally capture its stdout.

    Parameters
    ----------
    command : list[str | Path]
        Command and arguments to execute.
    capture_stdout : bool, optional
        Whether to capture and return stdout, by default False.

    Returns
    -------
    str | None
        Captured stdout with leading/trailing spaces removed when
        `capture_stdout` is True, otherwise None.
    """

    colored_print(f"Running command: {' '.join([str(c) for c in command])}", Colors.YELLOW)
    result = subprocess.run(
        command, stdout=subprocess.PIPE if capture_stdout else None, stderr=None, text=True
    )
    if result.returncode != 0:
        colored_print(f"Error running command: {' '.join(map(str, command))}", Colors.YELLOW)
        exit(result.returncode)
    if capture_stdout:
        return result.stdout.strip()
    return None


def get_release_version() -> str:
    """Prompt the user for a semantic version string.

    Returns
    -------
    str
        Validated release version in the form ``X.Y.Z`` where each
        segment is an integer.
    """

    pattern = re.compile(r"^\d+\.\d+\.\d+$")
    version_from_env = os.environ.get("RELEASE_VERSION")

    if version_from_env and pattern.match(version_from_env):
        default_version = version_from_env
    else:
        default_version = ""

    while True:
        prompt = (
            f"Enter the release version (X.Y.Z) [{default_version}]: "
            if default_version
            else "Enter the release version (X.Y.Z): "
        )
        release_version = colored_input(prompt, Colors.MAGENTA) or default_version
        if pattern.match(release_version):
            return release_version
        colored_print(
            (
                "Invalid format. Please enter the version in the format X.Y.Z where X, Y, and Z"
                "are integers."
            ),
            Colors.YELLOW,
        )


def get_pixi() -> Path:
    """Locate the pixi executable used for project automation.

    Returns
    -------
    Path
        Absolute path to the pixi binary within the user cache.

    Raises
    ------
    ValueError
        If the binary cannot be found on disk.
    """

    pixi_bin = Path().home().joinpath(".pixi/bin/pixi").resolve()

    if pixi_bin.is_file() and pixi_bin.exists():
        return pixi_bin
    raise ValueError(f"The path {pixi_bin} doesn't exist.")


def print_summary() -> None:
    """Display a summary of completed release steps."""

    colored_print("\nSummary of completed steps:", Colors.YELLOW)
    for step in status:
        colored_print(f"- {step}", Colors.YELLOW)


atexit.register(print_summary)


def main() -> None:
    """Interactively guide the maintainer through the release checklist."""

    steps = [
        "Start release process",
        "Check main branch and CI status",
        "Set release version",
        "Create and switch to release branch",
        "Bump all versions",
        "Update Pixi lockfile",
        "Update changelog",
        "Lint changes",
        "Commit changes",
        "Push changes",
        "Create and merge release prep PR",
    ]

    colored_print("Select the step to start from:", Colors.YELLOW)
    for i, step in enumerate(steps, 1):
        colored_print(f"{i}. {step}", Colors.YELLOW)

    while True:
        try:
            start_step = int(colored_input("Enter the step number: ", Colors.MAGENTA))
            if 1 <= start_step <= len(steps):
                break
            else:
                colored_print("Invalid step number. Please enter a valid number.", Colors.YELLOW)
        except ValueError:
            colored_print("Invalid input. Please enter a number.", Colors.YELLOW)

    pixi = get_pixi()

    step = 1
    try:
        if start_step <= 1:
            colored_print(f"{step}. Making a release of pixi", Colors.YELLOW)
            status.append("Started release process")
            step += 1

        if start_step <= 2:
            colored_input(
                f"{step}. Make sure main is up-to-date and CI passes. Press Enter to continue...",
                Colors.MAGENTA,
            )
            status.append("Checked main branch and CI status")
            step += 1

        release_version = get_release_version()
        os.environ["RELEASE_VERSION"] = release_version
        status.append(f"Release version set to {release_version}")
        step += 1

        if start_step <= 4:
            colored_print(f"\n{step}. Creating a new branch for the release...", Colors.YELLOW)
            run_command(["git", "checkout", "main"])
            run_command(["git", "pull", "origin", "main"])
            branch = f"bump/prepare-v{release_version}"

            branch_exists = run_command(["git", "branch", "--list", branch], capture_stdout=True)
            if branch_exists:
                run_command(["git", "branch", "--delete", branch])
            run_command(["git", "switch", "--create", branch])
            status.append(f"Created and switched to branch {branch}")
            step += 1

        # if start_step <= 5:
        #     # colored_print(f"\n{step}. Bumping all versions...", Colors.YELLOW)
        #     # run_command([pixi, "run", "bump"])
        #     # status.append("Bumped all versions")
        #     # step += 1

        #     colored_print(f"\n{step}. Creating version tag...", Colors.YELLOW)
        #     tag_name = f"v{release_version}"

        # run_command(["git", "tag", "-a", tag_name, "-m", f"Release {release_version}"])

        # Verify version using hatchling
        # try:
        #     version_output = run_command(
        #         [pixi, "run", "python", "-c",
        #         ("from hatchling.version.source.vcs import VCSVersionSource; "
        #         "print(VCSVersionSource('.', {}).get_version_data()['version'])")],
        #         capture_stdout=True
        #     )
        #     colored_print(f"✓ Verified version from tag: {version_output}", Colors.YELLOW)

        #     if version_output != release_version:
        #         colored_print(
        #             (f"⚠ Warning: Tag version ({version_output}) doesn't match "
        #              "expected ({release_version})"),
        #             Colors.YELLOW
        #         )

        #     raise ValueError( (f"Tag version ({version_output}) doesn't "
        #                       "match expected ({release_version}) ") )
        # except Exception as e:
        #     colored_print(f"⚠ Could not verify version: {e}", Colors.YELLOW)

        # status.append(f"Created tag {tag_name}")
        # step += 1

        if start_step <= 5:
            colored_print(f"\n{step}. Bumping all versions...", Colors.YELLOW)
            run_command([pixi, "run", "bump"])
            status.append("Bumped all versions")
            step += 1

        if start_step <= 6:
            colored_print(f"\n{step}. Update Pixi lockfile...", Colors.YELLOW)
            # run_command([pixi, "update"])
            # status.append("Updated all lockfile")
            step += 1

        if start_step <= 7:
            while True:
                response = (
                    colored_input(
                        f"{step}. Should we bump the changelog? (yes/no): ", Colors.MAGENTA
                    )
                    .strip()
                    .lower()
                )
                if response.lower() in ["yes", "no", "y", "n"]:
                    break
                else:
                    colored_print("Invalid response. Please enter 'yes' or 'no'.", Colors.YELLOW)
            if response == "yes" or response == "y":
                run_command([pixi, "run", "bump-changelog"])
            colored_input(
                (
                    "Don't forget to update the 'Highlights' section in `CHANGELOG.md`."
                    "Press Enter to continue..."
                ),
                Colors.MAGENTA,
            )
            status.append("Updated the changelog")
            step += 1

        if start_step <= 8:
            colored_print(f"\n{step}. Linting the changes...", Colors.YELLOW)
            run_command([pixi, "run", "lint"])
            step += 1

        if start_step <= 9:
            colored_print(f"\n{step}. Committing the changes...", Colors.YELLOW)
            run_command(["git", "commit", "-am", f"chore: version to {release_version}"])
            status.append("Committed the changes")
            step += 1

        if start_step <= 10:
            colored_print(f"\n{step}. Pushing the changes...", Colors.YELLOW)
            run_command(
                ["git", "push", "--set-upstream", "origin", f"bump/prepare-v{release_version}"]
            )
            status.append("Pushed the changes")
            step += 1

        if start_step <= 11:
            colored_print(f"\n{step}. Release prep PR", Colors.YELLOW)
            colored_input(
                "Create a PR to check off the change with the peers. Press Enter to continue...",
                Colors.MAGENTA,
            )
            colored_input("Merge that PR. Press Enter to continue...", Colors.MAGENTA)
            status.append("Created and merged the release prep PR")
            step += 1

        colored_print(
            (
                f"\nStart a release build for 'v{release_version}' "
                "by starting the workflow manually in "
                "https://github.com/prefix-dev/pixi/actions/workflows/release.yml"
            ),
            Colors.YELLOW,
        )

        colored_print("\nDONE!", Colors.YELLOW)
        status.append("Release process completed successfully")

    except KeyboardInterrupt:
        colored_print("\nProcess interrupted.", Colors.YELLOW)


if __name__ == "__main__":
    main()
