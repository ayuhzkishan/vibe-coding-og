# vibe-coding-og

A modular engineering workflow toolkit for Claude Code, designed to bring senior-engineer rigor, defensive automation, and structured practices to AI-assisted software development.

---

## 1. Project Philosophy

"Vibe coding" is often mistaken for unstructured, unverified code generation. **vibe-coding-og** reframes vibe coding as **high-leverage senior engineering**:
- **Move fast with guardrails**: Rapid iteration paired with automated sanity checks, pre-commit gates, and defensive validation.
- **Defensive by default**: Diagnostics before execution, zero secret leakage, safe test runner discovery without unprompted code execution.
- **Model-appropriate delegation**: Directing architectural challenges to high-reasoning tiers (Opus), implementation and code reviews to balanced tiers (Sonnet), and routine execution to fast tiers (Haiku).
- **Separation of concerns**: Clear boundaries between persistent project rules (`CLAUDE.md`), immutable records (`ADRs`), episodic memory (`claude-mem`), and ephemeral transitions (`session handoffs`).

---

## 2. Status & Capabilities

### Implemented Functionality (Ready & Verified)

- **Claude Code Marketplace & Plugin Core**:
  - Validated plugin manifest ([`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)) adhering to Anthropic specification.
  - Validated marketplace catalog ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)) enabling single-repo distribution (`"source": "./"`).
  - Genuine local install verification verified against Claude Code CLI v2.1.220 (`claude plugin validate`, `marketplace add`, and `install`).
- **Foundational Detection & Diagnostic Utilities** (Standard Library only, cross-platform):
  - [`scripts/detect-project.py`](scripts/detect-project.py): Detects languages (Java, Python, JS/TS), frameworks (Spring Boot, FastAPI, Flask, Django, React, Next.js), package managers (Maven, Gradle, pip, Poetry, uv, npm, pnpm, yarn), manifests, and Git state.
  - [`scripts/detect-test-runner.py`](scripts/detect-test-runner.py): Safely identifies test runners (pytest, unittest, Maven surefire, Gradle, Jest, Vitest) and recommends execution commands without executing tests.
  - [`scripts/validate-environment.py`](scripts/validate-environment.py): Validates runtimes (Python, Node, Java), package managers, Git configuration, and detects missing dependencies (`node_modules/`, virtual environments) with zero secret exposure.
- **Engineering References & Policies**:
  - [`references/model-routing.md`](references/model-routing.md): Tier delegation, escalation rules, and fallback strategies.
  - [`references/security-checklist.md`](references/security-checklist.md): Secrets management, OWASP Top 10, AuthN/AuthZ, dependency pinning, and CI/CD hardening.
  - [`references/commit-conventions.md`](references/commit-conventions.md): Conventional Commits 1.0.0 guidelines with plugin-specific scopes.
  - [`references/memory-policy.md`](references/memory-policy.md): Matrix governing `CLAUDE.md`, ADRs, `claude-mem`, and session handoffs.
  - [`references/output-templates.md`](references/output-templates.md): Standardized formats for diagnostics, testing, code review, security audits, and pre-commit checks.
- **Automated Testing Harness**:
  - Master test runner ([`tests/run_tests.py`](tests/run_tests.py)) executing all integration and manifest tests with 100% pass rate.
  - Automated manifest validation test ([`tests/integration-tests/test_plugin_manifests.py`](tests/integration-tests/test_plugin_manifests.py)).
  - Local installation resolution test ([`tests/integration-tests/test_plugin_install.py`](tests/integration-tests/test_plugin_install.py)).
  - Script diagnostic & security test suite ([`tests/integration-tests/test_detection_scripts.py`](tests/integration-tests/test_detection_scripts.py)).

### Planned Capabilities (Roadmap)

- **12 Custom Claude Code Skills** (`skills/`):
  - `doctor`: Automated environment and project health checks.
  - `check`: Fast syntax, linting, and type verification.
  - `test`: Automated test runner discovery and selective execution.
  - `ship`: Pre-release verification, changelog generation, and tag creation.
  - `deep-plan`: Opus-driven architectural design and decomposition.
  - `maintain`: Dependency audit, updates, and deprecation cleanups.
  - `security`: OWASP Top 10 and secret exposure audit against `security-checklist.md`.
  - `review`: Sonnet-tier structured code reviews with remediation diffs.
  - `verify`: Pre-commit multi-layer gate enforcement.
  - `docs`: API specification and markdown documentation synchronizer.
  - `memory-sync`: `CLAUDE.md` and ADR update validator.
  - `handoff`: Structured session context generator for turn/agent transitions.
- **Subagents** (`agents/`): Specialized agent roles with tailored system prompts.
- **Event Hooks** (`hooks/`): Lifecycle hooks for pre-commit checks and event gates.
- **Multi-Runtime Examples** (`examples/`): Real-world Spring Boot, Python, and Node.js reference projects.

---

## 3. Architecture Overview

```
                      Claude Code CLI / Session
                                 │
           ┌─────────────────────┴─────────────────────┐
           │                                           │
  /plugin marketplace add                     /plugin install
           │                                           │
           ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│ .claude-plugin/           │               │ .claude-plugin/           │
│ marketplace.json          │───────────────│ plugin.json               │
│ (Catalog & Registry)      │  references   │ (Plugin Identity & Spec)  │
└───────────────────────────┘    "./"       └─────────────┬─────────────┘
                                                          │
          ┌───────────────────────────────────────────────┴───────────────────────────────────────────────┐
          │                                               │                                               │
          ▼                                               ▼                                               ▼
┌───────────────────┐                           ┌───────────────────┐                           ┌───────────────────┐
│ skills/           │                           │ scripts/          │                           │ references/       │
│ • doctor, check   │──── invokes utilities ───▶│ • detect-project  │◀─── guided by policies ───│ • model-routing   │
│ • test, ship      │     (standard library)    │ • detect-test     │     and standards         │ • security        │
│ • review, verify  │                           │ • validate-env    │                           │ • commit / memory │
└───────────────────┘                           └───────────────────┘                           └───────────────────┘
```

---

## 4. Directory Structure

```
vibe-coding-og/
├── .claude-plugin/
│   ├── marketplace.json            # Claude Code marketplace catalog manifest
│   └── plugin.json                 # Claude Code plugin manifest
├── agents/                         # Custom Claude Code subagents
├── examples/                       # Reference fixtures
│   ├── node/
│   ├── python/
│   └── spring-boot/
├── hooks/                          # Event-driven lifecycle hooks
├── references/                     # Architecture, security & memory standards
│   ├── commit-conventions.md       # Conventional commit guidelines
│   ├── memory-policy.md            # CLAUDE.md vs ADRs vs claude-mem policy
│   ├── model-routing.md            # Opus vs Sonnet vs Haiku task allocation
│   ├── output-templates.md         # Reusable diagnostic, review & test reports
│   └── security-checklist.md       # OWASP, secrets & infrastructure checklist
├── scripts/                        # Python detection & validation utilities
│   ├── detect-project.py           # Stack & structure detection
│   ├── detect-test-runner.py       # Safe test runner & command discovery
│   └── validate-environment.py     # Environment & dependency validation
├── skills/                         # Modular engineering skills
│   ├── check/
│   ├── deep-plan/
│   ├── docs/
│   ├── doctor/
│   ├── handoff/
│   ├── maintain/
│   ├── memory-sync/
│   ├── review/
│   ├── security/
│   ├── ship/
│   ├── test/
│   └── verify/
├── tests/                          # Test harness & suites
│   ├── hook-tests/                 # Hook test suites
│   ├── integration-tests/          # Manifest, install & script integration tests
│   │   ├── test_detection_scripts.py
│   │   ├── test_plugin_install.py
│   │   └── test_plugin_manifests.py
│   ├── skill-tests/                # Skill test suites
│   ├── README.md                   # Testing instructions
│   └── run_tests.py                # Master test runner
├── .gitattributes                  # LF/CRLF line-ending normalization
├── .gitignore                      # Comprehensive runtime & secret ignore rules
├── LICENSE                         # MIT License
└── README.md                       # Repository documentation
```

---

## 5. Prerequisites

- **Python**: `3.8+` (Core scripts use the Python Standard Library exclusively; no `pip install` required).
- **Git**: `2.20+`.
- **Claude Code CLI**: `2.1.0+` (Tested on Claude Code CLI v2.1.220).
- *Optional Runtimes* (depending on projects being analyzed):
  - Node.js `18+` (with npm, pnpm, or yarn).
  - Java JDK `17+` (with Maven or Gradle).

---

## 6. Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ayuhzkishan/vibe-coding-og.git
   cd vibe-coding-og
   ```

2. **Run the Test Suite**:
   ```bash
   python tests/run_tests.py
   ```

---

## 7. Plugin Validation Instructions

Before committing changes or publishing releases, validate plugin and marketplace manifests:

### Automated Python Validation
```bash
python tests/integration-tests/test_plugin_manifests.py
```

### Official Claude Code CLI Validation
```bash
claude plugin validate .
```
*Expected output:*
```text
Validating marketplace manifest: .../.claude-plugin/marketplace.json
√ Validation passed
```

---

## 8. Installation Instructions

### Method 1: From Remote Marketplace (Recommended for Users)

Once published to GitHub:

1. **Add the Marketplace**:
   - In Claude Code interactive session:
     ```text
     /plugin marketplace add ayuhzkishan/vibe-coding-og
     ```
   - Or from terminal:
     ```bash
     claude plugin marketplace add ayuhzkishan/vibe-coding-og
     ```

2. **Install the Plugin**:
   - In Claude Code interactive session:
     ```text
     /plugin install vibe-coding-og@vibe-coding-og
     ```
   - Or from terminal:
     ```bash
     claude plugin install vibe-coding-og@vibe-coding-og
     ```

### Method 2: Local Filesystem Installation (Verified)

To install directly from your local clone for development:

```bash
# Register local directory as marketplace
claude plugin marketplace add /path/to/vibe-coding-og

# Install into local or user scope
claude plugin install vibe-coding-og@vibe-coding-og --scope local

# Verify installation
claude plugin list
claude plugin details vibe-coding-og@vibe-coding-og
```

*To uninstall local testing build:*
```bash
claude plugin uninstall vibe-coding-og@vibe-coding-og --scope local
claude plugin marketplace remove vibe-coding-og
```

---

## 9. How to Add a New Skill Manually

To implement a new skill in `skills/<skill-name>/`:

1. **Create the Skill File**:
   Inside the target skill folder (e.g., `skills/doctor/`), create a `SKILL.md` file:
   ```markdown
   ---
   name: doctor
   description: Inspect project health, runtimes, package managers, and dependencies.
   ---

   # Doctor Skill

   When the user asks to check project health or diagnose environment problems:
   1. Run python ../../scripts/validate-environment.py --path .
   2. Summarize any detected runtime or dependency issues.
   ```
2. **Invoke Reusable Utilities**:
   Skill instructions can reference scripts in `scripts/`:
   - `python scripts/detect-project.py --json`
   - `python scripts/detect-test-runner.py --json`
   - `python scripts/validate-environment.py --json`
3. **Add Automated Skill Tests**:
   Create a test file in `tests/skill-tests/test_doctor.py`.
4. **Validate**:
   Run `claude plugin validate .` to confirm Claude Code discovers the new skill.

---

## 10. How to Add Agents and Hooks Manually

### Adding an Agent (`agents/`)
1. Create a markdown agent definition in `agents/<agent-name>.md`:
   ```markdown
   ---
   name: code-reviewer
   description: Autonomous code review agent focused on correctness and security.
   model: sonnet
   ---

   You are an expert senior code reviewer. You evaluate code changes against
   the security checklist in references/security-checklist.md and produce reports
   matching references/output-templates.md.
   ```
2. Claude Code automatically discovers markdown files in `agents/`.

### Adding a Hook (`hooks/`)
1. Create hook scripts or configurations in `hooks/` (e.g. `pre-commit.sh`, `pre-commit.py`, or event triggers).
2. Ensure hook scripts:
   - Handle missing runtimes gracefully.
   - Return exit code `0` on success and non-zero on gate failure.
   - Never print secrets or environment variable values.
3. Add a verification test in `tests/hook-tests/test_<hook_name>.py`.

---

## 11. Contribution Guidelines

1. **Conventional Commits**: All commit messages must follow [`references/commit-conventions.md`](references/commit-conventions.md).
2. **Zero Dependencies for Core Tools**: New utility scripts in `scripts/` must use the Python standard library exclusively.
3. **Security Compliance**: Ensure all code changes comply with [`references/security-checklist.md`](references/security-checklist.md). Never commit secrets, tokens, or personal configurations.
4. **Verification**: Run `python tests/run_tests.py` and `claude plugin validate .` prior to opening pull requests.

---

## 12. License

This project is licensed under the [MIT License](LICENSE).
