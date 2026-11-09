#!/usr/bin/env python3
"""
detect-project.py - Foundational Project Detection Utility for vibe-coding-og.

Analyzes a project directory to detect programming languages, frameworks,
package managers, build systems, manifests, and git status.

Standard library only. Cross-platform (Windows & Linux).
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set


def sanitize_git_url(url: str) -> str:
    """Remove embedded credentials or tokens from git remote URLs."""
    if not url:
        return ""
    # Matches http://user:pass@host or https://token@host
    return re.sub(r'(https?://)[^/@]+@', r'\1', url.strip())


def get_git_info(project_dir: Path) -> Dict[str, Any]:
    """Retrieve Git repository status using git CLI or .git directory inspection."""
    git_info: Dict[str, Any] = {
        "is_git_repo": False,
        "branch": None,
        "commit_hash": None,
        "is_clean": None,
        "remote_url": None,
    }

    git_dir = project_dir / ".git"
    if not git_dir.exists():
        # Check if parent is git worktree
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res.returncode != 0:
                return git_info
        except Exception:
            return git_info

    git_info["is_git_repo"] = True

    # Try using git CLI first if available
    git_bin = shutil.which("git")
    if git_bin:
        try:
            # Branch
            res_branch = subprocess.run(
                [git_bin, "branch", "--show-current"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res_branch.returncode == 0 and res_branch.stdout.strip():
                git_info["branch"] = res_branch.stdout.strip()

            # Commit hash
            res_hash = subprocess.run(
                [git_bin, "rev-parse", "--short", "HEAD"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res_hash.returncode == 0 and res_hash.stdout.strip():
                git_info["commit_hash"] = res_hash.stdout.strip()

            # Clean/dirty status
            res_status = subprocess.run(
                [git_bin, "status", "--porcelain"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res_status.returncode == 0:
                git_info["is_clean"] = len(res_status.stdout.strip()) == 0

            # Remote URL (sanitized)
            res_remote = subprocess.run(
                [git_bin, "config", "--get", "remote.origin.url"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res_remote.returncode == 0 and res_remote.stdout.strip():
                git_info["remote_url"] = sanitize_git_url(res_remote.stdout)
            return git_info
        except Exception:
            pass

    # Fallback to direct inspection of .git/HEAD
    head_file = git_dir / "HEAD"
    if head_file.is_file():
        try:
            content = head_file.read_text(encoding="utf-8", errors="ignore").strip()
            if content.startswith("ref: refs/heads/"):
                git_info["branch"] = content.replace("ref: refs/heads/", "").strip()
            elif len(content) in (40, 64):
                git_info["commit_hash"] = content[:7]
        except Exception:
            pass

    return git_info


def read_text_safe(path: Path, max_bytes: int = 100_000) -> str:
    """Read a text file safely up to max_bytes."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def detect_java_project(project_dir: Path) -> Dict[str, Any]:
    """Detect Java, Spring Boot, Maven, and Gradle components."""
    data: Dict[str, Any] = {
        "languages": [],
        "frameworks": [],
        "package_managers": [],
        "build_systems": [],
        "manifests": [],
        "config_files": [],
        "directories": [],
    }

    pom_xml = project_dir / "pom.xml"
    build_gradle = project_dir / "build.gradle"
    build_gradle_kts = project_dir / "build.gradle.kts"
    mvnw = project_dir / "mvnw"
    mvnw_cmd = project_dir / "mvnw.cmd"
    gradlew = project_dir / "gradlew"
    gradlew_cmd = project_dir / "gradlew.cmd"

    has_java_files = (
        pom_xml.exists()
        or build_gradle.exists()
        or build_gradle_kts.exists()
        or (project_dir / "src" / "main" / "java").exists()
    )

    if not has_java_files:
        return data

    data["languages"].append("Java")

    # Maven detection
    if pom_xml.exists():
        data["manifests"].append("pom.xml")
        data["build_systems"].append("Maven")
        data["package_managers"].append("Maven")
        pom_content = read_text_safe(pom_xml)
        if "spring-boot" in pom_content:
            data["frameworks"].append("Spring Boot")
        if "quarkus" in pom_content.lower():
            data["frameworks"].append("Quarkus")
        if "micronaut" in pom_content.lower():
            data["frameworks"].append("Micronaut")

    # Gradle detection
    if build_gradle.exists() or build_gradle_kts.exists():
        if build_gradle.exists():
            data["manifests"].append("build.gradle")
            gradle_content = read_text_safe(build_gradle)
        else:
            data["manifests"].append("build.gradle.kts")
            gradle_content = read_text_safe(build_gradle_kts)

        data["build_systems"].append("Gradle")
        data["package_managers"].append("Gradle")
        if "org.springframework.boot" in gradle_content or "spring-boot" in gradle_content:
            data["frameworks"].append("Spring Boot")
        if "io.quarkus" in gradle_content:
            data["frameworks"].append("Quarkus")

    # Wrappers
    if mvnw.exists() or mvnw_cmd.exists():
        data["config_files"].append("mvnw" if mvnw.exists() else "mvnw.cmd")
    if gradlew.exists() or gradlew_cmd.exists():
        data["config_files"].append("gradlew" if gradlew.exists() else "gradlew.cmd")

    # Spring Boot config files
    resources_dir = project_dir / "src" / "main" / "resources"
    for cfg in ("application.properties", "application.yml", "application.yaml", "bootstrap.yml"):
        if (resources_dir / cfg).exists():
            data["config_files"].append(f"src/main/resources/{cfg}")
        elif (project_dir / cfg).exists():
            data["config_files"].append(cfg)

    # Standard Java directories
    for d in ("src/main/java", "src/test/java", "src/main/resources", "src/test/resources"):
        if (project_dir / Path(d)).exists():
            data["directories"].append(d)

    return data


