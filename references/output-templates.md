# Standard Output Templates

This document provides reusable report formats for skills, hooks, and automated workflows within `vibe-coding-og`.

---

## 1. System Diagnostics Report (`doctor`)

```markdown
# System Diagnostics Report

**Project**: [PROJECT_NAME]  
**Timestamp**: [YYYY-MM-DD HH:MM:SS UTC]  
**Overall Status**: [PASS | WARN | FAIL]

---

### Environment & Runtimes
| Component | Detected Version | Expected / Minimum | Status |
| :--- | :--- | :--- | :---: |
| [Runtime Name] | [e.g. Node v20.10.0] | [e.g. >= 18.0.0] | [✓ / ✗] |
| [Package Manager] | [e.g. pnpm 8.15.0] | [e.g. >= 8.0.0] | [✓ / ✗] |
| Git | [e.g. 2.43.0] | [Configured: Yes] | [✓ / ✗] |

### Dependency Status
- **Lockfile Present**: [Yes / No] ([LOCKFILE_NAME])
- **Dependencies Installed**: [Yes / No]
- **Diagnostic Issues**:
  - `[ERROR | WARN]`: [Issue description and impact]

### Recommended Remediation
1. [Actionable step 1]
2. [Actionable step 2]
```

---

## 2. Test Execution Report

```markdown
# Test Execution Report

**Project**: [PROJECT_NAME]  
**Test Runner**: [e.g. pytest | Maven surefire | Jest]  
**Command Executed**: `[COMMAND]`  
**Result**: [PASS | FAIL] (Exit Code: [CODE])

---

### Summary Metrics
| Total Tests | Passed | Failed | Skipped | Duration |
| :---: | :---: | :---: | :---: | :---: |
| [TOTAL] | [PASSED] | [FAILED] | [SKIPPED] | [TIME]s |

### Failure Details (if applicable)
```text
[PASTE CONCISE STACK TRACE OR TEST FAILURE SUMMARY HERE]
```

### Analysis & Next Steps
- **Failing Tests**: `[test_module_or_class.test_name]`
- **Root Cause**: [Brief explanation of why the assertion or test failed]
- **Suggested Fix**: [Proposed code modification]
```

---

## 3. Code Review Report

```markdown
# Code Review Report

**Pull Request / Branch**: `[BRANCH_NAME]`  
**Review Tier**: [Sonnet | Opus]  
**Decision**: [APPROVE | REQUEST_CHANGES | COMMENT]

---

### Key Findings Summary
| Severity | Category | File | Description |
| :---: | :--- | :--- | :--- |
| **CRITICAL** | Architecture / Bug | `[path/to/file.ext#L10]` | [High-risk issue] |
| **MAJOR** | Maintainability | `[path/to/file.ext#L42]` | [Performance or structural flaw] |
| **MINOR** | Code Style | `[path/to/file.ext#L85]` | [Naming or formatting improvement] |

---

### Detailed Feedback

#### [File Path or Component]
- **Issue**: [Concise explanation of the problem]
- **Suggestion**:
  ```[language]
  // Suggested replacement or diff
  ```
- **Rationale**: [Why this change improves correctness, security, or maintainability]

---

### Positive Highlights
- [Notable clean code patterns, great test coverage, or elegant architectural decisions]
```

---

## 4. Security Audit Report

```markdown
# Security Audit Report

**Target**: [PROJECT_NAME / COMMIT_HASH]  
**Audit Standard**: OWASP Top 10 & vibe-coding-og Security Checklist  
**Verdict**: [PASS | CONDITIONAL_PASS | BLOCKING_FAIL]

---

### Vulnerability Matrix
| ID | Severity | Category | File / Location | Remediation Effort |
| :--- | :---: | :--- | :--- | :---: |
| SEC-01 | **CRITICAL** | Secrets Management | `.env.local` committed | Immediate |
| SEC-02 | **HIGH** | Injection / SSRF | `src/api/fetch.py#L44` | Low |
| SEC-03 | **MEDIUM** | AuthN / AuthZ | Missing role check on `/admin` | Medium |

---

### Finding Breakdown

#### [SEC-01] [Vulnerability Title]
- **Severity**: [CRITICAL | HIGH | MEDIUM | LOW]
- **Impact**: [What an attacker could accomplish if exploited]
- **Proof of Concept / Affected Code**:
  ```[language]
  [Snippet showing vulnerable pattern]
  ```
- **Remediation**:
  ```[language]
  [Secure pattern implementation]
  ```
- **Verification Command**: `[Command to verify fix]`
```

---

## 5. Pre-Commit Verification Report

```markdown
# Pre-Commit Verification Report

**Branch**: `[BRANCH_NAME]`  
**Status**: [READY_TO_COMMIT | BLOCKED]

---

### Verification Checklist
- [x] **Linting & Formatting**: Clean (No syntax errors or style violations)
- [x] **Static Type Check**: Passed (0 errors)
- [x] **Automated Tests**: Passed ([PASSED]/[TOTAL] tests)
- [x] **Secrets Scan**: Clean (No API keys or sensitive tokens detected)
- [x] **Git Cleanliness**: Staged files match conventional commit scope

### Commit Message Suggestion
```text
[type]([scope]): [imperative description without period]
```

### Action Required
- [Proceed with `git commit`] OR [List remaining fixes before committing]
```
