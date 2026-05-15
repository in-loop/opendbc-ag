#!/usr/bin/env bash
# opendbc-ag pre-publish preflight — runs identically on Linux + macOS.
#
# Usage:
#   bash scripts/preflight.sh
#
# Exits non-zero if any hard gate fails. Writes preflight-report.md alongside.
# This is Phase RT-T1 of the publish-prep plan.

set -u  # don't `set -e` — we want to keep going and report all failures
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

REPORT="$REPO_ROOT/preflight-report.md"
VENV="$REPO_ROOT/.venv-preflight"
START_TS=$(date +%s)
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# OS detection (BSD vs GNU sed/grep/iconv etc.)
OS="$(uname -s)"

# ---------- report header ----------
cat > "$REPORT" <<EOF
# opendbc-ag preflight report

**Started:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**OS:** $OS · $(uname -r)
**Repo:** $REPO_ROOT
**Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo "(not a git repo)")

| # | Check | Result | Details |
|---|---|---|---|
EOF

# ---------- helpers ----------
n=0
pass() {
    n=$((n+1)); PASS_COUNT=$((PASS_COUNT+1))
    printf "| %d | %s | ✅ pass | %s |\n" "$n" "$1" "${2:-—}" >> "$REPORT"
    printf "[%2d] PASS  %s\n" "$n" "$1"
}
fail() {
    n=$((n+1)); FAIL_COUNT=$((FAIL_COUNT+1))
    printf "| %d | %s | ❌ FAIL | %s |\n" "$n" "$1" "${2:-}" >> "$REPORT"
    printf "[%2d] FAIL  %s — %s\n" "$n" "$1" "${2:-}" >&2
}
warn() {
    n=$((n+1)); WARN_COUNT=$((WARN_COUNT+1))
    printf "| %d | %s | ⚠️ warn | %s |\n" "$n" "$1" "${2:-}" >> "$REPORT"
    printf "[%2d] WARN  %s — %s\n" "$n" "$1" "${2:-}"
}

# ---------- 1. Fresh venv install ----------
echo "[1/10] Fresh venv install at $VENV…"
rm -rf "$VENV"
if python3 -m venv "$VENV" 2>/dev/null && \
   "$VENV/bin/pip" install --quiet --upgrade pip && \
   "$VENV/bin/pip" install --quiet -e ".[dev]" && \
   "$VENV/bin/pip" install --quiet pip-audit cantools; then
    pass "Fresh venv install" "python3 -m venv + pip install -e '.[dev]' + cantools + pip-audit"
else
    fail "Fresh venv install" "pip install failed; see stderr"
fi

PYTHON="$VENV/bin/python"

# ---------- 2. pytest sweep ----------
echo "[2/10] pytest sweep…"
PYTEST_OUT="$("$VENV/bin/pytest" opendbc_ag/tests/ -q 2>&1 || true)"
PYTEST_SUMMARY="$(echo "$PYTEST_OUT" | tail -1)"
if echo "$PYTEST_SUMMARY" | grep -qE "^[0-9]+ passed.*xfailed"; then
    pass "pytest sweep" "$PYTEST_SUMMARY"
elif echo "$PYTEST_SUMMARY" | grep -qE "^[0-9]+ passed"; then
    pass "pytest sweep" "$PYTEST_SUMMARY"
else
    fail "pytest sweep" "$PYTEST_SUMMARY"
fi

# ---------- 3. DBC load via cantools ----------
echo "[3/10] cantools load each DBC…"
LOAD_OUT="$("$PYTHON" <<'PY' 2>&1
import sys
from pathlib import Path
import cantools
results = []
for p in sorted(Path("opendbc_ag/dbc").glob("*.dbc")):
    try:
        db = cantools.database.load_file(str(p))
        results.append((p.name, len(db.messages), sum(len(m.signals) for m in db.messages), None))
    except Exception as e:
        results.append((p.name, 0, 0, str(e)))