def detect_python_project(project_dir: Path) -> Dict[str, Any]:
    """Detect Python, FastAPI, Flask, Django, and pytest components."""
    data: Dict[str, Any] = {
        "languages": [],
        "frameworks": [],
        "package_managers": [],
        "build_systems": [],
        "manifests": [],
        "config_files": [],
        "directories": [],
    }

    manifest_names = [
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "Pipfile.lock",
        "poetry.lock",
        "uv.lock",
    ]

    found_manifests = [m for m in manifest_names if (project_dir / m).exists()]

    # Also detect if any .py files in root or src/
    has_py_files = bool(found_manifests) or any(project_dir.glob("*.py"))
    if not has_py_files:
        return data

    data["languages"].append("Python")
    data["manifests"].extend(found_manifests)

    # Package manager and build system detection
    if "poetry.lock" in found_manifests or (
        "pyproject.toml" in found_manifests
        and "tool.poetry" in read_text_safe(project_dir / "pyproject.toml")
    ):
        data["package_managers"].append("Poetry")
        data["build_systems"].append("Poetry")
    elif "Pipfile" in found_manifests or "Pipfile.lock" in found_manifests:
        data["package_managers"].append("Pipenv")
    elif "uv.lock" in found_manifests:
        data["package_managers"].append("uv")
    else:
        data["package_managers"].append("pip")

    if "setup.py" in found_manifests or "setup.cfg" in found_manifests:
        data["build_systems"].append("setuptools")
    if "pyproject.toml" in found_manifests and "build_systems" not in data:
        pyproj = read_text_safe(project_dir / "pyproject.toml")
        if "hatchling" in pyproj:
            data["build_systems"].append("Hatch")
        elif "flit" in pyproj:
            data["build_systems"].append("Flit")

    # Framework detection by inspecting dependencies in manifests
    all_dep_text = ""
    for m in ("requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"):
        if m in found_manifests:
            all_dep_text += "\n" + read_text_safe(project_dir / m).lower()

    if re.search(r'\bfastapi\b', all_dep_text):
        data["frameworks"].append("FastAPI")
    if re.search(r'\bflask\b', all_dep_text):
        data["frameworks"].append("Flask")
    if re.search(r'\bdjango\b', all_dep_text):
        data["frameworks"].append("Django")
    if re.search(r'\bpytest\b', all_dep_text):
        data["frameworks"].append("pytest")

    # Config files
    for cfg in ("pytest.ini", "tox.ini", ".flake8", ".pylintrc", "ruff.toml", ".ruff.toml"):
        if (project_dir / cfg).exists():
            data["config_files"].append(cfg)

    # Standard python directories
    for d in ("src", "app", "tests", "test"):
        if (project_dir / d).is_dir():
            data["directories"].append(d)

    return data


