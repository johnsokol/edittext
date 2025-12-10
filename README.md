# edittext: A Complete Web CMS in 150 Lines of Bash

**Security Hardened Version**

**Original Author:** John Sokol (circa 2000s)  
**Security Hardening:** 2025

---

## Abstract

In an era dominated by complex web frameworks, databases, and microservices, it's easy to forget that powerful applications can be built with nothing more than standard Unix tools. This document examines **edittext**, a fully functional web-based content management system implemented entirely in Bash shell scripting. Originally written to win a bet, edittext demonstrates that a complete CRUD (Create, Read, Update, Delete) application with template rendering, persistent storage, and dynamic index generation can be achieved in approximately 150 lines of code using only bash, sed, awk, and grep.

This security-hardened version adds input sanitization, CSRF protection, file locking, and access logging while maintaining the original elegance and transparency.

---

## 1. Introduction

### 1.1 Origin Story

The edittext system was born from a simple wager. When challenged with the assertion that building a web CMS would require a "real" programming language, the author responded by creating a complete working system using only Bash CGI scripting. The proof of victory still exists in the system itself: FILE10.html, titled "Read this Jessie," contains the message:

> *"So it needs more input filtering, but its all here you can view source and see how I keep the data."*

This security-hardened version addresses that original caveat—now with proper input filtering.

### 1.2 Historical Context

edittext represents classic CGI-era web development, likely dating to the early 2000s. During this period, before the widespread adoption of PHP, Ruby on Rails, and Django, many web applications were built using simple CGI scripts. The Common Gateway Interface (CGI) allowed any executable program to generate dynamic web content by reading environment variables and standard input, then outputting HTTP headers and HTML to standard output.

### 1.3 Design Philosophy

edittext follows the Unix philosophy of small, composable tools that do one thing well. Rather than implementing a database, it uses the filesystem. Rather than using a template engine library, it uses sed substitution. Rather than maintaining separate data and presentation layers, it embeds metadata directly within HTML comments.

This same philosophy was later applied by the author at Vetronix/Robert Bosch Corporation (2008-2010), where a similar BusyBox + Bash architecture powered manufacturing test systems. Plain text scripts meant anyone—including factory workers in China—could debug issues directly. The transparency that made edittext work for a web CMS made the Bosch system work for hardware testing.

---

## 2. System Architecture

### 2.1 File Structure

The complete system consists of the following files:

| File | Lines | Purpose |
|------|-------|---------|
| `edittext.cgi` | ~300 | Main CGI handler (GET/POST requests) |
| `makeindex` | ~50 | Rebuilds index.html from all posts |
| `install.sh` | ~80 | Installation and setup script |
| `count` | 1 | Auto-increment counter for post IDs |
| `FILE*.html` | varies | Individual user-created posts |
| `index.html` | generated | Dynamic listing of all posts |
| `access.log` | generated | Audit trail of all operations |

**Total: ~430 lines for a complete, secure web CMS.**

### 2.2 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    edittext Data Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Browser ──GET/POST──→ edittext.cgi                             │
│                              │                                   │
│            ┌─────────────────┴─────────────────┐                │
│            │                                    │                │
│       [GET request]                      [POST request]          │
│            │                                    │                │
│     ┌──────┴──────┐                    ┌───────┴───────┐        │
│     │ ?name=N     │ no params          │ Validate CSRF │        │
│     │ Load FILE   │ New post           │ Sanitize input│        │
│     │ Parse DATA  │ Increment counter  │ HTML encode   │        │
│     └──────┬──────┘                    └───────┬───────┘        │
│            │                                    │                │
│            └─────────────┬─────────────────────┘                │
│                          │                                       │
│                   Render HTML                                    │
│                          │                                       │
│            ┌─────────────┴─────────────┐                        │
│            │                           │                         │
│     [Editor Form]               [Save FILE{N}.html]             │
│                                        │                         │
│                                  Run makeindex                   │
│                                        │                         │
│                                 Rebuild index.html               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Key Innovation: Self-Documenting Files