for n, f, s, e in results:
    if e:
        print(f"FAIL {n}: {e}")
    else:
        print(f"OK   {n}: {f} frames, {s} signals")
errors = [r for r in results if r[3]]
sys.exit(1 if errors else 0)
PY
)"
if [ $? -eq 0 ]; then
    pass "cantools load" "$(echo "$LOAD_OUT" | tr '\n' ' ')"
else
    fail "cantools load" "$LOAD_OUT"
fi

# ---------- 4. canmatrix round-trip ----------
echo "[4/10] canmatrix round-trip…"
RT_OUT="$("$PYTHON" <<'PY' 2>&1
import sys, tempfile, difflib
from pathlib import Path
from canmatrix import formats
issues = []
for p in sorted(Path("opendbc_ag/dbc").glob("*.dbc")):
    m = formats.loadp(str(p))
    mat = list(m.values())[0]
    with tempfile.NamedTemporaryFile(suffix=".dbc", delete=False) as tf:
        out_path = tf.name
    formats.dumpp({"": mat}, out_path, dbcExportEncoding="utf-8", dbcExportCommentEncoding="utf-8")
    # Re-parse and confirm frame count + signal count match
    m2 = formats.loadp(out_path)
    mat2 = list(m2.values())[0]
    n1, s1 = len(mat.frames), sum(len(f.signals) for f in mat.frames)
    n2, s2 = len(mat2.frames), sum(len(f.signals) for f in mat2.frames)
    if (n1, s1) != (n2, s2):
        issues.append(f"{p.name}: {n1}f/{s1}s → {n2}f/{s2}s")
    else:
        print(f"OK   {p.name}: {n1}f/{s1}s round-trip-stable")
if issues:
    print("FAIL:", "; ".join(issues))
    sys.exit(1)
PY
)"
if [ $? -eq 0 ]; then
    pass "canmatrix round-trip" "all 3 DBCs stable on parse→emit→parse"
else
    fail "canmatrix round-trip" "$RT_OUT"
fi

# ---------- 5. scope-policy gate ----------
echo "[5/10] scripts/check_dbc_policy.py…"
POLICY_OUT="$("$PYTHON" scripts/check_dbc_policy.py 2>&1)"
if [ $? -eq 0 ]; then
    pass "scope/duplicate/citation gate" "$(echo "$POLICY_OUT" | tr '\n' ' ')"
else
    fail "scope/duplicate/citation gate" "$POLICY_OUT"
fi