def detect_node_project(project_dir: Path) -> Dict[str, Any]:
    """Detect Node.js, JavaScript, TypeScript, React, Next.js, and package managers."""
    data: Dict[str, Any] = {
        "languages": [],
        "frameworks": [],
        "package_managers": [],
        "build_systems": [],
        "manifests": [],
        "config_files": [],
        "directories": [],
    }

    pkg_json = project_dir / "package.json"
    tsconfig = project_dir / "tsconfig.json"
    jsconfig = project_dir / "jsconfig.json"

    if not pkg_json.exists() and not tsconfig.exists() and not jsconfig.exists():
        return data

    if pkg_json.exists():
        data["manifests"].append("package.json")

    # Language detection
    has_ts = tsconfig.exists() or any(project_dir.glob("*.ts")) or any(project_dir.glob("*.tsx"))
    if (project_dir / "src").is_dir():
        has_ts = has_ts or any((project_dir / "src").glob("**/*.ts"))

    if has_ts:
        data["languages"].append("TypeScript")
    data["languages"].append("JavaScript")
    data["languages"].append("Node.js")

    # Package managers by lockfile
    if (project_dir / "pnpm-lock.yaml").exists():
        data["package_managers"].append("pnpm")
        data["config_files"].append("pnpm-lock.yaml")
    elif (project_dir / "yarn.lock").exists():
        data["package_managers"].append("yarn")
        data["config_files"].append("yarn.lock")
    elif (project_dir / "bun.lockb").exists() or (project_dir / "bun.lock").exists():
        data["package_managers"].append("bun")
        data["config_files"].append("bun.lockb" if (project_dir / "bun.lockb").exists() else "bun.lock")
    elif (project_dir / "package-lock.json").exists():
        data["package_managers"].append("npm")
        data["config_files"].append("package-lock.json")
    else:
        data["package_managers"].append("npm")

    # Parse package.json for frameworks and build systems
    if pkg_json.exists():
        try:
            content = read_text_safe(pkg_json)
            parsed = json.loads(content) if content else {}
            deps = parsed.get("dependencies", {})
            dev_deps = parsed.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            if "next" in all_deps:
                data["frameworks"].append("Next.js")
            if "react" in all_deps:
                data["frameworks"].append("React")
            if "vue" in all_deps:
                data["frameworks"].append("Vue")
            if "svelte" in all_deps:
                data["frameworks"].append("Svelte")
            if "express" in all_deps:
                data["frameworks"].append("Express")
            if "@nestjs/core" in all_deps:
                data["frameworks"].append("NestJS")

            # Build tools
            if "vite" in all_deps:
                data["build_systems"].append("Vite")
            if "next" in all_deps and "Next.js" not in data["build_systems"]:
                data["build_systems"].append("Next.js Build")
            if "webpack" in all_deps:
                data["build_systems"].append("Webpack")
            if "esbuild" in all_deps:
                data["build_systems"].append("esbuild")
        except Exception:
            pass

    # Config files
    configs_to_check = [
        "tsconfig.json",
        "jsconfig.json",
        "next.config.js",
        "next.config.mjs",
        "next.config.ts",
        "vite.config.js",
        "vite.config.ts",
        "webpack.config.js",
        "tailwind.config.js",
        "tailwind.config.ts",
        "postcss.config.js",
        ".eslintrc.json",
        ".eslintrc.js",
        "eslint.config.js",
        "eslint.config.mjs",
    ]
    for cfg in configs_to_check:
        if (project_dir / cfg).exists():
            data["config_files"].append(cfg)

    # Directories
    for d in ("src", "app", "pages", "components", "public", "tests", "test", "node_modules"):
        if (project_dir / d).is_dir():
            data["directories"].append(d)

    return data


