#!/usr/bin/env python3
"""
ASHFALL VFX FORGE — Build & Deploy Pipeline
Modular build system for patching, testing, and deploying.
"""
import json, os, re, subprocess, sys, urllib.request, urllib.error, time

PROJ = "/home/claude/ashfall-vfx-forge"
INDEX = f"{PROJ}/index.html"
WIKI = f"{PROJ}/wiki.html"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN","")
GITHUB_REPO = "MisTAiM/ashfall-vfx-forge"
VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN","")

# ══════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════

def log(msg, level="INFO"):
    colors = {"INFO": "\033[36m", "OK": "\033[32m", "ERR": "\033[31m", "WARN": "\033[33m", "PATCH": "\033[35m"}
    print(f"{colors.get(level, '')}[{level}]\033[0m {msg}")

def run(cmd, cwd=PROJ):
    """Run shell command with error handling."""
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"Command failed: {cmd}", "ERR")
        log(f"stderr: {r.stderr.strip()}", "ERR")
        return None
    return r.stdout.strip()

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    log(f"Wrote {path} ({len(content)} bytes)", "OK")

def patch_file(path, old, new, label=""):
    """Find-and-replace patch with validation."""
    content = read_file(path)
    if old not in content:
        log(f"PATCH FAILED — target string not found: {label or old[:60]}", "ERR")
        return False
    count = content.count(old)
    if count > 1:
        log(f"WARN: {count} matches found for patch '{label}', replacing first only", "WARN")
        content = content.replace(old, new, 1)
    else:
        content = content.replace(old, new)
    write_file(path, content)
    log(f"Patched: {label or old[:40]}... → {new[:40]}...", "PATCH")
    return True

def patch_between(path, start_marker, end_marker, new_content, label=""):
    """Replace everything between two markers (inclusive)."""
    content = read_file(path)
    pattern = re.escape(start_marker) + r'.*?' + re.escape(end_marker)
    if not re.search(pattern, content, re.DOTALL):
        log(f"PATCH BETWEEN FAILED — markers not found: {label}", "ERR")
        return False
    content = re.sub(pattern, start_marker + new_content + end_marker, content, count=1, flags=re.DOTALL)
    write_file(path, content)
    log(f"Patched between markers: {label}", "PATCH")
    return True

def inject_after(path, marker, new_content, label=""):
    """Inject content after a marker."""
    content = read_file(path)
    if marker not in content:
        log(f"INJECT FAILED — marker not found: {label}", "ERR")
        return False
    content = content.replace(marker, marker + new_content, 1)
    write_file(path, content)
    log(f"Injected after: {label}", "PATCH")
    return True

def inject_before(path, marker, new_content, label=""):
    """Inject content before a marker."""
    content = read_file(path)
    if marker not in content:
        log(f"INJECT FAILED — marker not found: {label}", "ERR")
        return False
    content = content.replace(marker, new_content + marker, 1)
    write_file(path, content)
    log(f"Injected before: {label}", "PATCH")
    return True

def validate_html(path):
    """Basic HTML validation."""
    content = read_file(path)
    errors = []
    if '<html' not in content: errors.append("Missing <html>")
    if '</html>' not in content: errors.append("Missing </html>")
    if '<script' in content and '</script>' not in content: errors.append("Unclosed <script>")
    # Count braces in script sections
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    for i, script in enumerate(scripts):
        opens = script.count('{') + script.count('(') + script.count('[')
        closes = script.count('}') + script.count(')') + script.count(']')
        if opens != closes:
            errors.append(f"Script block {i}: brace mismatch (open={opens}, close={closes})")
    if errors:
        for e in errors: log(e, "ERR")
        return False
    log(f"Validation passed: {path}", "OK")
    return True

# ══════════════════════════════════════
# GIT OPERATIONS
# ══════════════════════════════════════

def git_commit(message):
    run("git add -A")
    result = run(f'git commit -m "{message}"')
    if result is None:
        log("Nothing to commit or commit failed", "WARN")
        return False
    log(f"Committed: {message}", "OK")
    return True

def git_push():
    result = run("git push origin main")
    if result is None:
        log("Push failed", "ERR")
        return False
    log("Pushed to GitHub", "OK")
    return True

# ══════════════════════════════════════
# VERCEL DEPLOY
# ══════════════════════════════════════

def vercel_deploy():
    """Deploy to Vercel and poll until ready."""
    # Get repo ID
    log("Fetching repo info...", "INFO")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{GITHUB_REPO}",
        headers={"Authorization": f"token {GITHUB_TOKEN}"}
    )
    try:
        resp = urllib.request.urlopen(req)
        repo = json.loads(resp.read())
        repo_id = str(repo["id"])
    except Exception as e:
        log(f"Failed to get repo ID: {e}", "ERR")
        return None

    # Trigger deploy
    log("Triggering Vercel deployment...", "INFO")
    payload = json.dumps({
        "name": "ashfall-vfx-forge",
        "gitSource": {"type": "github", "repoId": repo_id, "ref": "main"},
        "target": "production", "projectSettings": {"framework": None}
    }).encode()
    req = urllib.request.Request(
        "https://api.vercel.com/v13/deployments",
        data=payload,
        headers={
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    try:
        resp = urllib.request.urlopen(req)
        deploy = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        log(f"Deploy failed: {e.code} — {body[:200]}", "ERR")
        return None

    deploy_id = deploy.get("id")
    deploy_url = deploy.get("url")
    log(f"Deployment started: {deploy_id}", "INFO")

    # Poll for ready
    for attempt in range(20):
        time.sleep(5)
        req = urllib.request.Request(
            f"https://api.vercel.com/v13/deployments/{deploy_id}",
            headers={"Authorization": f"Bearer {VERCEL_TOKEN}"}
        )
        try:
            resp = urllib.request.urlopen(req)
            status = json.loads(resp.read())
            state = status.get("readyState")
            log(f"  Poll {attempt+1}: {state}", "INFO")
            if state == "READY":
                url = f"https://{deploy_url}"
                log(f"DEPLOYED: {url}", "OK")
                return url
            if state in ("ERROR", "CANCELED"):
                log(f"Deploy failed with state: {state}", "ERR")
                return None
        except Exception as e:
            log(f"Poll error: {e}", "WARN")

    log("Deploy timed out after 100s", "ERR")
    return None

# ══════════════════════════════════════
# FULL PIPELINE
# ══════════════════════════════════════

def full_deploy(commit_msg="Update"):
    """Validate → Commit → Push → Deploy."""
    log("=" * 50, "INFO")
    log("ASHFALL VFX FORGE — Deploy Pipeline", "INFO")
    log("=" * 50, "INFO")

    # Validate
    if not validate_html(INDEX):
        log("Aborting deploy — validation failed", "ERR")
        return False

    # Git
    if not git_commit(commit_msg):
        log("No changes to deploy", "WARN")
        return True  # Not an error

    if not git_push():
        return False

    # Deploy
    url = vercel_deploy()
    if url:
        log(f"Live at: {url}", "OK")
        log(f"Wiki at: {url}/wiki.html", "OK")
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "deploy":
            msg = " ".join(sys.argv[2:]) or "Update"
            full_deploy(msg)
        elif cmd == "validate":
            validate_html(INDEX)
        elif cmd == "push":
            msg = " ".join(sys.argv[2:]) or "Update"
            git_commit(msg)
            git_push()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python3 build.py [deploy|validate|push] [message]")
    else:
        print("Usage: python3 build.py [deploy|validate|push] [message]")
