# OBSERVABILITY.md — Canonical Direct URLs for External Reviewers

> **Observability Registry**
> Every reviewable artifact lives in the repository root, because the external reviewer reads raw GitHub URLs and cannot navigate directories.
> All URLs below are raw and verified reachable.

---

## 1. Governance, Status & Contract Artifacts

* **PROMISES.md (Promise Contract — read this first):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/PROMISES.md

* **STATUS.md (Phase Status, Commit Hashes, What Rafael Must Decide):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/STATUS.md

* **DECISIONS.md (Design Decisions, Alternatives, Consequences):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/DECISIONS.md

* **AUDIT.md (Read-Only Adversarial Audit of H1–H10 and P0–P3):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/AUDIT.md

* **OBSERVABILITY.md (This Registry):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/OBSERVABILITY.md

* **EVALUATION.md (Self-Contained Audit & Verification Guide):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/EVALUATION.md

---

## 2. Code & Test Artifacts

* **db/rules.py (Deterministic Rule Engine):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/db/rules.py

* **test_rules.py (Rule Test Suite — 125/125 passing, concrete cases):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/test_rules.py

* **tools/metrics.py (Recomputes Every Published Figure):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/tools/metrics.py

* **tools/readonly_check.py (Verifies the Read-Only Invariant):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/tools/readonly_check.py

* **tools/privacy_check.py (Verifies No Personal Data in the Snapshot):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/tools/privacy_check.py

* **tools/run_reports.py (Regenerates All Module Reports):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/tools/run_reports.py

* **tools/determinism_check.py (Fail if a Report Changes Across Processes):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/tools/determinism_check.py

---

## 2b. Mechanical Modules (read-only, no labels needed)

* **MODULES.md (Method, Embedded Code and Limits):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/MODULES.md

* **report-completeness.md (Module A Output — missing required form fields):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/report-completeness.md

* **report-duplicates.md (Module B Output — probable duplicate pairs):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/report-duplicates.md

* **report-cross-links.md (Module C Output — cross-repo references):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/report-cross-links.md

* **report-obsolete.md (Module D Output — references to deleted source paths):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/report-obsolete.md

* **modules/completeness.py:**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/modules/completeness.py

* **modules/duplicates.py:**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/modules/duplicates.py

* **modules/cross_repo.py:**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/modules/cross_repo.py

* **modules/obsolete.py:**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/modules/obsolete.py

* **schemas/validate.py (Contract Test Runner — 12/12 passing):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/validate.py

* **schemas/triage-inference.schema.json (Recommendation Contract):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/triage-inference.schema.json

* **gold-p0-p1.md (Human-Review Gold Set, `veredicto_humano: pendiente`):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/gold-p0-p1.md

* **issues.json (Sanitized Snapshot of 1,228 Open Issues, no personal data):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/issues.json

---

## 3. Specifications, Governance & Models

* **README.md (Architecture Overview & Evaluation Guide):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/README.md

* **AGENTS.md (Development Protocol & Governance Principles):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/AGENTS.md

* **LICENSE (MIT License):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/LICENSE

* **docs/triage-model.md (Triage Model, 13 Dimensions, Rules H1–H10):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/triage-model.md

* **docs/decision-model.md (Maintainer Decision Authority & Escrow Model):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/decision-model.md

* **docs/walkthrough-examples.md (Pipeline Walkthrough, synthetic issue numbers):**
  https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/walkthrough-examples.md

---

## 4. Reproduction Commands

```bash
python3 tools/metrics.py          # every published figure
python3 db/rules.py               # classification + calibration sample
python3 test_rules.py             # rule suite (125/125)
.venv/bin/python schemas/validate.py   # contracts (12/12), needs jsonschema
python3 tools/readonly_check.py   # read-only invariant
python3 tools/privacy_check.py    # no personal data in the snapshot
python3 tools/run_reports.py     # regenerate all three module reports
python3 tools/determinism_check.py  # fail if any report changes across processes
```