def detect_project(project_path: Path) -> Dict[str, Any]:
    """Perform full project detection for the given path."""
    project_path = project_path.resolve()

    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    git_info = get_git_info(project_path)
    java_data = detect_java_project(project_path)
    python_data = detect_python_project(project_path)
    node_data = detect_node_project(project_path)

    # Deduplicate and aggregate
    languages = sorted(list(set(java_data["languages"] + python_data["languages"] + node_data["languages"])))
    frameworks = sorted(list(set(java_data["frameworks"] + python_data["frameworks"] + node_data["frameworks"])))
    package_managers = sorted(list(set(java_data["package_managers"] + python_data["package_managers"] + node_data["package_managers"])))
    build_systems = sorted(list(set(java_data["build_systems"] + python_data["build_systems"] + node_data["build_systems"])))
    manifests = sorted(list(set(java_data["manifests"] + python_data["manifests"] + node_data["manifests"])))
    config_files = sorted(list(set(java_data["config_files"] + python_data["config_files"] + node_data["config_files"])))
    directories = sorted(list(set(java_data["directories"] + python_data["directories"] + node_data["directories"])))

    # Determine primary type
    primary_language = languages[0] if languages else "Generic / Unknown"

    result = {
        "project_name": project_path.name,
        "project_path": str(project_path),
        "primary_language": primary_language,
        "languages": languages,
        "frameworks": frameworks,
        "package_managers": package_managers,
        "build_systems": build_systems,
        "manifests": manifests,
        "config_files": config_files,
        "main_directories": directories,
        "git": git_info,
    }

    return result


def format_human_readable(data: Dict[str, Any]) -> str:
    """Format detection report for readable terminal output."""
    lines: List[str] = []
    lines.append("==================================================")
    lines.append(f" Project Detection: {data['project_name']}")
    lines.append("==================================================")
    lines.append(f"Path:             {data['project_path']}")
    lines.append(f"Primary Stack:    {data['primary_language']}")
    lines.append(f"Languages:        {', '.join(data['languages']) if data['languages'] else 'None detected'}")
    lines.append(f"Frameworks:       {', '.join(data['frameworks']) if data['frameworks'] else 'None detected'}")
    lines.append(f"Package Managers: {', '.join(data['package_managers']) if data['package_managers'] else 'None detected'}")
    lines.append(f"Build Systems:    {', '.join(data['build_systems']) if data['build_systems'] else 'None detected'}")
    lines.append("")
    lines.append("Project Manifests:")
    if data["manifests"]:
        for m in data["manifests"]:
            lines.append(f"  • {m}")
    else:
        lines.append("  (None detected)")

    lines.append("")
    lines.append("Configuration Files:")
    if data["config_files"]:
        for c in data["config_files"]:
            lines.append(f"  • {c}")
    else:
        lines.append("  (None detected)")

    lines.append("")
    lines.append("Main Directories:")
    if data["main_directories"]:
        for d in data["main_directories"]:
            lines.append(f"  📁 {d}")
    else:
        lines.append("  (None detected)")

    lines.append("")
    lines.append("Git Repository Status:")
    git = data["git"]
    lines.append(f"  Is Git Repo:    {'Yes' if git['is_git_repo'] else 'No'}")
    if git["is_git_repo"]:
        lines.append(f"  Branch:         {git['branch'] or 'N/A'}")
        lines.append(f"  Commit:         {git['commit_hash'] or 'N/A'}")
        lines.append(f"  Clean:          {'Yes' if git['is_clean'] else 'No (uncommitted changes)' if git['is_clean'] is False else 'Unknown'}")
        if git["remote_url"]:
            lines.append(f"  Remote:         {git['remote_url']}")
    lines.append("==================================================")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect programming languages, frameworks, package managers, and structure of a project."
    )
    parser.add_argument(
        "--path",
        "-p",
        default=".",
        help="Path to the project directory to inspect (default: current working directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the detection results as JSON.",
    )

    args = parser.parse_args()

    try:
        project_dir = Path(args.path)
        data = detect_project(project_dir)

        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_human_readable(data))
        return 0
    except (FileNotFoundError, NotADirectoryError) as err:
        error_payload = {"error": str(err), "exit_code": 1}
        if args.json:
            print(json.dumps(error_payload, indent=2), file=sys.stderr)
        else:
            print(f"Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        error_payload = {"error": f"Unexpected error: {err}", "exit_code": 1}
        if args.json:
            print(json.dumps(error_payload, indent=2), file=sys.stderr)
        else:
            print(f"Error: Unexpected error during detection: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
