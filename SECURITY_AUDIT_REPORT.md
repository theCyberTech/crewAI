# CrewAI Security Audit Report

**Date:** 2026-01-24
**Auditor:** Security Audit System
**Version Audited:** 1.8.1
**Scope:** Full codebase security review

---

## Executive Summary

This security audit of the CrewAI framework identified **15 security findings** across different severity levels. The framework demonstrates security awareness through the use of linting tools (Bandit, Ruff), proper SQL parameterization, and YAML safe loading. However, several areas require attention, particularly around code execution, deserialization, and input validation.

| Severity | Count |
|----------|-------|
| Critical | 3 |
| High | 4 |
| Medium | 5 |
| Low | 3 |

---

## Critical Findings

### 1. Arbitrary Code Execution via `os.system()` in CodeInterpreterTool

**Location:** `lib/crewai-tools/src/crewai_tools/tools/code_interpreter_tool/code_interpreter_tool.py:383`

**Description:** The `run_code_unsafe()` method uses `os.system()` with an f-string to install packages, which is vulnerable to command injection.

```python
os.system(f"pip install {library}")  # noqa: S605
```

**Risk:** An attacker who can control the `libraries_used` parameter could execute arbitrary shell commands on the host system.

**Recommendation:**
- Remove `unsafe_mode` functionality or gate it behind explicit environment variable opt-in
- Use `subprocess.run()` with list arguments instead of shell string
- Validate library names against an allowlist pattern (e.g., `^[a-zA-Z0-9_-]+$`)

---

### 2. Arbitrary Code Execution via `exec()` in Unsafe Mode

**Location:** `lib/crewai-tools/src/crewai_tools/tools/code_interpreter_tool/code_interpreter_tool.py:388`

**Description:** The unsafe mode executes arbitrary Python code without any sandbox restrictions.

```python
exec(code, {}, exec_locals)  # noqa: S102
```

**Risk:** Complete system compromise if an attacker can control the code being executed.

**Recommendation:**
- Remove unsafe mode entirely, or
- Require explicit environment variable `CREWAI_ALLOW_UNSAFE_CODE=true`
- Add prominent warnings in documentation
- Log all unsafe code executions

---

### 3. Insecure Deserialization via Pickle

**Location:** `lib/crewai/src/crewai/utilities/file_handler.py:170`

**Description:** The `PickleHandler` class uses `pickle.load()` to deserialize data from files.

```python
return pickle.load(file)  # noqa: S301
```

**Risk:** Pickle deserialization can execute arbitrary code when loading malicious pickle files. This is a known attack vector (CWE-502).

**Recommendation:**
- Replace pickle with safer serialization formats (JSON, MessagePack)
- If pickle must be used, implement signature verification
- Restrict pickle file sources to trusted internal paths only

---

## High Severity Findings

### 4. SQL Injection Risk in NL2SQLTool

**Location:** `lib/crewai-tools/src/crewai_tools/tools/nl2sql/nl2sql_tool.py:57`

**Description:** The tool constructs SQL queries using f-strings with user-controlled input.

```python
f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"  # noqa: S608
```

**Risk:** SQL injection if table_name is not properly validated.

**Recommendation:**
- Use parameterized queries for all SQL operations
- Validate table_name against schema metadata
- Implement query allowlists

---

### 5. Path Traversal in File Tools

**Locations:**
- `lib/crewai-tools/src/crewai_tools/tools/file_read_tool/file_read_tool.py:80`
- `lib/crewai-tools/src/crewai_tools/tools/file_writer_tool/file_writer_tool.py:49`

**Description:** File read and write tools accept user-provided file paths without validation.

```python
with open(file_path, "r") as file:
    return file.read()
```

**Risk:** Attackers could read sensitive files (e.g., `/etc/passwd`, `.env`, private keys) or write to critical locations.

**Recommendation:**
- Implement path canonicalization and validation
- Restrict file operations to a configured sandbox directory
- Block access to sensitive file patterns (`.env`, `*.key`, `credentials*`)

