# Commit Conventions

`vibe-coding-og` follows the **Conventional Commits 1.0.0** standard to ensure readable history, clean changelog generation, and automated semantic versioning.

---

## 1. Commit Message Structure

Each commit message consists of a **header**, an optional **body**, and an optional **footer**:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Constraints:
- **Header length**: Limit header line to 72 characters or fewer.
- **Letter casing**: Use lowercase for type, scope, and description.
- **Mood**: Use imperative, present tense ("add", "fix", "refactor", not "added", "fixes", "refactored").
- **Punctuation**: Do not end the description with a period.

---

## 2. Commit Types

| Type | Purpose | SemVer Impact |
| :--- | :--- | :--- |
| `feat` | Introduces a new feature or capability | Minor (`0.X.0`) |
| `fix` | Patches a bug or resolves an issue | Patch (`0.0.X`) |
| `refactor`| Code change that neither fixes a bug nor adds a feature | Patch |
| `perf` | Code change that improves performance | Patch |
| `test` | Adds missing tests or corrects existing test suites | None / Patch |
| `docs` | Documentation-only changes | None |
| `style` | Formatting, whitespace, semi-colons (no production logic change)| None |
| `build` | Changes to build configuration, dependencies, or package manifests | Patch |
| `ci` | Changes to CI/CD workflows, automation scripts, or tooling | None |
| `chore` | Routine maintenance tasks or housekeeping | None |
| `revert`| Reverts a previous commit | Dependent on target |

---

## 3. Scopes for `vibe-coding-og`

Recommended scopes include:
- `skills`: Additions or modifications to skill instruction sets.
- `agents`: Agent role prompts or behavioral configurations.
- `hooks`: Event-driven lifecycle hooks.
- `scripts`: Internal diagnostic, test runner, and detection scripts.
- `tests`: Test suites (unit, integration, hook, skill tests).
- `references`: Guidelines, checklists, ADRs, or documentation standards.
- `marketplace`: `.claude-plugin/` manifest and catalog changes.

---

## 4. Breaking Changes

Breaking changes must be indicated by:
1. Appending an exclamation mark `!` before the colon in the header:
   ```
   feat(scripts)!: change detect-project output schema to nested format
   ```
2. Or including `BREAKING CHANGE:` in the footer:
   ```
   feat(scripts): overhaul detect-project output structure

   BREAKING CHANGE: The `languages` array now returns language objects with versions instead of plain strings.
   ```
*SemVer Impact: Major (`X.0.0`)*

---

## 5. Concrete Examples

### Feature Addition
```
feat(skills): add doctor health-check skill for project diagnostics
```

### Bug Fix
```
fix(scripts): resolve false negative in Jest test runner detection

Ensure detect-test-runner.py inspects root package.json devDependencies
when custom test scripts are not explicitly declared.
```

### Documentation Update
```
docs(references): add model routing guidelines for Opus, Sonnet, and Haiku
```

### Build & Tooling
```
build(deps): update Node test runner fixtures in examples/node
```

### CI / Test Infrastructure
```
ci(tests): integrate integration test suite into pre-commit validation hook
```

### Multi-Paragraph with References
```
fix(hooks): sanitize output before emitting pre-commit check reports

Strip sensitive environment variables and credentials from git status
and command execution outputs to comply with security-checklist.md.

Fixes #42
```
