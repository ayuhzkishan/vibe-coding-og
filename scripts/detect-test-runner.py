#!/usr/bin/env python3
"""
detect-test-runner.py - Test Runner Detection Utility for vibe-coding-og.

Analyzes a project directory to identify available test frameworks and recommend
appropriate test execution commands (without executing them).

Standard library only. Cross-platform (Windows & Linux).
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional


def read_text_safe(path: Path, max_bytes: int = 100_000) -> str:
    """Read a text file safely up to max_bytes."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def detect_node_test_runners(project_dir: Path) -> List[Dict[str, Any]]:
    """Detect Node.js test runners (Jest, Vitest, Mocha, npm test, etc.)."""
    runners: List[Dict[str, Any]] = []
    pkg_json_path = project_dir / "package.json"

    if not pkg_json_path.exists():
        return runners

    # Identify package manager
    pm = "npm"
    if (project_dir / "pnpm-lock.yaml").exists():
        pm = "pnpm"
    elif (project_dir / "yarn.lock").exists():
        pm = "yarn"
    elif (project_dir / "bun.lockb").exists() or (project_dir / "bun.lock").exists():
        pm = "bun"

    content = read_text_safe(pkg_json_path)
    try:
        data = json.loads(content) if content else {}
    except Exception:
        data = {}

    scripts = data.get("scripts", {})
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}

    test_script = scripts.get("test", "")
    is_placeholder = (
        not test_script
        or "no test specified" in test_script
        or test_script.strip() == "exit 1"
    )

    # 1. Vitest
    has_vitest = "vitest" in all_deps or any(
        project_dir.glob("vitest.config.*")
    )
    if has_vitest:
        files = ["package.json"]
        for f in ("vitest.config.ts", "vitest.config.js", "vitest.config.mjs"):
            if (project_dir / f).exists():
                files.append(f)
        cmd = f"{pm} test" if ("vitest" in test_script) else "npx vitest run"
        runners.append({
            "name": "Vitest",
            "framework": "Vitest",
            "command": cmd,
            "confidence": "high",
            "reason": "Found Vitest dependency/configuration in project",
            "files_matched": files,
        })

    # 2. Jest
    has_jest = "jest" in all_deps or any(
        project_dir.glob("jest.config.*")
    ) or "jest" in data
    if has_jest:
        files = ["package.json"]
        for f in ("jest.config.js", "jest.config.ts", "jest.config.json", "jest.config.mjs"):
            if (project_dir / f).exists():
                files.append(f)
        cmd = f"{pm} test" if ("jest" in test_script) else "npx jest"
        runners.append({
            "name": "Jest",
            "framework": "Jest",
            "command": cmd,
            "confidence": "high",
            "reason": "Found Jest dependency/configuration in project",
            "files_matched": files,
        })

    # 3. Mocha
    has_mocha = "mocha" in all_deps or (project_dir / ".mocharc.json").exists()
    if has_mocha:
        cmd = f"{pm} test" if ("mocha" in test_script) else "npx mocha"
        runners.append({
            "name": "Mocha",
            "framework": "Mocha",
            "command": cmd,
            "confidence": "high",
            "reason": "Found Mocha dependency/configuration in project",
            "files_matched": ["package.json"],
        })

    # 4. Generic npm/pnpm/yarn test script if not a placeholder and not yet covered
    if not is_placeholder and not any(r["command"] == f"{pm} test" for r in runners):
        runners.append({
            "name": f"{pm} test",
            "framework": "Custom NPM Script",
            "command": f"{pm} test",
            "confidence": "high",
            "reason": f"Found defined 'test' script in package.json: '{test_script}'",
            "files_matched": ["package.json"],
        })

    return runners


def detect_python_test_runners(project_dir: Path) -> List[Dict[str, Any]]:
    """Detect Python test runners (pytest, unittest, tox)."""
    runners: List[Dict[str, Any]] = []

    # Check for pytest markers
    pytest_files = []
    for f in ("pytest.ini", "setup.cfg", ".pytest.ini"):
        if (project_dir / f).exists():
            content = read_text_safe(project_dir / f)
            if "pytest" in content or f == "pytest.ini":
                pytest_files.append(f)

    pyproject_file = project_dir / "pyproject.toml"
    if pyproject_file.exists():
        pyproject_text = read_text_safe(pyproject_file)
        if "tool.pytest" in pyproject_text or "pytest" in pyproject_text:
            pytest_files.append("pyproject.toml")

    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        if re.search(r'\bpytest\b', read_text_safe(req_file)):
            pytest_files.append("requirements.txt")

    if (project_dir / "conftest.py").exists():
        pytest_files.append("conftest.py")

    # If pytest detected
    if pytest_files:
        runners.append({
            "name": "pytest",
            "framework": "pytest",
            "command": "pytest",
            "confidence": "high",
            "reason": f"Found pytest markers in: {', '.join(pytest_files)}",
            "files_matched": sorted(list(set(pytest_files))),
        })

    # Check for tox
    if (project_dir / "tox.ini").exists():
        runners.append({
            "name": "tox",
            "framework": "tox",
            "command": "tox",
            "confidence": "medium",
            "reason": "Found tox.ini configuration file",
            "files_matched": ["tox.ini"],
        })

    # Unittest fallback if test files exist
    test_dirs = [d for d in ("tests", "test") if (project_dir / d).is_dir()]
    has_test_files = False
    for td in test_dirs:
        if any((project_dir / td).glob("test_*.py")) or any((project_dir / td).glob("*_test.py")):
            has_test_files = True
            break

    if not pytest_files and (has_test_files or any(project_dir.glob("test_*.py"))):
        runners.append({
            "name": "unittest",
            "framework": "Python unittest",
            "command": "python -m unittest discover",
            "confidence": "medium",
            "reason": "Found test_*.py files without explicit pytest configuration",
            "files_matched": [d for d in ("tests", "test") if (project_dir / d).is_dir()],
        })

    return runners