The most elegant aspect of edittext is how each saved post serves multiple purposes simultaneously. Every FILE{N}.html is:

1. **A viewable HTML page** — Users can browse directly to the file
2. **A data record** — The DATALINE comment stores the original URL-encoded form submission
3. **Its own index entry** — The LISTINGDATA comment contains pre-formatted HTML for the index page

This is achieved by embedding metadata within HTML comments in the document's `<head>` section:

```html
<!--
DATALINE subject=New+Title&limitedtextarea=Content+here&filename=21
LISTINGDATA <a href="/edittext/FILE21.html">New Title</a>, <a href="...">edit</a>
-->
```

This approach eliminates the need for a separate database entirely. The filesystem *is* the database, and each HTML file carries all the information needed to edit it or include it in the index.

### 3.1 The Round-Trip

When a user clicks "edit" on an existing post:

1. `GET /cgi-bin/edittext.cgi?name=21`
2. Script extracts DATALINE from FILE21.html
3. URL-encoded data is parsed back into form fields
4. Editor renders with content pre-filled
5. User edits and submits
6. POST data is sanitized, validated, and saved
7. makeindex rebuilds the listing

The DATALINE preserves the exact form submission, enabling perfect round-trip editing.

---

## 4. Security Hardening

The original edittext, as acknowledged in FILE10.html, needed "more input filtering." This version addresses all major vulnerabilities while maintaining the original simplicity.

### 4.1 Vulnerabilities Addressed

| Vulnerability | Risk | Fix |
|---------------|------|-----|
| **XSS Injection** | Script execution in browser | HTML entity encoding on all output |
| **Shell Injection** | Command execution on server | Input sanitization before sed/awk |
| **CSRF** | Unauthorized actions | Token validation on all POST requests |
| **Path Traversal** | File access outside webroot | Numeric-only filename validation |
| **Race Conditions** | Data corruption | flock() file locking |
| **Unlimited Input** | Resource exhaustion | Maximum length enforcement |
| **No Audit Trail** | Unknown access patterns | Comprehensive access logging |
| **Silent Failures** | Undetected errors | Strict mode (set -euo pipefail) |

### 4.2 Input Sanitization

All user input is HTML-encoded before output:

```bash
html_encode() {
    local str="$1"
    str="${str//&/&amp;}"
    str="${str//</&lt;}"
    str="${str//>/&gt;}"
    str="${str//\"/&quot;}"
    str="${str//\'/&#39;}"
    printf '%s' "$str"
}
```

**Before:** User submits `<script>alert('xss')</script>`  
**After:** Displayed as literal text `&lt;script&gt;alert('xss')&lt;/script&gt;`

### 4.3 CSRF Protection

Each form includes a cryptographic token:

```html
<input type="hidden" name="csrf_token" value="a1b2c3d4e5f6...">
```

The token is a SHA256 hash of:
- Server secret
- Client IP address  
- Current hour (allows 1-hour validity window)

POST requests without a valid token are rejected and logged.

### 4.4 File Locking

Concurrent access is protected with flock():

```bash
acquire_lock() {
    exec 200>"$LOCKFILE"
    if ! flock -w 5 200; then
        echo "System busy. Please try again."
        exit 1
    fi
}
```

This prevents data corruption when multiple users edit simultaneously.

### 4.5 Filename Validation

Path traversal attacks are prevented by strict validation:

```bash
validate_filename_num() {
    local num="$1"
    # Must be numeric only
    if [[ ! "$num" =~ ^[0-9]+$ ]]; then
        exit 1
    fi
    # Must be in valid range
    if [ "$num" -gt 99999 ] || [ "$num" -lt 1 ]; then
        exit 1
    fi
}
```

An attacker cannot request `?name=../../../etc/passwd` — only numeric IDs are accepted.

### 4.6 Access Logging

All operations create an audit trail:

```
2025-12-09 10:30:45|192.168.1.100|POST_SAVE|file=FILE42.html subject='My Post'
2025-12-09 10:31:02|192.168.1.101|GET_EDIT|file=FILE42.html
2025-12-09 10:32:15|192.168.1.102|CSRF_FAIL|Invalid token
2025-12-09 10:33:00|192.168.1.103|GET_NEW|new_id=43
```

---

## 5. Technical Implementation

### 5.1 URL Decoding

Form data arrives URL-encoded. The secure version uses bash parameter expansion:

```bash
urldecode() {
    local data="${1//+/ }"
    printf '%b' "${data//%/\\x}"
}
```

This handles all percent-encoded characters, not just the common ones.

### 5.2 Template Rendering

Rather than external template files with sed substitution (which risks injection), the secure version uses heredocs with properly escaped variables:

```bash
render_editor() {
    local safe_subject=$(html_encode "$subject")
    local safe_text=$(html_encode "$text")
    
    cat << EOF
    <input type="text" value="$safe_subject">
    <textarea>$safe_text</textarea>
EOF
}
```

Variables are sanitized *before* interpolation.

### 5.3 Index Generation

The makeindex script remains elegantly simple:

```bash
#!/bin/bash
set -euo pipefail

# Create header
cat > "$BASEDIR/index.html" << 'HEADER'
<!DOCTYPE html>
<html>...
HEADER

# Extract LISTINGDATA from all posts
for file in FILE*.html; do
    head -10 "$file" | grep "^LISTINGDATA" | sed 's/^LISTINGDATA //'
done >> "$BASEDIR/index.html"

# Close HTML
echo "</ul></body></html>" >> "$BASEDIR/index.html"
```

The `head -10` optimization means only the first 10 lines of each file are read—since LISTINGDATA is always in the `<head>` section, there's no need to read entire files.

---

## 6. Installation

### 6.1 Quick Start

```bash
# Download files
git clone https://github.com/johnsokol/edittext
cd edittext

# Run installer as root
sudo ./install.sh
```

### 6.2 Manual Installation

```bash
# Create directories
mkdir -p /htdocs/edittext
mkdir -p /cgi-bin

# Copy files
cp edittext.cgi /cgi-bin/
cp makeindex /htdocs/edittext/

# Initialize
echo "0" > /htdocs/edittext/count
touch /htdocs/edittext/access.log

# Set permissions
chmod 755 /cgi-bin/edittext.cgi
chmod 755 /htdocs/edittext/makeindex
chown -R www-data:www-data /htdocs/edittext

# Build initial index
/htdocs/edittext/makeindex
```

### 6.3 Web Server Configuration

**Apache:**
```apache
ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
<Directory "/usr/lib/cgi-bin">
    Options +ExecCGI
    Require all granted
</Directory>

Alias /edittext/ /htdocs/edittext/
```

**nginx (with fcgiwrap):**
```nginx
location /cgi-bin/ {
    fastcgi_pass unix:/var/run/fcgiwrap.socket;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME /usr/lib/cgi-bin$fastcgi_script_name;
}
```

### 6.4 Adding Authentication

For password protection, create `.htaccess`:

```apache
AuthType Basic
AuthName "edittext"
AuthUserFile /etc/htpasswd-edittext
Require valid-user
```

```bash
htpasswd -c /etc/htpasswd-edittext admin
```

---

## 7. Comparison: Original vs Secure

| Feature | Original (2000s) | Secure (2025) |
|---------|------------------|---------------|
| XSS Protection | ❌ None | ✅ HTML encoding |
| CSRF Protection | ❌ None | ✅ Token validation |
| Shell Injection | ❌ Vulnerable | ✅ Input sanitization |
| Path Traversal | ❌ Vulnerable | ✅ Numeric validation |
| File Locking | ❌ None | ✅ flock() |
| Input Limits | ❌ None | ✅ Length enforcement |
| Error Handling | ❌ Silent failures | ✅ Strict mode |
| Audit Trail | ❌ None | ✅ Access logging |
| Lines of Code | ~150 | ~430 |

