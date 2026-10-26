#!/usr/bin/env python3
"""lint.py — deterministic health check for an agent-maintained Obsidian vault.

The one script allowed by AGENTS.md (see "Tooling"). Stdlib only, no network,
no LLM, no config file, no --fix. It reports; a human or an agent decides.

    python3 lint.py [VAULT_ROOT] [--json] [--quiet]

Exit codes: 0 = clean (no errors), 1 = errors found, 2 = usage or internal error.

Checks
------
LINK001  error    wikilink resolves to no file
LINK002  warning  wikilink matches more than one file (ambiguous)
LINK003  warning  wikilink resolves to no file inside progress/ — a record, not a gap
FM001    error    page has no frontmatter
FM002    error    frontmatter is missing a required key
FM003    error    frontmatter value invalid (type, status, date, list syntax)
FM004    error    frontmatter carries a key the contract does not define
IDX001   error    page in wiki/<project>/ not linked from that project's index
                  (progress records are exempt: numbered, not linked)
IDX002   error    project folder not listed in wiki/index.md
TITLE001 error    H1 does not match the filename stem
NAME001  error    filename contains a character that breaks wikilinks
DUP001   error    two pages in one project share a basename
ORPHAN001 warning  page has no inbound link and appears in no index
                  (progress records are exempt: numbered, not linked)

What is deliberately not checked
--------------------------------
Link targets are the commodity part of this tool — an editor that renders the
vault shows unresolved links already. The rules that matter here are the ones
no editor knows about: frontmatter schema, index completeness, title/filename
agreement, filename legality. Treat LINK001 as the floor, not the product.

Nothing in raw/ is inspected: it is write-once and immutable, so a finding
there would be a finding nobody may fix. It is still indexed, so links into it
resolve.

Example wikilinks inside fenced code and inline code are stripped before
scanning — AGENTS.md and tasks.md contain them as syntax, not as links.
"""

import argparse
import datetime
import json
import os
import re
import sys

# --- contract constants -----------------------------------------------------

PAGE_TYPES = {"entity", "concept", "source", "synthesis", "note", "index", "progress"}
STATUSES = {"done": 1, "wip": 1, "blocked": 1}
PAGE_KEYS = {"type", "created", "updated", "sources", "tags"}
PROGRESS_KEYS = {"type", "date", "agent", "status", "sources", "tags"}
PAGE_REQUIRED = ("type", "created", "updated")
PROGRESS_REQUIRED = ("type", "date", "agent", "status")

# Root contract file and the vault's own system files: exempt from the page
# schema and the title rule. `log.md` carries no frontmatter by design.
EXEMPT_NAMES = {"AGENTS.md", "index.md", "log.md", "tasks.md"}

SKIP_DIRS = {".git", ".obsidian", ".trash", "raw"}

FORBIDDEN_FILENAME_CHARS = set("[]{ }|#^".replace(" ", ""))

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FLOW_LIST_RE = re.compile(r"^\[.*\]$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s?(.*)$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)*\1")
WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+)\]\]")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")


