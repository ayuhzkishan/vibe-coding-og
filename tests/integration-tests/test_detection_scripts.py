#!/usr/bin/env python3
"""
test_detection_scripts.py - Automated tests for vibe-coding-og detection scripts.

Tests detect-project.py, detect-test-runner.py, and validate-environment.py
using temporary mock projects.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
PYTHON_EXE = sys.executable


class TestDetectProject(unittest.TestCase):
    def test_detect_spring_boot_maven(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pom = tmp_path / "pom.xml"
            pom.write_text(
                """<project>
                    <modelVersion>4.0.0</modelVersion>
                    <groupId>com.example</groupId>
                    <artifactId>demo</artifactId>
                    <version>0.0.1-SNAPSHOT</version>
                    <parent>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-parent</artifactId>
                    </parent>
                </project>""",
                encoding="utf-8",
            )
            (tmp_path / "src" / "main" / "java").mkdir(parents=True)
            (tmp_path / "mvnw").write_text("#!/bin/sh\n", encoding="utf-8")

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-project.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertIn("Java", data["languages"])
            self.assertIn("Spring Boot", data["frameworks"])
            self.assertIn("Maven", data["build_systems"])
            self.assertIn("pom.xml", data["manifests"])
            self.assertIn("src/main/java", data["main_directories"])

    def test_detect_python_fastapi(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "requirements.txt").write_text("fastapi==0.110.0\npytest>=8.0.0\nuvicorn\n", encoding="utf-8")
            (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
            (tmp_path / "tests").mkdir()

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-project.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertIn("Python", data["languages"])
            self.assertIn("FastAPI", data["frameworks"])
            self.assertIn("pytest", data["frameworks"])
            self.assertIn("pip", data["package_managers"])
            self.assertIn("requirements.txt", data["manifests"])

    def test_detect_node_nextjs_ts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pkg = {
                "name": "my-app",
                "dependencies": {"next": "14.0.0", "react": "18.2.0"},
                "devDependencies": {"typescript": "5.0.0"},
            }
            (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
            (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")
            (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-project.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertIn("TypeScript", data["languages"])
            self.assertIn("Next.js", data["frameworks"])
            self.assertIn("React", data["frameworks"])
            self.assertIn("pnpm", data["package_managers"])


class TestDetectTestRunner(unittest.TestCase):
    def test_detect_pytest(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
            (tmp_path / "tests").mkdir()

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-test-runner.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertEqual(data["default_command"], "pytest")
            runners = [r["name"] for r in data["test_runners"]]
            self.assertIn("pytest", runners)

    def test_detect_jest_and_npm_test(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pkg = {
                "name": "node-tests",
                "scripts": {"test": "jest"},
                "devDependencies": {"jest": "^29.0.0"},
            }
            (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-test-runner.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertIn("test", data["default_command"])
            runners = [r["name"] for r in data["test_runners"]]
            self.assertIn("Jest", runners)

    def test_detect_maven_test(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
            (tmp_path / "mvnw").write_text("", encoding="utf-8")

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "detect-test-runner.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertTrue("mvn" in data["default_command"])


class TestValidateEnvironment(unittest.TestCase):
    def test_validate_missing_node_modules(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "package.json").write_text('{"name": "missing-modules"}', encoding="utf-8")

            res = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "validate-environment.py"), "-p", str(tmp_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            # Should exit with code 1 due to missing node_modules
            self.assertEqual(res.returncode, 1)
            data = json.loads(res.stdout)
            self.assertEqual(data["overall_status"], "FAIL")
            categories = [i["category"] for i in data["issues"]]
            self.assertIn("dependencies", categories)

    def test_security_no_env_secrets_leaked(self):
        """Verify that environment variable values are never output in plain text or JSON."""
        # Set a dummy secret in the environment
        secret_key = "TOP_SECRET_AUTH_TOKEN_TEST"
        secret_val = "SECRET_VALUE_DO_NOT_LEAK_XYZ"
        os.environ[secret_key] = secret_val

        try:
            res_json = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "validate-environment.py"), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotIn(secret_val, res_json.stdout)
            self.assertNotIn(secret_key, res_json.stdout)

            res_text = subprocess.run(
                [PYTHON_EXE, str(SCRIPTS_DIR / "validate-environment.py")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotIn(secret_val, res_text.stdout)
            self.assertNotIn(secret_key, res_text.stdout)
        finally:
            os.environ.pop(secret_key, None)


if __name__ == "__main__":
    unittest.main()
