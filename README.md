# vibe-coding-og

A modular engineering workflow toolkit for Claude Code.

## Overview

`vibe-coding-og` provides a senior-engineer-style development workflow for Claude Code with modular skills, agents, hooks, and automated workflows.

## Installation

### 1. Add the Marketplace

From inside a Claude Code session:

```bash
/plugin marketplace add YOUR_GITHUB_USERNAME/vibe-coding-og
```

*(Or via the CLI outside a session: `claude plugin marketplace add YOUR_GITHUB_USERNAME/vibe-coding-og`)*

### 2. Install the Plugin

From inside a Claude Code session:

```bash
/plugin install vibe-coding-og@vibe-coding-og
```

*(Or via the CLI outside a session: `claude plugin install vibe-coding-og@vibe-coding-og`)*

### Local Development Install

To test the plugin directly from a local clone:

```bash
claude plugin install ./vibe-coding-og
```

## Repository Structure

```
vibe-coding-og/
├── .claude-plugin/        # Claude Code plugin manifest and marketplace catalog
├── skills/                # Domain-specific engineering skills
├── agents/                # Autonomous agent definitions and configurations
├── hooks/                 # Lifecycle and workflow event hooks
├── references/            # Architecture decision records, reference guides, and docs
├── scripts/               # Utility, automation, and tooling scripts
├── tests/                 # Skill, hook, and integration test suites
├── examples/              # Reference implementation examples (Spring Boot, Python, Node)
├── .gitignore             # Ignore rules for environments, IDEs, runtimes, and local state
├── LICENSE                # MIT License
└── README.md              # Project overview and installation guide
```

## Configuration

Before publishing, update the placeholders in the following files:
- `.claude-plugin/plugin.json`: Author information and repository URLs (`YOUR_NAME`, `YOUR_EMAIL`, `YOUR_GITHUB_USERNAME`).
- `.claude-plugin/marketplace.json`: Marketplace owner information and source references.
- `LICENSE`: Author copyright notice (`[YOUR_NAME]`).

## License

This project is licensed under the [MIT License](LICENSE).
