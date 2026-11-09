#!/usr/bin/env python3
"""
test_plugin_manifests.py - Validation test suite for Claude Code plugin manifests.

Validates .claude-plugin/plugin.json and .claude-plugin/marketplace.json against
official Claude Code specifications and structural requirements.
"""

import json
from pathlib import Path
import re
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestPluginManifest(unittest.TestCase):
    def setUp(self):
        self.manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"

    def test_plugin_json_exists(self):
        self.assertTrue(self.manifest_path.is_file(), "plugin.json must exist in .claude-plugin/")

    def test_plugin_json_syntax_and_required_fields(self):
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Name
        self.assertIn("name", data)
        self.assertEqual(data["name"], "vibe-coding-og")
        self.assertTrue(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", data["name"]), "Name must be kebab-case")

        # Version
        self.assertIn("version", data)
        self.assertEqual(data["version"], "0.1.0")
        self.assertTrue(re.match(r"^\d+\.\d+\.\d+$", data["version"]), "Version must follow SemVer")

        # Description
        self.assertIn("description", data)
        self.assertTrue(len(data["description"].strip()) > 0)

        # Author
        self.assertIn("author", data)
        self.assertIsInstance(data["author"], dict)
        self.assertIn("name", data["author"])
        self.assertIn("email", data["author"])

        # License
        self.assertIn("license", data)
        self.assertEqual(data["license"], "MIT")

        # Keywords
        self.assertIn("keywords", data)
        self.assertIsInstance(data["keywords"], list)
        self.assertIn("claude-code", data["keywords"])


class TestMarketplaceManifest(unittest.TestCase):
    def setUp(self):
        self.marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    def test_marketplace_json_exists(self):
        self.assertTrue(self.marketplace_path.is_file(), "marketplace.json must exist in .claude-plugin/")

    def test_marketplace_json_syntax_and_structure(self):
        with open(self.marketplace_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Name
        self.assertIn("name", data)
        self.assertEqual(data["name"], "vibe-coding-og")

        # Owner
        self.assertIn("owner", data)
        self.assertIsInstance(data["owner"], dict)
        self.assertIn("name", data["owner"])

        # Plugins
        self.assertIn("plugins", data)
        self.assertIsInstance(data["plugins"], list)
        self.assertGreaterEqual(len(data["plugins"]), 1)

        plugin_entry = next((p for p in data["plugins"] if p.get("name") == "vibe-coding-og"), None)
        self.assertIsNotNone(plugin_entry, "Marketplace must contain an entry for 'vibe-coding-og'")

        # Source resolution
        self.assertIn("source", plugin_entry)
        source_val = plugin_entry["source"]
        self.assertEqual(source_val, "./", "Plugin source must point to './' for local root plugin")

        # Verify target directory has plugin.json
        resolved_plugin_path = (REPO_ROOT / source_val / ".claude-plugin" / "plugin.json").resolve()
        self.assertTrue(resolved_plugin_path.is_file(), f"Target plugin file must exist at {resolved_plugin_path}")


if __name__ == "__main__":
    unittest.main()