---

### 6. Sandbox Bypass in Code Interpreter

**Location:** `lib/crewai-tools/src/crewai_tools/tools/code_interpreter_tool/code_interpreter_tool.py:52-137`

**Description:** The `SandboxPython` class attempts to restrict dangerous operations but has potential bypass vectors:

1. The `__builtins__` restriction can be bypassed via `().__class__.__bases__[0].__subclasses__()`
2. Module blocking is name-based and can be bypassed via `__import__` tricks

**Risk:** Code execution escaping the sandbox.

**Recommendation:**
- Always prefer Docker-based execution
- Consider using RestrictedPython library instead of custom sandbox
- Implement resource limits (CPU, memory, time)
- Add network isolation

---

### 7. Telemetry Data Exposure

**Location:** `lib/crewai/src/crewai/telemetry/telemetry.py`

**Description:** When `share_crew=True`, sensitive data including task descriptions, agent backstories, goals, and execution outputs are transmitted to external telemetry endpoints.

```python
if crew.share_crew:
    self._add_attribute(span, "crew_agents", json.dumps([{
        "goal": agent.goal,
        "backstory": agent.backstory,
        ...
    }]))
```

**Risk:** Unintentional data leakage of sensitive business logic or PII.

**Recommendation:**
- Make telemetry opt-in rather than opt-out
- Add data minimization - hash or redact sensitive fields
- Document exactly what data is collected
- Provide granular telemetry controls

---

## Medium Severity Findings

### 8. Weak Sandbox Module Blocklist

**Location:** `lib/crewai-tools/src/crewai_tools/tools/code_interpreter_tool/code_interpreter_tool.py:60-70`

**Description:** The blocklist is incomplete:
```python
BLOCKED_MODULES: ClassVar[set[str]] = {
    "os", "sys", "subprocess", "shutil", "importlib",
    "inspect", "tempfile", "sysconfig", "builtins",
}
```

Missing dangerous modules: `ctypes`, `multiprocessing`, `socket`, `signal`, `_thread`, `gc`, `traceback`, `code`, `codeop`, `pty`, `pipes`

**Recommendation:** Expand blocklist or use allowlist approach instead.

---

### 9. SSRF Risk in Web Tools

**Locations:** Multiple tools make HTTP requests to user-controlled URLs:
- `lib/crewai-tools/src/crewai_tools/rag/loaders/pdf_loader.py:40`
- Various web scraping tools

**Description:** User-controlled URLs could target internal services.

**Recommendation:**
- Implement URL validation (block private IP ranges, localhost)
- Use allowlists for permitted domains where possible
- Set appropriate timeouts and size limits

---

### 10. Dynamic Module Import in Authentication

**Location:** `lib/crewai/src/crewai/cli/authentication/main.py:67-68`

**Description:** Provider name is used to dynamically import modules:
```python
module = importlib.import_module(
    f"crewai.cli.authentication.providers.{settings.provider.lower()}"
)
```

**Risk:** If `settings.provider` is user-controlled, could potentially load unintended modules.

**Recommendation:** Validate provider against explicit allowlist before import.

---

### 11. Insufficient Token Validation

**Location:** `lib/crewai/src/crewai/cli/authentication/main.py`

**Description:** JWT tokens are validated but the code doesn't clearly enforce token expiration in all code paths.

**Recommendation:**
- Ensure token expiration is always checked
- Implement token refresh logic
- Add rate limiting on authentication attempts

---

### 12. Subprocess Execution Without Full Path Validation

**Locations:** Multiple files execute subprocess commands:
- `lib/crewai/src/crewai/cli/git.py` - Git commands
- Various tool installation commands using `subprocess.run()`

**Description:** While commands use list arguments (safe), they rely on PATH resolution which could be manipulated.

**Recommendation:**
- Use absolute paths for critical executables
- Validate command existence before execution

---

## Low Severity Findings

### 13. Hardcoded Test Credentials

**Locations:** Multiple test files contain hardcoded test credentials.

