# Security Checklist

Actionable security baseline for `vibe-coding-og` workflows, code generation, and automated review.

---

## 1. Secrets Management
- [ ] **No Hardcoded Secrets**: Ensure zero API keys, tokens, private keys, passwords, or database credentials exist in source code or commits.
- [ ] **Local Environment Isolation**: Ensure sensitive variables reside in untracked `.env` files; confirm `.env*` is ignored by `.gitignore`.
- [ ] **Secret Sanitization**: Sanitize URLs, stack traces, and terminal logs before display (e.g., strip `https://user:token@github.com`).
- [ ] **Pre-Commit Secret Scanning**: Integrate secret detection (e.g., `gitleaks`, `detect-secrets`) to block commits containing high-entropy strings.
- [ ] **Secret Rotation & Revocation**: Verify immediate key revocation processes exist for any accidentally committed credentials.

---

## 2. Authentication (AuthN)
- [ ] **Strong Password & Secret Hashing**: Use modern salted algorithms (Argon2id, bcrypt, PBKDF2); never store plain text or MD5/SHA1 hashes.
- [ ] **Secure Token Standards**: Use signed JWTs (RS256 / EdDSA preferred) with strict signature verification and explicit algorithm validation (`alg != "none"`).
- [ ] **Token Expiration & Refresh**: Enforce short lifespans for access tokens (15-60 min) with secure, revocable refresh tokens stored in `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
- [ ] **Rate Limiting on Auth Endpoints**: Protect login, password reset, and MFA endpoints against brute-force attacks.

---

## 3. Authorization (AuthZ) & Access Control
- [ ] **Principle of Least Privilege**: Grant users, processes, and API tokens the minimum necessary permissions.
- [ ] **Object-Level Validation (IDOR Prevention)**: Validate that the authenticated subject owns or has explicit permission to access requested entity IDs (e.g., `/api/documents/{id}`).
- [ ] **Role-Based Access Control (RBAC)**: Ensure server-side middleware or route guards enforce role boundaries; never rely solely on client-side routing.
- [ ] **Fail Secure / Deny by Default**: Unrecognized routes or unauthenticated requests must default to access denied (`401 Unauthorized` or `403 Forbidden`).

---

## 4. OWASP Top 10 Mitigation
- [ ] **Injection (SQL/NoSQL/Command)**:
  - Use parameterized queries, ORM prepared statements, or query builders exclusively.
  - Never concatenate raw user input into shell commands or SQL statements.
- [ ] **Cross-Site Scripting (XSS)**:
  - Sanitize and contextualize all user-rendered HTML.
  - Avoid `dangerouslySetInnerHTML`, `v-html`, or equivalent raw sinks unless paired with an approved sanitizer (e.g., DOMPurify).
  - Deploy Content Security Policy (`CSP`) headers.
- [ ] **Cross-Site Request Forgery (CSRF)**:
  - Use anti-CSRF tokens for state-changing operations or enforce `SameSite=Strict` / `Lax` cookies with custom request headers (`X-Requested-With`).
- [ ] **Server-Side Request Forgery (SSRF)**:
  - Validate and whitelist target domains and IPs when making outbound HTTP requests on behalf of users.
  - Block requests resolving to private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`, `169.254.169.254`).
- [ ] **Security Misconfiguration**:
  - Disable debug modes, detailed stack traces, and default accounts in non-development environments.
  - Set security headers (`Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).

---

## 5. Dependency Security
- [ ] **Deterministic Lockfiles**: Commit lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`) to ensure repeatable builds.
- [ ] **Vulnerability Audits**: Run automated vulnerability scanners (`npm audit`, `pip-audit`, `cargo audit`, or Snyk) during development and CI.
- [ ] **Minimal Dependency Surface**: Avoid installing unmaintained or bloated packages for trivial operations.
- [ ] **Dependency Pinning & Verification**: Validate package integrity hashes during installs.

---

## 6. Cloud & Infrastructure Security
- [ ] **Non-Root Execution**: Ensure containers execute as non-privileged users (`USER appuser`).
- [ ] **Minimal Container Images**: Use distroless or minimal base images (e.g. `alpine`, `distroless`) with no unused packages.
- [ ] **Encryption in Transit & at Rest**: Enforce TLS 1.3/1.2 for all ingress and inter-service traffic. Encrypt database volumes and object storage buckets.
- [ ] **Cloud IAM Boundaries**: Restrict cloud service accounts to specific resources using IAM conditions and explicit action whitelists.

---

## 7. CI/CD Pipeline Security
- [ ] **Minimal `GITHUB_TOKEN` Permissions**: Enforce `permissions: read-all` at top-level; grant `write` access strictly per-job where required.
- [ ] **Pin Actions by Full Commit SHA**: Pin third-party GitHub Actions to immutable full commit SHAs (e.g., `actions/checkout@b4ffde...`) rather than mutable tags (`@v4`).
- [ ] **Protected Branches**: Require pull request reviews, passing status checks, and linear history before merging to `main`.
- [ ] **Sanitized CI Logs**: Mask secrets and sensitive parameters in CI runner outputs.