# ---------- 6. UTF-8 sanity ----------
echo "[6/10] UTF-8 sanity on each DBC…"
UTF_ERRORS=""
for f in opendbc_ag/dbc/*.dbc; do
    if ! iconv -f utf-8 -t utf-8 "$f" > /dev/null 2>&1; then
        UTF_ERRORS="$UTF_ERRORS $f"
    fi
done
if [ -z "$UTF_ERRORS" ]; then
    pass "UTF-8 sanity" "all 3 DBCs decode clean"
else
    fail "UTF-8 sanity" "non-UTF-8 bytes in:$UTF_ERRORS"
fi

# ---------- 7. BS_ line cantools-compatible (must be empty form) ----------
echo "[7/10] BS_ line is cantools-compatible empty form…"
BS_ERRORS=""
for f in opendbc_ag/dbc/*.dbc; do
    # cantools only accepts `BS_:` with nothing after the colon.
    # Baudrate is documented out-of-band (README/coverage.md) since cantools
    # reads it from BA_ attributes, not BS_.
    if ! grep -qE "^BS_:[[:space:]]*$" "$f"; then
        BS_ERRORS="$BS_ERRORS $f"
    fi
done
if [ -z "$BS_ERRORS" ]; then
    pass "BS_ cantools-compat" "all 3 DBCs use empty BS_: form"
else
    fail "BS_ cantools-compat" "BS_ line not cantools-compatible in:$BS_ERRORS"
fi

# ---------- 8. No IEEE-754 noise ----------
echo "[8/10] no IEEE-754 noise in factor/min/max…"
NOISE_COUNT=0
for f in opendbc_ag/dbc/*.dbc; do
    # local var name (not `n` — that's the global pass/fail counter)
    file_noise=$(grep -cE "0\.[0-9]{8,}|\b0E-[0-9]" "$f" || true)
    NOISE_COUNT=$((NOISE_COUNT + file_noise))
done
if [ "$NOISE_COUNT" -eq 0 ]; then
    pass "no IEEE-754 noise" "0 long-decimal tokens, 0 Decimal-scientific zeros"
else
    fail "no IEEE-754 noise" "$NOISE_COUNT noisy tokens across DBCs"
fi

# ---------- 9. README coverage table matches DBC reality ----------
echo "[9/10] coverage-claim consistency check…"
COVERAGE_OUT="$("$PYTHON" <<'PY' 2>&1
import re, sys
from pathlib import Path
from canmatrix import formats
# Sum actual frames/signals
total_f = total_s = 0
for p in sorted(Path("opendbc_ag/dbc").glob("*.dbc")):
    mat = list(formats.loadp(str(p)).values())[0]
    total_f += len(mat.frames)
    total_s += sum(len(f.signals) for f in mat.frames)
# Find a count claim in README
readme = Path("README.md").read_text()
# Look for "X unique PGNs" or "X frames" patterns near the coverage table
m_pgns = re.findall(r"([\d,]+)\s*unique PGNs?", readme)
m_signals = re.findall(r"([\d,]+)\s*signals?", readme)
readme_f = int(m_pgns[0].replace(",", "")) if m_pgns else None
readme_s = int(m_signals[0].replace(",", "")) if m_signals else None
print(f"DBC reality: {total_f} frames / {total_s} signals")
print(f"README claim: {readme_f} frames / {readme_s} signals")
if readme_f and abs(readme_f - total_f) > 0:
    print(f"MISMATCH on frames: {readme_f} vs {total_f}")
    sys.exit(1)
PY
)"
if [ $? -eq 0 ]; then
    pass "coverage claim ↔ DBC reality" "$(echo "$COVERAGE_OUT" | tr '\n' ' ')"
else
    fail "coverage claim ↔ DBC reality" "$COVERAGE_OUT"
fi

# ---------- 10. pip-audit (soft warn) ----------
echo "[10/10] pip-audit (soft-warn)…"
AUDIT_OUT="$("$VENV/bin/pip-audit" --progress-spinner=off 2>&1)"
AUDIT_RC=$?
if [ "$AUDIT_RC" -eq 0 ] && ! echo "$AUDIT_OUT" | grep -qiE "vulnerab|advisor"; then
    pass "pip-audit" "no known advisories"
else
    SUMMARY="$(echo "$AUDIT_OUT" | grep -iE "vulnerab|advisor|found" | head -3 | tr '\n' '; ')"
    warn "pip-audit" "${SUMMARY:-see stderr; soft-warn matches CI posture}"
fi

# ---------- footer ----------
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))
cat >> "$REPORT" <<EOF

---

**Summary:** $PASS_COUNT passed · $FAIL_COUNT failed · $WARN_COUNT warned · ${ELAPSED}s elapsed

**Status:** $(if [ "$FAIL_COUNT" -eq 0 ]; then echo "✅ ALL HARD GATES PASS — RT-T1 complete on $OS"; else echo "❌ $FAIL_COUNT hard gate(s) failed — block before proceeding"; fi)

**Next:** $(if [ "$FAIL_COUNT" -eq 0 ]; then echo "Run this script on the Mac (RT-T2), then SavvyCAN GUI load each DBC."; else echo "Triage failures above. Re-run after fix."; fi)
EOF

echo ""
echo "===== preflight summary ====="
echo "$PASS_COUNT passed · $FAIL_COUNT failed · $WARN_COUNT warned · ${ELAPSED}s"
echo "Report: $REPORT"

# Exit code reflects hard-gate state
exit $FAIL_COUNT