The secure version is roughly 3x larger, but still remarkably small for a complete, secure web application.

---

## 8. Lessons and Legacy

### 8.1 The Unix Philosophy in Action

edittext exemplifies the Unix philosophy articulated by Doug McIlroy:

> "Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface."

Every component of edittext processes text: HTML templates, URL-encoded form data, and the files themselves. The security hardening maintains this principle—sanitization functions are small, focused, and composable.

### 8.2 The Sokol Design Pattern

This same architectural approach appears across the author's career:

| Era | System | Platform | Principle |
|-----|--------|----------|-----------|
| 2000s | edittext | Bash CGI | Plain text, anyone can debug |
| 2008 | Bosch Test System | BusyBox + Bash | Factory workers debug scripts |
| 2024 | AOS (Amorphous OS) | Browser JavaScript | AI-auditable, transparent apps |

The through-line: **No hidden complexity. No black boxes. Everything inspectable.**

### 8.3 Simplicity vs. Complexity

Modern web development often defaults to heavyweight frameworks, container orchestration, and microservice architectures. edittext serves as a reminder that many applications don't require such complexity. A bulletin board, simple CMS, or internal tool can often be built with nothing more than the tools already present on any Unix system.

### 8.4 The Value of Constraints

The constraint of using only Bash forced creative solutions:
- Embedding data in HTML comments (no database needed)
- Using the filesystem as storage (no ORM needed)
- Building a template engine from sed (no library needed)

These constraints produced an elegant, understandable system that serves as an excellent teaching tool for CGI fundamentals, Unix pipelines, and web architecture basics.

---

## 9. Limitations

Even with security fixes, edittext remains a simple system by design:

- **No user authentication** — Add via .htaccess or extend CGI
- **No rich text editing** — Plain text only (prevents complexity)
- **No image uploads** — Text content only (prevents storage issues)
- **No versioning** — Edits overwrite (could add git integration)
- **Single server** — Not distributed (files could sync via rsync)
- **No delete UI** — Files must be deleted manually (prevents accidents)

These are features, not bugs. The system does exactly what it needs to do, nothing more.

---

## 10. Conclusion

edittext stands as proof that sophisticated web applications can be built with surprisingly simple tools. In approximately 430 lines of Bash (300 for the CGI, 50 for makeindex, 80 for installation), using only standard Unix utilities, it implements a complete content management system with:

- Create, read, update operations
- Template-based rendering
- Persistent storage
- Dynamic index generation
- XSS and CSRF protection
- File locking for concurrency
- Complete audit trail

More importantly, it stands as proof that **Jesse lost the bet.**

---

## Appendix A: Configuration Reference

Edit the top of `edittext.cgi`:

```bash
BASEDIR="/htdocs/edittext"      # Data directory
WORKDIR="/edittext"             # URL path to data
THISCGI="/cgi-bin/edittext.cgi" # URL path to CGI
LOCKFILE="/tmp/edittext.lock"   # Lock file location
MAX_SUBJECT_LEN=100             # Max subject length
MAX_CONTENT_LEN=10000           # Max content length  
MAX_FILENAME_NUM=99999          # Max post ID
```

---

## Appendix B: Security Checklist

Before deploying to production:

- [ ] Enable HTTPS (required for CSRF token security)
- [ ] Set proper file permissions (755 for scripts, 644 for data)
- [ ] Configure web server correctly
- [ ] Add authentication if public-facing
- [ ] Review access.log regularly
- [ ] Backup data directory
- [ ] Test CSRF protection works
- [ ] Verify HTML encoding on output

---

## License

GNU General Public License v3.0

## Links

- **Repository:** https://github.com/johnsokol/edittext
- **Author:** http://www.johnsokol.com
- **Original Paper:** "edittext: A Complete Web CMS in 150 Lines of Bash"