class Finding:
    __slots__ = ("path", "line", "code", "severity", "message")

    def __init__(self, path, line, code, severity, message):
        self.path = path
        self.line = line
        self.code = code
        self.severity = severity
        self.message = message

    def sort_key(self):
        return (self.path, self.line, self.code)

    def as_dict(self):
        return {
            "path": self.path,
            "line": self.line,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


# --- vault model ------------------------------------------------------------


def walk_vault(root):
    """Every .md path in the vault, relative, POSIX separators, sorted."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(".md"):
                full = os.path.join(dirpath, name)
                found.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(found)


def strip_code(lines):
    """Yield (lineno, text) for lines outside fenced blocks, inline code removed."""
    fence = None
    for n, line in enumerate(lines, 1):
        stripped = line.lstrip()
        m = FENCE_RE.match(stripped)
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        yield n, INLINE_CODE_RE.sub("", line)


def scan_links(lines):
    """[(lineno, raw_target)] for every wikilink outside code."""
    links = []
    for n, text in strip_code(lines):
        for m in WIKILINK_RE.finditer(text):
            links.append((n, m.group(1).strip()))
    return links


def link_target(raw):
    """Split [[Target#Heading|Alias]] into the page part."""
    target = raw.split("|", 1)[0]
    target = target.split("#", 1)[0]
    return target.strip()


def first_h1(lines):
    for n, text in strip_code(lines):
        m = H1_RE.match(text)
        if m:
            return n, m.group(1)
    return None, None


def parse_frontmatter(lines):
    """Return (entries, end_line) where entries = [(key, lineno, value)] or None."""
    if not lines or lines[0].strip() != "---":
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            entries = []
            for offset, raw in enumerate(lines[1:i], start=2):
                if not raw.strip() or raw.lstrip().startswith("#"):
                    continue
                entries.append((offset, raw))
            return entries, i + 1
    return None, 0


class Resolver:
    def __init__(self, paths):
        self.by_path = {}
        self.by_name = {}
        for path in paths:
            stem = path[:-3] if path.endswith(".md") else path
            self.by_path.setdefault(stem, []).append(path)
            self.by_name.setdefault(stem.rsplit("/", 1)[-1], []).append(path)

    @staticmethod
    def _distance(from_dir, path):
        """Path distance between the linking file's directory and a candidate."""
        a = from_dir.split("/") if from_dir else []
        b = path.split("/")[:-1]
        common = 0
        for x, y in zip(a, b):
            if x != y:
                break
            common += 1
        return (len(a) - common) + (len(b) - common)

    def resolve(self, target, from_path=None):
        """Paths a wikilink target could mean, using Obsidian's own tolerance.

        Exact path, then basename, then relative suffix. When a basename is
        shared, the nearest file wins — that is what Obsidian does, and calling
        every shared basename ambiguous would flag links that work on screen.
        Only a genuine tie survives as ambiguity.
        """
        if not target:
            return []
        stem = target[:-3] if target.endswith(".md") else target
        hits = self.by_path.get(stem)
        if hits:
            return list(hits)
        hits = self.by_name.get(stem)
        if not hits:
            suffix = "/" + stem
            hits = [p for s, paths in self.by_path.items() if s.endswith(suffix) for p in paths]
        if len(hits) > 1 and from_path:
            from_dir = from_path.rsplit("/", 1)[0] if "/" in from_path else ""
            scored = sorted((self._distance(from_dir, p), p) for p in hits)
            if scored[0][0] < scored[1][0]:
                return [scored[0][1]]
        return list(hits)


# --- frontmatter checks -----------------------------------------------------


def valid_date(value):
    if not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def check_frontmatter(path, lines, findings):
    entries, _ = parse_frontmatter(lines)
    is_progress = "/progress/" in path

    if entries is None:
        findings.append(
            Finding(path, 1, "FM001", "error", "no frontmatter block at the top of the file")
        )
        return

    keys = {}
    for lineno, raw in entries:
        m = KEY_RE.match(raw)
        if not m:
            findings.append(
                Finding(path, lineno, "FM003", "error", "unparseable frontmatter line: %s" % raw.strip())
            )
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in keys:
            findings.append(
                Finding(path, lineno, "FM003", "error", "duplicate frontmatter key %r" % key)
            )
            continue
        keys[key] = (lineno, value)

    allowed = PROGRESS_KEYS if is_progress else PAGE_KEYS
    required = PROGRESS_REQUIRED if is_progress else PAGE_REQUIRED

    for key, (lineno, _) in keys.items():
        if key not in allowed:
            findings.append(
                Finding(
                    path,
                    lineno,
                    "FM004",
                    "error",
                    "key %r is not part of the page contract (allowed: %s)"
                    % (key, ", ".join(sorted(allowed))),
                )
            )

    for key in required:
        if key not in keys:
            findings.append(
                Finding(path, 1, "FM002", "error", "frontmatter missing required key %r" % key)
            )

    def check_date(key):
        if key not in keys:
            return
        lineno, value = keys[key]
        if not valid_date(value):
            findings.append(
                Finding(path, lineno, "FM003", "error", "%s is not a valid YYYY-MM-DD date: %r" % (key, value))
            )

    if is_progress:
        check_date("date")
    else:
        check_date("created")
        check_date("updated")

    if "type" in keys:
        lineno, value = keys["type"]
        if value not in PAGE_TYPES:
            findings.append(
                Finding(
                    path,
                    lineno,
                    "FM003",
                    "error",
                    "type %r is not one of: %s" % (value, ", ".join(sorted(PAGE_TYPES))),
                )
            )
        elif is_progress and value != "progress":
            findings.append(
                Finding(path, lineno, "FM003", "error", "page in progress/ must have type: progress")
            )
        elif not is_progress and value == "progress":
            findings.append(
                Finding(path, lineno, "FM003", "error", "type: progress outside progress/")
            )

    if "status" in keys:
        lineno, value = keys["status"]
        if value not in STATUSES:
            findings.append(
                Finding(
                    path,
                    lineno,
                    "FM003",
                    "error",
                    "status %r is not one of: done, wip, blocked" % value,
                )
            )

    for key in ("sources", "tags"):
        if key not in keys:
            continue
        lineno, value = keys[key]
        if not FLOW_LIST_RE.match(value):
            findings.append(
                Finding(path, lineno, "FM003", "error", "%s must be a flow list, e.g. [\"raw/x.md\"]" % key)
            )
            continue
        if key == "sources":
            inner = value[1:-1].strip()
            if inner:
                items = re.findall(r'"([^"]*)"|\'([^\']*)\'', inner)
                leftover = re.sub(r'"[^"]*"|\'[^\']*\'', "", inner).replace(",", "").strip()
                if leftover:
                    findings.append(
                        Finding(path, lineno, "FM003", "error", "sources entries must be quoted strings")
                    )
                for quoted, single in items:
                    source = quoted or single
                    # A URL is a legitimate provenance record: the source exists,
                    # it just is not a file in raw/. Forcing a local path would
                    # make an agent invent one.
                    if source.startswith(("http://", "https://")):
                        continue
                    if not os.path.exists(os.path.join(BASE_DIR, source)):
                        findings.append(
                            Finding(path, lineno, "FM003", "error", "sources path does not exist: %s" % source)
                        )


# --- checks -----------------------------------------------------------------


def check_links(pages, resolver, findings):
    for path, lines in pages.items():
        # log.md is append-only history. A pointer that has since been renamed
        # is the record of that rename, not a defect to repair.
        if path == "wiki/log.md":
            continue
        historical = "/progress/" in path
        for lineno, raw in scan_links(lines):
            target = link_target(raw)
            if not target:
                findings.append(
                    Finding(path, lineno, "LINK001", "error", "empty wikilink target [[%s]]" % raw)
                )
                continue
            hits = resolver.resolve(target, path)
            if not hits:
                findings.append(
                    Finding(
                        path,
                        lineno,
                        "LINK003" if historical else "LINK001",
                        "warning" if historical else "error",
                        "wikilink target not found: [[%s]]%s"
                        % (target, " (immutable progress record)" if historical else ""),
                    )
                )
            elif len(hits) > 1:
                findings.append(
                    Finding(
                        path,
                        lineno,
                        "LINK002",
                        "warning",
                        "wikilink [[%s]] matches %d files: %s"
                        % (target, len(hits), ", ".join(sorted(hits))),
                    )
                )


def check_titles(pages, findings):
    for path, lines in pages.items():
        name = path.rsplit("/", 1)[-1]
        if name in EXEMPT_NAMES or "/progress/" in path:
            continue
        lineno, title = first_h1(lines)
        stem = name[:-3]
        if title is None:
            findings.append(
                Finding(path, 1, "TITLE001", "error", "no H1 heading")
            )
        elif title != stem:
            findings.append(
                Finding(
                    path,
                    lineno,
                    "TITLE001",
                    "error",
                    "H1 %r does not match filename %r" % (title, stem),
                )
            )


def check_filenames(all_paths, findings):
    for path in all_paths:
        name = path.rsplit("/", 1)[-1]
        bad = sorted(ch for ch in name if ch in FORBIDDEN_FILENAME_CHARS)
        if bad:
            findings.append(
                Finding(path, 1, "NAME001", "error", "filename contains %s" % ", ".join(repr(c) for c in bad))
            )


def project_of(path):
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "wiki":
        return parts[1]
    return None


def check_indexes(pages, resolver, findings):
    projects = sorted({p for p in (project_of(path) for path in pages) if p})

    root_index = "wiki/index.md"
    root_targets = set()
    if root_index in pages:
        for _, raw in scan_links(pages[root_index]):
            root_targets.update(resolver.resolve(link_target(raw), root_index))

    for project in projects:
        index = "wiki/%s/index.md" % project
        if index not in pages:
            findings.append(
                Finding(
                    "wiki/%s" % project,
                    1,
                    "IDX002",
                    "error",
                    "project folder has no index.md",
                )
            )
            continue
        if root_targets and index not in root_targets:
            findings.append(
                Finding(root_index, 1, "IDX002", "error", "project %r is not listed in the root index" % project)
            )
        elif not root_targets and root_index not in pages:
            findings.append(
                Finding("wiki/index.md", 1, "IDX002", "error", "root index is missing")
            )

        listed = set()
        for _, raw in scan_links(pages[index]):
            listed.update(resolver.resolve(link_target(raw), index))

        for path in pages:
            if path == index or project_of(path) != project:
                continue
            # Progress records are numbered, not linked. They are reached by
            # taking the highest number, so requiring a link would be busywork.
            if "/progress/" in path:
                continue
            if path not in listed:
                findings.append(
                    Finding(
                        path,
                        1,
                        "IDX001",
                        "error",
                        "not linked from %s" % index,
                    )
                )


def check_duplicates(pages, findings):
    seen = {}
    for path in pages:
        project = project_of(path)
        if project is None:
            continue
        key = (project, path.rsplit("/", 1)[-1])
        if key in seen:
            findings.append(
                Finding(
                    path,
                    1,
                    "DUP001",
                    "error",
                    "basename collides with %s inside project %r" % (seen[key], project),
                )
            )
        else:
            seen[key] = path


def check_orphans(pages, resolver, findings):
    inbound = {path: 0 for path in pages}
    for path, lines in pages.items():
        for _, raw in scan_links(lines):
            for hit in resolver.resolve(link_target(raw), path):
                if hit != path:
                    inbound[hit] = inbound.get(hit, 0) + 1
    for path in pages:
        name = path.rsplit("/", 1)[-1]
        if name in EXEMPT_NAMES or path.rsplit("/", 1)[-1] == "AGENTS.md":
            continue
        # Same reason: a session record is addressed by number, not by link.
        if "/progress/" in path:
            continue
        if inbound.get(path, 0) == 0:
            findings.append(
                Finding(path, 1, "ORPHAN001", "warning", "no inbound wikilink from any page")
            )


# --- main -------------------------------------------------------------------

BASE_DIR = "."


def main(argv=None):
    global BASE_DIR
    parser = argparse.ArgumentParser(
        description="Deterministic lint for an agent-maintained Obsidian vault."
    )
    parser.add_argument("vault", nargs="?", default=".", help="vault root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--quiet", action="store_true", help="findings only, no summary")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.vault)
    if not os.path.isdir(root):
        sys.stderr.write("lint: not a directory: %s\n" % args.vault)
        return 2
    BASE_DIR = root

    all_paths = walk_vault(root)
    resolver = Resolver(all_paths)

    pages = {}
    for path in all_paths:
        if path.startswith("raw/"):
            continue
        if path.rsplit("/", 1)[-1].startswith("."):
            continue
        with open(os.path.join(root, path), encoding="utf-8") as handle:
            pages[path] = handle.read().splitlines()

    findings = []
    check_links(pages, resolver, findings)
    check_titles(pages, findings)
    check_filenames(all_paths, findings)
    check_indexes(pages, resolver, findings)
    check_duplicates(pages, findings)
    check_orphans(pages, resolver, findings)

    for path, lines in pages.items():
        name = path.rsplit("/", 1)[-1]
        if name == "AGENTS.md" or path == "wiki/log.md":
            continue
        check_frontmatter(path, lines, findings)

    findings.sort(key=Finding.sort_key)
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors

    if args.json:
        print(
            json.dumps(
                {
                    "vault": root,
                    "files": len(all_paths),
                    "checked": len(pages),
                    "errors": errors,
                    "warnings": warnings,
                    "findings": [f.as_dict() for f in findings],
                },
                indent=2,
            )
        )
    else:
        for f in findings:
            print("%s:%d: %s: %s: %s" % (f.path, f.line, f.code, f.severity, f.message))
        if not args.quiet:
            if findings:
                print()
            print(
                "%d files, %d checked, %d error%s, %d warning%s"
                % (
                    len(all_paths),
                    len(pages),
                    errors,
                    "" if errors == 1 else "s",
                    warnings,
                    "" if warnings == 1 else "s",
                )
            )

    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(2)
