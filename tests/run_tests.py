#!/usr/bin/env python3
"""
run_tests.py - Master Test Runner for vibe-coding-og.

Discovers and executes test suites across:
- tests/integration-tests/
- tests/hook-tests/
- tests/skill-tests/

Uses standard library unittest. Cross-platform (Windows & Linux).
"""

import os
from pathlib import Path
import sys
import unittest

TESTS_DIR = Path(__file__).resolve().parent


def collect_test_files():
    """Find all test_*.py files in tests subdirectories."""
    subdirs = ["integration-tests", "hook-tests", "skill-tests"]
    test_files = []
    for sub in subdirs:
        subpath = TESTS_DIR / sub
        if subpath.is_dir():
            for f in sorted(subpath.glob("test_*.py")):
                test_files.append(f)
    return test_files


def run_all_tests() -> int:
    test_files = collect_test_files()
    if not test_files:
        print("No test files found in tests/ directories.")
        return 0

    print("==================================================")
    print(f" vibe-coding-og Test Suite ({len(test_files)} test modules)")
    print("==================================================")
    for tf in test_files:
        print(f"  • {tf.relative_to(TESTS_DIR)}")
    print("--------------------------------------------------")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for tf in test_files:
        # Load tests from file path
        try:
            mod_suite = loader.discover(
                start_dir=str(tf.parent),
                pattern=tf.name,
                top_level_dir=str(tf.parent),
            )
            suite.addTests(mod_suite)
        except Exception as e:
            print(f"Error loading {tf}: {e}", file=sys.stderr)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("==================================================")
    print(f"Tests Run: {result.testsRun} | Passed: {result.testsRun - len(result.failures) - len(result.errors)} | Failures: {len(result.failures)} | Errors: {len(result.errors)}")
    print("==================================================")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
