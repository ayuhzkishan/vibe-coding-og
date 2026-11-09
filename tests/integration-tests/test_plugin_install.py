#!/usr/bin/env python3
"""
test_plugin_install.py - Integration test for local Claude Code plugin resolution & install readiness.

Simulates and verifies that the repository layout satisfies all prerequisites
for local installation via `claude plugin install .` or `/plugin marketplace add`.
"""

import json
from pathlib import Path
import shutil
import subprocess
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestPluginInstallReadiness(unittest.TestCase):
    def test_required_plugin_layout(self):
        """Verify that standard plugin top-level directories exist and are structured correctly."""
        required_dirs = [
            REPO_ROOT / ".claude-plugin",
            REPO_ROOT / "skills",
            REPO_ROOT / "agents",
            REPO_ROOT / "hooks",
            REPO_ROOT / "references",
            REPO_ROOT / "scripts",
        ]
        for d in required_dirs:
            self.assertTrue(d.is_dir(), f"Required plugin directory {d.name} must exist")

    def test_marketplace_to_plugin_linkage(self):
        """Simulate Claude Code resolving marketplace catalog to local plugin root."""
        marketplace_file = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        with open(marketplace_file, "r", encoding="utf-8") as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        rel_source = plugin_entry["source"]
        target_dir = (REPO_ROOT / rel_source).resolve()

        # The target dir must contain .claude-plugin/plugin.json
        target_manifest = target_dir / ".claude-plugin" / "plugin.json"
        self.assertTrue(target_manifest.is_file(), f"Resolved target manifest must exist at {target_manifest}")

        with open(target_manifest, "r", encoding="utf-8") as f:
            plugin_data = json.load(f)

        self.assertEqual(
            plugin_entry["name"],
            plugin_data["name"],
            "Marketplace entry name must match plugin.json name",
        )
        self.assertEqual(
            plugin_entry["version"],
            plugin_data["version"],
            "Marketplace entry version must match plugin.json version",
        )

    def test_claude_cli_validation_if_available(self):
        """If `claude` CLI is installed on host, execute `claude plugin validate .`."""
        claude_bin = shutil.which("claude")
        if not claude_bin:
            self.skipTest("Claude Code CLI ('claude') not detected in PATH; skipping CLI command test")

        res = subprocess.run(
            [claude_bin, "plugin", "validate", "."],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"'claude plugin validate .' failed:\n{res.stdout}\n{res.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