**Description:** Test files contain strings like `api_key="test-key"`, `password="test_password"`.

**Risk:** Low - these are test values, but could set bad examples.

**Recommendation:** Use environment variables or fixtures for test credentials.

---

### 14. Verbose Error Messages

**Locations:** Various error handlers expose internal state.

**Description:** Exception messages may leak internal paths, configuration details, or stack traces.

**Recommendation:** Implement structured error handling that sanitizes messages in production.

---

### 15. Default Timeout Values

**Locations:** Various HTTP clients and subprocess calls.

**Description:** Some operations use long or no timeouts, potential for resource exhaustion.

**Recommendation:** Implement consistent, configurable timeout policies.

---

## Positive Security Findings

The audit also identified several security best practices already in place:

1. **SQL Parameterization:** SQLite operations in `ltm_sqlite_storage.py` use proper parameterized queries
2. **YAML Safe Loading:** Configuration loading uses `yaml.safe_load()`
3. **Security Linting:** Project uses Bandit (S rules) and acknowledges security concerns with `# noqa: S###` comments
4. **JWT Validation:** Authentication uses PyJWT with proper verification
5. **Docker Isolation:** Code interpreter defaults to Docker execution for isolation
6. **Telemetry Opt-Out:** Users can disable telemetry via environment variables
7. **Input Validation:** Pydantic is used extensively for input validation

---

## Dependency Analysis

### Core Dependencies Review

| Package | Version | Security Notes |
|---------|---------|----------------|
| pydantic | ~2.11.9 | No known CVEs |
| openai | ~1.83.0 | Keep updated for API security |
| chromadb | ~1.1.0 | Local vector DB, limited exposure |
| pyjwt | >=2.9.0 | Ensure algorithm verification |
| requests | ~2.32.5 | No known CVEs |
| docker | ~7.1.0 | Ensure Docker daemon security |

### Recommendations
- Implement automated dependency scanning (Dependabot, Snyk)
- Pin exact versions in production deployments
- Regularly audit transitive dependencies

---

## Remediation Priority Matrix

| Finding | Severity | Effort | Priority |
|---------|----------|--------|----------|
| #1 os.system() injection | Critical | Low | Immediate |
| #2 Unsafe exec() | Critical | Medium | Immediate |
| #3 Pickle deserialization | Critical | Medium | High |
| #4 SQL injection | High | Low | High |
| #5 Path traversal | High | Medium | High |
| #6 Sandbox bypass | High | High | Medium |
| #7 Telemetry exposure | High | Medium | Medium |
| #8 Module blocklist | Medium | Low | Medium |
| #9 SSRF risk | Medium | Medium | Medium |
| #10 Dynamic import | Medium | Low | Low |
| #11 Token validation | Medium | Medium | Low |
| #12 Subprocess paths | Medium | Low | Low |
| #13 Test credentials | Low | Low | Low |
| #14 Error messages | Low | Medium | Low |
| #15 Timeouts | Low | Low | Low |

---

## Recommendations Summary

### Immediate Actions (Critical)
1. Add input validation to `os.system()` call or replace with `subprocess.run()`
2. Gate unsafe code execution behind explicit opt-in
3. Replace pickle with JSON serialization

### Short-Term Actions (High)
4. Implement path validation in file tools
5. Use parameterized queries in NL2SQL tool
6. Review and enhance code sandbox

### Medium-Term Actions
7. Implement SSRF protections
8. Add telemetry data minimization
9. Expand security test coverage

### Long-Term Actions
10. Implement security-focused CI/CD pipeline
11. Conduct regular dependency audits
12. Establish vulnerability disclosure program

---

## Conclusion

CrewAI demonstrates security awareness through its use of security linting tools and safe coding practices in many areas. However, the nature of an AI agent framework that executes code and accesses files introduces inherent security challenges that require careful attention.

The critical findings around code execution and deserialization should be addressed immediately, while the medium and low severity findings can be addressed as part of regular development cycles.

---

*This report was generated as part of a security audit. For questions or clarifications, please contact the security team.*
