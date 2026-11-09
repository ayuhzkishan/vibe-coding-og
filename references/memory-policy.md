# Memory & Context Policy

This document defines the clear boundaries, responsibilities, and storage lifecycles for memory systems used across `vibe-coding-og` development workflows.

---

## 1. Responsibility Matrix

| Memory Mechanism | Scope | Primary Purpose | Storage Location | Lifecycle | Version Controlled |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`CLAUDE.md`** | Repository | Standing codebase instructions, conventions, build commands | Project Root (`./CLAUDE.md`) | Persistent | Yes |
| **ADRs** | Architectural | Immutable historical records of major architectural choices | `references/adrs/` or `docs/adrs/` | Permanent | Yes |
| **`claude-mem`** | User / Cross-Session | Cross-project developer preferences, recurring patterns | Local User State (`~/.claude/`) | Ephemeral/Long-term | No |
| **Session Handoffs** | Shift / Inter-Agent | Immediate work-in-progress state between turns or developers | Active Session / PR comment | Ephemeral | Contextual |

---

## 2. Detailed Breakdown

### A. `CLAUDE.md` (Project Directives)
- **Role**: The foundational "living rulebook" and context briefing read by Claude Code at the start of every session.
- **What belongs here**:
  - Exact build, lint, and test commands (e.g., `./mvnw test`, `npm test`).
  - Code style rules, naming conventions, and preferred libraries.
  - Directory overview and repository-specific patterns.
  - Critical project "do's and don'ts".
- **What does NOT belong here**:
  - Temporary task notes, scratchpad checklists, or in-flight bug notes.
  - Individual developer personal preferences.
  - Complete copies of documentation found elsewhere in `references/`.
- **Maintenance**: Updated alongside feature PRs whenever repository conventions or build tools change.

---

### B. Architectural Decision Records (ADRs)
- **Role**: Formal, immutable documentation of significant architectural and design choices.
- **What belongs here**:
  - Context and problem statement.
  - Alternatives evaluated (with pros and cons).
  - Selected solution and technical justification.
  - Expected consequences, trade-offs, and migration paths.
- **Format**: Standard lightweight format (Title, Status, Context, Decision, Consequences).
- **Maintenance**: Once accepted and committed, an ADR is never retroactively modified to describe a new decision. New decisions require a new ADR that explicitly supersedes the prior record.

---

### C. `claude-mem` (Episodic Cross-Session Memory)
- **Role**: Personalized memory layer preserving user habits, developer quirks, and cross-project insights.
- **What belongs here**:
  - Developer interaction preferences (e.g., "User prefers concise answers with unified diffs").
  - Environment idiosyncrasies (e.g., local proxy setups, OS-specific path quirks).
  - Common pitfalls resolved across multiple projects.
- **What does NOT belong here**:
  - Proprietary project secrets, tokens, or private credentials.
  - Repository-specific architecture rules (which belong in `CLAUDE.md` or ADRs).
- **Maintenance**: Managed automatically or manually by the user; isolated to the local workstation.

---

### D. Session Handoffs (Ephemeral Context Transitions)
- **Role**: Immediate checkpoint capturing the exact state of work in flight when pausing work, switching agents, or handing off to another engineer.
- **What belongs here**:
  - **Completed**: Summary of tasks finished during the turn.
  - **In Flight**: Specific files being edited and current behavior.
  - **Verification Status**: Last test run output, passing/failing tests.
  - **Blockers / Open Questions**: Unresolved edge cases or required decisions.
  - **Immediate Next Step**: The exact single action to execute upon resumption.
- **Format**: Markdown handoff report (see [`output-templates.md`](output-templates.md)).
- **Lifecycle**: Temporary; discarded or archived once the work is committed and merged.
