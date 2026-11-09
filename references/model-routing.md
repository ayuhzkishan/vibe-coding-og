# Model Routing Guidelines

This document outlines the model selection strategy and routing principles for the `vibe-coding-og` plugin architecture.

---

## 1. Core Model Tiers & Preferences

To balance reasoning capability, latency, and token efficiency, tasks are routed across three primary tiers:

```
┌─────────────────────────────────────────────────────────────┐
│                         OPUS TIER                           │
│     System Architecture • Complex Planning • Deep Debug     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Escalates to / Fallback from
┌──────────────────────────────▼──────────────────────────────┐
│                        SONNET TIER                          │
│     Implementation • Code Review • Security • Documentation │
└──────────────────────────────┬──────────────────────────────┘
                               │ Escalates to / Fallback from
┌──────────────────────────────▼──────────────────────────────┐
│                         HAIKU TIER                          │
│       Routine Tests • Linting • Status Checks • Parsing     │
└─────────────────────────────────────────────────────────────┘
```

### Opus Tier
- **Target Workloads**:
  - System and macro-architecture design.
  - Multi-component project planning and dependency resolution.
  - Root-cause analysis of non-deterministic, distributed, or deep concurrency bugs.
  - High-consequence architectural trade-off evaluations.
- **Characteristics**: Highest context comprehension, superior complex reasoning, deeper strategic planning.

### Sonnet Tier (Default Workhorse)
- **Target Workloads**:
  - Core feature implementation and bug fixing.
  - Detailed pull request and code review.
  - Security audit checklist verification.
  - Test suite authoring and refactoring.
  - Technical documentation and API specifications.
- **Characteristics**: Optimal balance of code quality, speed, and cost-effectiveness. Primary tier for everyday engineering tasks.

### Haiku Tier
- **Target Workloads**:
  - Routine test execution and pass/fail monitoring.
  - Fast linting, formatting, and syntax validation.
  - Log summarization and raw metric parsing.
  - Repetitive data extraction and status ping verification.
- **Characteristics**: Near-instantaneous response times, minimal token footprint, ideal for high-frequency loops.

---

## 2. Dynamic Model Abstraction

> [!IMPORTANT]
> Model identifiers change over time. Never hardcode fixed timestamped model IDs (e.g. `claude-3-opus-20240229`) in logic, prompts, or scripts.

- Use **tier aliases** (`opus`, `sonnet`, `haiku`) or environment configuration variables.
- Map aliases to the latest stable model identifiers provided by Claude Code or runtime configuration.
- Allow user overrides via configuration files or environment parameters without altering workflow code.

---

## 3. Escalation Principles

When a task exceeds the complexity threshold of a lower tier, it must be escalated systematically:

1. **Haiku ➔ Sonnet**:
   - *Trigger*: A routine test runner fails with ambiguous stack traces, unhandled exceptions, or structural compile errors.
   - *Action*: Hand off the failure context, relevant logs, and stack trace to Sonnet for diagnostic investigation and code fix implementation.

2. **Sonnet ➔ Opus**:
   - *Trigger*: Sonnet attempts two consecutive unsuccessful fixes, encounters circular architectural dependencies, or requires restructuring core system contracts.
   - *Action*: Pause implementation; prompt Opus to perform architectural re-evaluation and formulate an updated execution plan.

---

## 4. Fallback & Graceful Degradation

When higher-tier models face rate limits, network latency spikes, or temporary service interruptions:

1. **Opus Fallback to Sonnet**:
   - Decompose high-level architectural planning into modular, sequential sub-problems.
   - Supply Sonnet with explicit boundary constraints, interface definitions, and architectural decisions to guide its output.

2. **Sonnet Fallback to Haiku**:
   - Restrict Haiku to mechanical code generation, stub generation, or syntax fixing.
   - Require human-in-the-loop review or automated verification before merging Haiku-generated implementations.

3. **Rate-Limit Backoff**:
   - Implement exponential backoff with jitter on 429 / 529 responses.
   - Queue non-critical tasks (e.g., docs generation, test running) until tier availability restores.
