
# Month 4 Syllabus — *archivist*

**Anchor Project:** `archivist`
**Invariant:** SQLite DB is the single source of truth; state persists across runs.
**Entry Rule:** One `main` entry point; one module owns all SQLite access.

---

## Day 1 — Project Skeleton & Entry Point

**DO:** Create project structure and a runnable `main` with argparse subcommands stubbed (`init`, `scan`, `archive`, `status`).
**GATE:**

* Program runs with `--help`
* Invalid command exits cleanly
  **STOP:** CLI prints help and exits.

## Day 2 — Command Dispatch Integrity

**DO:** Implement subcommand dispatch functions that print placeholder output.
**GATE:**

* Each command is reachable
* Unknown args fail safely
  **STOP:** Each command prints its name and exits.

## Day 3 — SQLite Demand Identified

**DO:** Define required persistent state in comments (files seen, hashes, status).
**GATE:**

* State cannot be represented in memory alone
* SQLite necessity is explicit
  **STOP:** No database code written.

---

## Day 4 — SQLite Module Creation

**DO:** Create a single `db.py` module that opens a SQLite file.
**GATE:**

* DB file is created
* Connection closes cleanly
  **STOP:** No tables yet.

## Day 5 — Schema Definition

**DO:** Create tables for files and actions using basic SQL.
**GATE:**

* Tables created once
* Re-running does not error
  **STOP:** Tables exist, empty.

## Day 6 — `init` Command

**DO:** Implement `init` to create DB and tables.
**GATE:**

* Running twice is safe
* Missing permissions fail cleanly
  **STOP:** DB initialized.

---

## Day 7 — File Metadata Capture

**DO:** Walk a directory with pathlib and collect path, size, mtime.
**GATE:**

* Walk completes
* Permission errors handled
  **STOP:** Metadata printed only.

## Day 8 — Insert File Records

**DO:** Insert scanned file metadata into SQLite if unseen.
**GATE:**

* Duplicate scan does not duplicate rows
* DB remains consistent on error
  **STOP:** Records inserted.

## Day 9 — Scan Idempotency

**DO:** Update scan logic to skip unchanged files.
**GATE:**

* Re-scan adds zero rows
* Changed file is detected
  **STOP:** Scan command complete.

---

## Day 10 — File Change Detection

**DO:** Add hash or mtime comparison to mark files as changed.
**GATE:**

* Change toggles eligibility
* No false positives
  **STOP:** Change state stored.

## Day 11 — Archive Eligibility Rules

**DO:** Define and store eligibility flags in DB.
**GATE:**

* Eligibility persisted
* Invalid state rejected
  **STOP:** No archiving yet.

## Day 12 — Archive Stub

**DO:** Implement `archive` command that selects eligible files only.
**GATE:**

* Selection correct
* No file operations yet
  **STOP:** Prints planned actions.

---

## Day 13 — Archive Execution

**DO:** Archive files using standard library tools.
**GATE:**

* Files archived once
* Errors do not corrupt DB
  **STOP:** Files moved/copied.

## Day 14 — Archive Idempotency

**DO:** Prevent re-archiving unchanged files.
**GATE:**

* Second run does nothing
* Changed file re-eligible
  **STOP:** Verified behavior.

## Day 15 — Failure Recording

**DO:** Record archive failures in DB.
**GATE:**

* Failure stored
* Program continues safely
  **STOP:** Failure visible.

---

## Day 16 — Status Command

**DO:** Implement `status` to show counts by state.
**GATE:**

* Counts accurate
* Empty DB handled
  **STOP:** Status prints summary.

## Day 17 — Safe Failure Paths

**DO:** Force failures (bad path, perms) and observe behavior.
**GATE:**

* Program does not crash
* State remains valid
  **STOP:** Failure cases tested.

## Day 18 — Scan + Archive Interaction

**DO:** Ensure scan updates eligibility post-archive.
**GATE:**

* Archived files not re-selected
* Changed files re-selected
  **STOP:** Interaction stable.

---

## Day 19 — DB Access Encapsulation

**DO:** Route all SQLite calls through `db.py`.
**GATE:**

* No sqlite calls elsewhere
* Program still works
  **STOP:** Encapsulation complete.

## Day 20 — Entry Point Audit

**DO:** Enforce `if __name__ == "__main__"` usage.
**GATE:**

* Imports do not execute logic
* CLI still functions
  **STOP:** Clean entry confirmed.

## Day 21 — Data Integrity Checks

**DO:** Add defensive checks before DB writes.
**GATE:**

* Invalid data rejected
* No partial writes
  **STOP:** Integrity enforced.

---

## Day 22 — Repeated Run Validation

**DO:** Run full cycle twice (`scan → archive → status`).
**GATE:**

* Second run no-ops correctly
* Counts unchanged
  **STOP:** Behavior confirmed.

## Day 23 — Controlled Change Test

**DO:** Modify a file and re-run cycle.
**GATE:**

* Change detected
* File re-archived
  **STOP:** Change handling proven.

## Day 24 — Deletion Edge Case

**DO:** Handle missing files gracefully on scan/archive.
**GATE:**

* Missing file recorded
* No crash
  **STOP:** Edge case logged.

---

## Day 25 — Output Clarity

**DO:** Normalize CLI output messages.
**GATE:**

* No ambiguous output
* Errors clearly labeled
  **STOP:** Output stable.

## Day 26 — State Inspection

**DO:** Manually inspect SQLite DB contents.
**GATE:**

* Tables consistent
* States match expectations
  **STOP:** Inspection complete.

## Day 27 — No-Off-Syllabus Audit

**DO:** Verify only allowed modules and concepts used.
**GATE:**

* No blacklisted items
* Procedural style intact
  **STOP:** Audit passed.

---

## Day 28 — Cold Start Test

**DO:** Delete DB and rerun full workflow.
**GATE:**

* init required
* System recovers cleanly
  **STOP:** Cold start validated.

## Day 29 — Failure Recovery Test

**DO:** Induce mid-archive failure and retry.
**GATE:**

* Retry succeeds
* No duplicate archives
  **STOP:** Recovery confirmed.

## Day 30 — Final Gate

**DO:** Demonstrate all commands in sequence.
**GATE:**

* Program runs
* Program fails safely
* Persistent state correct
  **STOP:** Month 4 complete.
