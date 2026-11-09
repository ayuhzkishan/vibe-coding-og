# Testing Infrastructure

This directory provides the automated test suites, test runners, and validation procedures for `vibe-coding-og`.

---

## 1. Directory Structure

```
tests/
├── README.md                      # Testing guide & manifest validation docs
├── run_tests.py                   # Master test runner (discovers all suites)
├── skill-tests/                   # Test suites for individual Claude Code skills
├── hook-tests/                    # Test suites for lifecycle event hooks
└── integration-tests/             # End-to-end integration & manifest tests
    ├── test_detection_scripts.py  # Tests for scripts/ detection utilities
    ├── test_plugin_manifests.py   # Schema & structure tests for manifests
    └── test_plugin_install.py     # Local plugin installation & resolution tests
```

---

## 2. Running Automated Tests

All tests rely strictly on Python's standard library (`unittest`) with zero external dependencies.

### Run All Tests
From the root of `vibe-coding-og`:

```bash
python tests/run_tests.py
```

### Run Specific Test Suites
```bash
# Test project detection, test runner detection, and environment validation scripts
python tests/integration-tests/test_detection_scripts.py

# Test plugin and marketplace manifest validity
python tests/integration-tests/test_plugin_manifests.py

# Test local plugin installation prerequisites and structure
python tests/integration-tests/test_plugin_install.py
```

---

## 3. Validating Plugin Manifests

Claude Code plugins use two critical manifest files in `.claude-plugin/`:
- **`plugin.json`**: Plugin identity, version, author, and documentation.
- **`marketplace.json`**: Marketplace catalog indexing installable plugins.

### Automated Python Validation
Run the manifest test suite:
```bash
python tests/integration-tests/test_plugin_manifests.py
```
This test asserts:
- Valid JSON syntax and structure.
- Required fields (`name`, `version`, `description`, `author`/`owner`).
- Kebab-case naming rules (`vibe-coding-og`).
- Correct local directory source reference (`"source": "./"`).

### Official Claude Code CLI Validation
If the Claude Code CLI (`claude`) is installed in your environment, validate the plugin manifest directly:

```bash
# Validate plugin in the current directory
claude plugin validate .

# Or validate with explicit path
claude plugin validate ./vibe-coding-og
```

---

## 4. Local Integration Testing & Installation

To verify that Claude Code can discover, install, and execute the plugin locally before publishing to a remote GitHub repository:

### Method A: Direct Local Plugin Install
Installs the plugin directly from your local filesystem clone into Claude Code:

```bash
claude plugin install .
```
*(Or from inside an active Claude Code session: `/plugin install .`)*

### Method B: Local Marketplace Catalog Simulation
Tests adding the repository as a local marketplace and installing from that marketplace:

1. Register the local repository as a marketplace:
   ```bash
   claude plugin marketplace add ./
   ```
2. Install the plugin using the marketplace identifier:
   ```bash
   claude plugin install vibe-coding-og@vibe-coding-og
   ```
3. Verify installed plugins:
   ```bash
   claude plugin list
   ```

---

## 5. Guidelines for Testing Skills & Hooks

As you author new skills in `skills/<skill-name>/` and event hooks in `hooks/`:

### Skill Tests (`tests/skill-tests/`)
- Place test files named `test_<skill_name>.py` inside `tests/skill-tests/`.
- Test skill scripts and invocation prompts against the mock fixtures in `examples/`.
- Verify that skill instructions correctly call the utilities in `scripts/` with expected argument flags.

### Hook Tests (`tests/hook-tests/`)
- Place test files named `test_<hook_name>.py` inside `tests/hook-tests/`.
- Verify that hook scripts execute within designated timeout limits.
- Assert that exit codes (0 for success, non-zero for block) behave correctly for pre-commit or event gates.
