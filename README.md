# Secure Code Review: Flask Application

A secure code review of a deliberately vulnerable **Flask** web application, combining **manual code analysis** with **static application security testing (SAST)** using **Bandit**. The repository contains the vulnerable application, a fully remediated version, and the scan results. Developed as **Task 3 of the CodeAlpha Cybersecurity Internship**.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![Bandit](https://img.shields.io/badge/SAST-Bandit-yellow)
![Findings](https://img.shields.io/badge/Bandit%20findings-6%20→%200-brightgreen)

---

## Overview

| File | Purpose |
|---|---|
| `app.py` | Deliberately vulnerable application (**do not deploy**) |
| `app_fixed.py` | Remediated application with every finding fixed |
| `bandit_report.html` | Bandit SAST report for `app.py` |
| `screenshots/` | Evidence from the review and remediation |

**Result:** Bandit reports **6 issues** in `app.py` and **0 issues** in `app_fixed.py`.

## Methodology

1. **Manual review:** traced every point where user input enters the application (`request.args`) and followed it to where it is used (SQL queries, HTML output, deserialization).
2. **Automated SAST:** scanned the code with Bandit to confirm findings and catch insecure configuration.
3. **Verification:** confirmed each vulnerability was exploitable in the original app.
4. **Remediation:** applied industry-standard fixes and re-tested with the same inputs and a fresh Bandit scan.

## Findings and Remediation

| # | Vulnerability | OWASP Top 10 (2021) | Location in `app.py` | Remediation in `app_fixed.py` |
|---|---|---|---|---|
| 1 | Hardcoded credentials | A07 Identification & Authentication Failures | `ADMIN_PASSWORD = "admin123"` | Secret read from the `ADMIN_PASSWORD` environment variable |
| 2 | SQL injection | A03 Injection | `get_user()` builds the query by string concatenation | Parameterized query (`WHERE username = ?`) |
| 3 | Reflected cross-site scripting (XSS) | A03 Injection | `/greet` inserts `name` into HTML | Output escaped with `markupsafe.escape` |
| 4 | Insecure deserialization (remote code execution) | A08 Software & Data Integrity Failures | `/load` calls `pickle.loads` on user input | JSON parsing, strict base64 validation, escaped output |
| 5 | Debug mode enabled, bound to all interfaces | A05 Security Misconfiguration | `app.run(debug=True, host='0.0.0.0')` | `debug=False`, bound to `127.0.0.1` |

### Details

**1. Hardcoded credentials:** secrets committed to source code are exposed to anyone with repository access and remain in the Git history. They belong in environment variables or a secrets manager.

**2. SQL injection:** concatenating input into SQL lets an attacker change the query itself (e.g. `' OR '1'='1` returns every row). Parameterized queries send input to the database strictly as data.

**3. Cross-site scripting:** unescaped input such as `<script>…</script>` executes in the victim's browser and can steal session cookies. Escaping converts `<` and `>` into HTML entities so the browser displays them as text.

**4. Insecure deserialization:** Python's `pickle` format can instruct the interpreter to call functions while loading, so unpickling untrusted data lets an attacker execute code on the server. JSON can only represent data. The fixed version also escapes the decoded value and rejects malformed input with HTTP 400.

**5. Security misconfiguration:** Flask's debug mode exposes stack traces and an interactive debugger, and `0.0.0.0` makes the server reachable from the entire network.

## Bandit Results

| Test ID | Issue | Severity | `app.py` | `app_fixed.py` |
|---|---|---|---|---|
| B201 | Flask app run with `debug=True` | High | ❌ | ✅ |
| B301 | `pickle` deserialization of untrusted data | Medium | ❌ | ✅ |
| B608 | SQL built by string concatenation | Medium | ❌ | ✅ |
| B104 | Binding to all interfaces | Medium | ❌ | ✅ |
| B105 | Hardcoded password string | Low | ❌ | ✅ |
| B403 | Import of the `pickle` module | Low | ❌ | ✅ |

Bandit did not flag the XSS in `/greet`. Pattern-based SAST tools often miss context-dependent flaws, which is why manual review remains essential.

## Getting Started

### Requirements
- Python 3.8+
- Linux, macOS or Windows

### Installation
```bash
git clone https://github.com/HailshZ/CodeAlpha_Task3_Secure_Code_Review.git
cd CodeAlpha_Task3_Secure_Code_Review

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run the SAST scan
```bash
bandit -r app.py                                  # 6 findings
bandit -r app_fixed.py                            # 0 findings
bandit -r app.py -f html -o bandit_report.html    # HTML report
```

### Run the applications
Start them with the Flask CLI, bound to localhost:

```bash
flask --app app run --host 127.0.0.1 --port 5000          # vulnerable version
flask --app app_fixed run --host 127.0.0.1 --port 5001    # remediated version
```

> ⚠️ Don't start the vulnerable version with `python app.py`. That enables the debug server on all network interfaces.

### Verify the XSS fix
```bash
# Vulnerable: the script tag is returned unchanged
curl -G --data-urlencode "name=<script>alert(1)</script>" http://127.0.0.1:5000/greet

# Remediated: the script tag is escaped
curl -G --data-urlencode "name=<script>alert(1)</script>" http://127.0.0.1:5001/greet
# <h1>Hello, &lt;script&gt;alert(1)&lt;/script&gt;</h1>
```

### Verify the deserialization fix
```bash
# Valid JSON is accepted and safely escaped
curl -G --data-urlencode "data=$(echo -n '{"user":"hazel"}' | base64)" http://127.0.0.1:5001/load

# Anything that is not base64-encoded JSON (including pickle data) is rejected with HTTP 400
curl -i -G --data-urlencode "data=not-valid" http://127.0.0.1:5001/load
```

## Screenshots

**Bandit SAST scan of the vulnerable application**
![Bandit scan](screenshots/figure_1_bandit_scan.png)

**Manual review: hardcoded credentials**
![Hardcoded credentials](screenshots/figure_2_hardcoded_credentials.png)

**Remediation: parameterized query**
![Parameterized query](screenshots/figure_3_parameterized_query.png)

## Scope and Limitations

- `get_user()` demonstrates the SQL injection pattern for code review. It isn't exposed through an HTTP route, and no `users.db` is created.
- `ADMIN_PASSWORD` illustrates secret handling. The application has no login feature.
- The project focuses on code-level flaws. A production review would also cover authentication, session management, CSRF protection, security headers and dependency scanning, and would add dynamic testing (DAST) with tools such as OWASP ZAP or Burp Suite.

## Ethical Use

`app.py` is intentionally insecure and exists for education only. Never deploy it or expose it to a network.

## Author

**Hailemariam Zeleke**
Full Stack Developer | Ethical Hacker
[Portfolio](https://hailemariamzelekeportfolio.netlify.app) · [GitHub](https://github.com/HailshZ) · [LinkedIn](https://www.linkedin.com/in/hailemariam-zeleke-38178329a)
