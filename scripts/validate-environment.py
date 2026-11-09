#!/usr/bin/env python3
"""
validate-environment.py - Environment & Toolchain Validation Utility for vibe-coding-og.

Validates required runtimes, package managers, git availability, project configuration,
and detects missing dependencies for the active project.

Security: Never exposes environment variables, secrets, or credential files.
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
from typing import Any, Dict, List, Optional, Tuple


def get_tool_version(binary_name: str, version_arg: str = "--version") -> Optional[str]:
    """Safely check if a binary exists in PATH and retrieve its version string."""
    binary_path = shutil.which(binary_name)
    if not binary_path:
        return None

    try:
        res = subprocess.run(
            [binary_path, version_arg],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        output = (res.stdout or res.stderr).strip()
        if output:
            # Extract first line of version output
            first_line = output.splitlines()[0].strip()
            return first_line
        return "Installed"
    except Exception:
        return "Installed (version unavailable)"


def check_git_readiness(project_dir: Path) -> Dict[str, Any]:
    """Check Git installation and configuration without revealing user identity."""
    git_bin = shutil.which("git")
    if not git_bin:
        return {
            "installed": False,
            "version": None,
            "user_configured": False,
            "status": "missing",
        }

    git_ver = get_tool_version("git", "--version")
    user_configured = False

    try:
        res_name = subprocess.run(
            [git_bin, "config", "--get", "user.name"],
            cwd=str(project_dir) if project_dir.exists() else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        res_email = subprocess.run(
            [git_bin, "config", "--get", "user.email"],
            cwd=str(project_dir) if project_dir.exists() else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        user_configured = bool(res_name.stdout.strip() and res_email.stdout.strip())
    except Exception:
        user_configured = False

    return {
        "installed": True,
        "version": git_ver,
        "user_configured": user_configured,
        "status": "ready" if user_configured else "warning (user.name/email not set)",
    }


def check_runtimes() -> Dict[str, Dict[str, Any]]:
    """Inspect system runtimes (Python, Node.js, Java)."""
    runtimes = {}

    # Python
    py_ver = f"Python {sys.version.split()[0]}"
    runtimes["python"] = {
        "name": "Python",
        "installed": True,
        "version": py_ver,
        "executable": sys.executable,
    }

    # Node.js
    node_bin = shutil.which("node")
    node_ver = get_tool_version("node", "--version") if node_bin else None
    runtimes["node"] = {
        "name": "Node.js",
        "installed": bool(node_bin),
        "version": node_ver,
        "executable": node_bin,
    }

    # Java
    java_bin = shutil.which("java")
    java_ver = get_tool_version("java", "-version") if java_bin else None
    runtimes["java"] = {
        "name": "Java (JDK/JRE)",
        "installed": bool(java_bin),
        "version": java_ver,
        "executable": java_bin,
    }

    return runtimes


def check_package_managers() -> Dict[str, Dict[str, Any]]:
    """Inspect availability of common package managers."""
    pm_list = [
        ("npm", "--version"),
        ("pnpm", "--version"),
        ("yarn", "--version"),
        ("pip", "--version"),
        ("poetry", "--version"),
        ("uv", "--version"),
        ("mvn", "--version"),
        ("gradle", "--version"),
    ]

    results = {}
    for pm, arg in pm_list:
        binary_path = shutil.which(pm)
        version = get_tool_version(pm, arg) if binary_path else None
        results[pm] = {
            "name": pm,
            "installed": bool(binary_path),
            "version": version,
        }
    return results


def validate_project_dependencies(project_dir: Path) -> List[Dict[str, str]]:
    """Identify missing runtimes, build tools, or local dependency directories."""
    issues: List[Dict[str, str]] = []

    # 1. Node.js project checks
    pkg_json = project_dir / "package.json"
    if pkg_json.exists():
        # Check Node.js
        if not shutil.which("node"):
            issues.append({
                "severity": "error",
                "category": "runtime",
                "message": "Node.js project detected (package.json exists), but 'node' runtime is not found in PATH.",
            })

        # Check package manager
        has_pnpm = (project_dir / "pnpm-lock.yaml").exists()
        has_yarn = (project_dir / "yarn.lock").exists()
        if has_pnpm and not shutil.which("pnpm"):
            issues.append({
                "severity": "warning",
                "category": "package_manager",
                "message": "Project uses pnpm (pnpm-lock.yaml present), but 'pnpm' is not installed in PATH.",
            })
        elif has_yarn and not shutil.which("yarn"):
            issues.append({
                "severity": "warning",
                "category": "package_manager",
                "message": "Project uses yarn (yarn.lock present), but 'yarn' is not installed in PATH.",
            })

        # Check node_modules
        node_modules = project_dir / "node_modules"
        if not node_modules.is_dir():
            issues.append({
                "severity": "error",
                "category": "dependencies",
                "message": "Dependencies directory 'node_modules/' is missing. Run your package manager install command.",
            })

    # 2. Python project checks
    has_py_manifest = any(
        (project_dir / m).exists()
        for m in ("pyproject.toml", "requirements.txt", "Pipfile", "setup.py")
    )
    if has_py_manifest:
        # Check virtualenv presence
        in_virtualenv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        local_venv_dirs = [d for d in (".venv", "venv", "env", "ENV") if (project_dir / d).is_dir()]

        if not in_virtualenv and not local_venv_dirs:
            issues.append({
                "severity": "warning",
                "category": "environment",
                "message": "Python project detected, but no local virtual environment (.venv/ or venv/) or active virtual environment found.",
            })

        # Poetry check
        if (project_dir / "poetry.lock").exists() and not shutil.which("poetry"):
            issues.append({
                "severity": "warning",
                "category": "package_manager",
                "message": "Project uses Poetry (poetry.lock present), but 'poetry' CLI is not found in PATH.",
            })

        # Pipenv check
        if (project_dir / "Pipfile").exists() and not shutil.which("pipenv"):
            issues.append({
                "severity": "warning",
                "category": "package_manager",
                "message": "Project uses Pipenv (Pipfile present), but 'pipenv' CLI is not found in PATH.",
            })

    # 3. Java project checks
    pom_xml = project_dir / "pom.xml"
    build_gradle = project_dir / "build.gradle"
    build_gradle_kts = project_dir / "build.gradle.kts"

    if pom_xml.exists() or build_gradle.exists() or build_gradle_kts.exists():
        if not shutil.which("java"):
            issues.append({
                "severity": "error",
                "category": "runtime",
                "message": "Java project detected, but 'java' runtime (JDK) is not found in PATH.",
            })

        if pom_xml.exists():
            has_mvn = bool(shutil.which("mvn"))
            has_mvnw = (project_dir / "mvnw").exists() or (project_dir / "mvnw.cmd").exists()
            if not has_mvn and not has_mvnw:
                issues.append({
                    "severity": "error",
                    "category": "build_system",
                    "message": "Maven project detected, but neither 'mvn' in PATH nor Maven wrapper (mvnw) is present.",
                })

        if build_gradle.exists() or build_gradle_kts.exists():
            has_gradle = bool(shutil.which("gradle"))
            has_gradlew = (project_dir / "gradlew").exists() or (project_dir / "gradlew.cmd").exists()
            if not has_gradle and not has_gradlew:
                issues.append({
                    "severity": "error",
                    "category": "build_system",
                    "message": "Gradle project detected, but neither 'gradle' in PATH nor Gradle wrapper (gradlew) is present.",
                })

    return issues


def validate_environment(project_path: Path) -> Dict[str, Any]:
    """Perform full environment validation."""
    project_path = project_path.resolve()

    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    git_status = check_git_readiness(project_path)
    runtimes = check_runtimes()
    package_managers = check_package_managers()
    issues = validate_project_dependencies(project_path)

    has_errors = any(i["severity"] == "error" for i in issues)
    has_warnings = any(i["severity"] == "warning" for i in issues)

    if has_errors:
        overall_status = "FAIL"
    elif has_warnings or not git_status["user_configured"]:
        overall_status = "WARN"
    else:
        overall_status = "PASS"

    return {
        "project_name": project_path.name,
        "project_path": str(project_path),
        "overall_status": overall_status,
        "git": git_status,
        "runtimes": runtimes,
        "package_managers": package_managers,
        "issues": issues,
    }


def format_human_readable(data: Dict[str, Any]) -> str:
    """Format validation results for clean terminal output."""
    lines: List[str] = []
    lines.append("==================================================")
    lines.append(f" Environment Validation: {data['project_name']}")
    lines.append("==================================================")
    lines.append(f"Path:             {data['project_path']}")
    status_icon = "✓ PASS" if data["overall_status"] == "PASS" else ("⚠ WARN" if data["overall_status"] == "WARN" else "✗ FAIL")
    lines.append(f"Overall Status:   {status_icon}")
    lines.append("")

    # Runtimes
    lines.append("Runtimes:")
    for r_key, r_info in data["runtimes"].items():
        if r_info["installed"]:
            lines.append(f"  ✓ {r_info['name']:<16} {r_info['version']}")
        else:
            lines.append(f"  ✗ {r_info['name']:<16} Not Installed")

    lines.append("")
    # Git
    git = data["git"]
    lines.append("Version Control:")
    if git["installed"]:
        user_info = "configured" if git["user_configured"] else "unconfigured (user.name/email missing)"
        lines.append(f"  ✓ Git             {git['version']} [User: {user_info}]")
    else:
        lines.append("  ✗ Git             Not Installed in PATH")

    lines.append("")
    # Package Managers
    lines.append("Package Managers:")
    for pm_key, pm_info in data["package_managers"].items():
        if pm_info["installed"]:
            lines.append(f"  ✓ {pm_info['name']:<8} {pm_info['version']}")
        else:
            lines.append(f"  - {pm_info['name']:<8} Not Installed")

    lines.append("")
    # Issues
    lines.append("Project Diagnostics & Dependencies:")
    if not data["issues"]:
        lines.append("  ✓ No missing dependencies or runtime mismatches detected.")
    else:
        for issue in data["issues"]:
            icon = "✗ ERROR:" if issue["severity"] == "error" else "⚠ WARNING:"
            lines.append(f"  {icon} [{issue['category']}] {issue['message']}")

    lines.append("==================================================")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate required runtimes, package managers, and detect missing project dependencies."
    )
    parser.add_argument(
        "--path",
        "-p",
        default=".",
        help="Path to project directory (default: current working directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output validation results in JSON format.",
    )

    args = parser.parse_args()

    try:
        project_dir = Path(args.path)
        data = validate_environment(project_dir)

        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_human_readable(data))

        # Exit code: 0 on PASS / WARN, 1 on FAIL (hard error like missing runtime/node_modules)
        return 0 if data["overall_status"] != "FAIL" else 1

    except (FileNotFoundError, NotADirectoryError) as err:
        error_payload = {"error": str(err), "exit_code": 2}
        if args.json:
            print(json.dumps(error_payload, indent=2), file=sys.stderr)
        else:
            print(f"Error: {err}", file=sys.stderr)
        return 2
    except Exception as err:
        error_payload = {"error": f"Unexpected error: {err}", "exit_code": 2}
        if args.json:
            print(json.dumps(error_payload, indent=2), file=sys.stderr)
        else:
            print(f"Error: Unexpected error during environment validation: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