def detect_java_test_runners(project_dir: Path) -> List[Dict[str, Any]]:
    """Detect Java test runners (Maven, Gradle, JUnit)."""
    runners: List[Dict[str, Any]] = []

    is_windows = sys.platform.startswith("win")

    # Maven
    pom_xml = project_dir / "pom.xml"
    if pom_xml.exists():
        has_wrapper = (project_dir / "mvnw").exists() or (project_dir / "mvnw.cmd").exists()
        if has_wrapper:
            cmd = "mvnw.cmd test" if is_windows else "./mvnw test"
        else:
            cmd = "mvn test"

        matched = ["pom.xml"]
        if (project_dir / "mvnw").exists():
            matched.append("mvnw")
        if (project_dir / "mvnw.cmd").exists():
            matched.append("mvnw.cmd")

        pom_content = read_text_safe(pom_xml)
        framework = "JUnit 5" if "junit-jupiter" in pom_content else "JUnit"
        if "testng" in pom_content.lower():
            framework = "TestNG"

        runners.append({
            "name": "Maven",
            "framework": framework,
            "command": cmd,
            "confidence": "high",
            "reason": "Found Maven pom.xml configuration",
            "files_matched": matched,
        })

    # Gradle
    build_gradle = project_dir / "build.gradle"
    build_gradle_kts = project_dir / "build.gradle_kts"
    if build_gradle.exists() or build_gradle_kts.exists():
        has_wrapper = (project_dir / "gradlew").exists() or (project_dir / "gradlew.cmd").exists()
        if has_wrapper:
            cmd = "gradlew.bat test" if is_windows else "./gradlew test"
        else:
            cmd = "gradle test"

        matched = [build_gradle.name if build_gradle.exists() else build_gradle_kts.name]
        if (project_dir / "gradlew").exists():
            matched.append("gradlew")
        if (project_dir / "gradlew.cmd").exists():
            matched.append("gradlew.cmd")

        runners.append({
            "name": "Gradle",
            "framework": "JUnit (Gradle Test Runner)",
            "command": cmd,
            "confidence": "high",
            "reason": "Found Gradle build file",
            "files_matched": matched,
        })

    return runners


def detect_test_runners(project_path: Path) -> Dict[str, Any]:
    """Identify all available test runners in the project."""
    project_path = project_path.resolve()

    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    all_runners: List[Dict[str, Any]] = []
    all_runners.extend(detect_java_test_runners(project_path))
    all_runners.extend(detect_python_test_runners(project_path))
    all_runners.extend(detect_node_test_runners(project_path))

    # Sort runners by confidence: high > medium > low
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    all_runners.sort(key=lambda r: confidence_order.get(r.get("confidence", "low"), 3))

    default_command = all_runners[0]["command"] if all_runners else None

    return {
        "project_name": project_path.name,
        "project_path": str(project_path),
        "total_runners_detected": len(all_runners),
        "default_command": default_command,
        "test_runners": all_runners,
    }


def format_human_readable(data: Dict[str, Any]) -> str:
    """Format test runner detection for human-readable terminal output."""
    lines: List[str] = []
    lines.append("==================================================")
    lines.append(f" Test Runner Detection: {data['project_name']}")
    lines.append("==================================================")
    lines.append(f"Path:             {data['project_path']}")
    lines.append(f"Runners Found:    {data['total_runners_detected']}")
    lines.append(f"Primary Command:  {data['default_command'] or 'None detected'}")
    lines.append("")

    if not data["test_runners"]:
        lines.append("No automated test runners detected.")
        lines.append("Check that your project includes standard test files, manifests, or scripts.")
    else:
        lines.append("Detected Test Runners:")
        for idx, runner in enumerate(data["test_runners"], start=1):
            lines.append(f"  {idx}. {runner['name']} ({runner['framework']})")
            lines.append(f"     Command:    {runner['command']}")
            lines.append(f"     Confidence: {runner['confidence'].upper()}")
            lines.append(f"     Reason:     {runner['reason']}")
            if runner.get("files_matched"):
                lines.append(f"     Files:      {', '.join(runner['files_matched'])}")
            lines.append("")

    lines.append("--------------------------------------------------")
    lines.append("Note: Test commands were detected but NOT executed.")
    lines.append("==================================================")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Identify available test frameworks and recommended test commands without running tests."
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
        help="Output detected test runners in JSON format.",
    )

    args = parser.parse_args()

    try:
        project_dir = Path(args.path)
        data = detect_test_runners(project_dir)

        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_human_readable(data))

        # Exit code: 0 if test runners found, 1 if no runners detected
        return 0 if data["total_runners_detected"] > 0 else 1

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
            print(f"Error: Unexpected error during test runner detection: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
