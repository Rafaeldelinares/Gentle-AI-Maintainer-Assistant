#!/usr/bin/env python3
"""
validate.py — Test runner for Gentle AI Maintainer Assistant schemas & fixtures

Validates all contracts in schemas/ against their JSON Schema definitions
and verifies that invalid edge cases fail closed.

Usage:
  .venv/bin/python schemas/validate.py
"""

import json
import sys
from pathlib import Path
import jsonschema
from jsonschema.validators import validator_for

SCHEMAS_DIR = Path(__file__).parent
FIXTURES_DIR = SCHEMAS_DIR / "fixtures"

# Map schemas to their fixtures
SCHEMA_FIXTURE_MAP = [
    ("issue-record.schema.json", ["issue-record.fixture.json"]),
    ("triage-inference.schema.json", [
        "triage-inference-deterministic.fixture.json",
        "triage-inference-llm.fixture.json",
        "triage-inference-p0-candidate.fixture.json",
    ]),
    ("maintainer-decision.schema.json", [
        "maintainer-decision-accept.fixture.json",
        "maintainer-decision-override.fixture.json",
    ]),
    ("triage-batch-report.schema.json", ["triage-batch-report.fixture.json"]),
]

def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" VALIDATING SCHEMAS & FIXTURES (Draft 2020-12)")
    print("════════════════════════════════════════════════════════════════════\n")

    # Load all schemas first to build a Registry for $ref resolution
    schemas = {}
    for schema_file, _ in SCHEMA_FIXTURE_MAP:
        sp = SCHEMAS_DIR / schema_file
        if not sp.exists():
            print(f"❌ Schema missing: {schema_file}", file=sys.stderr)
            return 1
        schemas[schema_file] = load_json(sp)

    # Use jsonschema Resource and Registry
    try:
        from referencing import Registry, Resource
        resources = []
        for s_file, s_data in schemas.items():
            res = Resource.from_contents(s_data)
            resources.append((s_data.get("$id", s_file), res))
            resources.append((s_file, res))
        registry = Registry().with_resources(resources)
    except ImportError:
        registry = None

    passed_count = 0
    total_count = 0

    # 1. POSITIVE TESTS (Fixtures must pass validation)
    for schema_file, fixtures in SCHEMA_FIXTURE_MAP:
        schema_data = schemas[schema_file]
        validator_cls = validator_for(schema_data)
        validator_cls.check_schema(schema_data)
        print(f"✔ Schema syntax OK: {schema_file}")

        if registry:
            validator = validator_cls(schema_data, registry=registry)
        else:
            validator = validator_cls(schema_data)

        for fix_file in fixtures:
            total_count += 1
            fix_path = FIXTURES_DIR / fix_file
            if not fix_path.exists():
                print(f"❌ Fixture missing: {fix_file}", file=sys.stderr)
                return 1
            fix_data = load_json(fix_path)
            try:
                validator.validate(fix_data)
                print(f"    ✔ Valid fixture: {fix_file}")
                passed_count += 1
            except jsonschema.ValidationError as e:
                print(f"    ❌ Error validating {fix_file}: {e.message}", file=sys.stderr)
                return 1

    # 2. NEGATIVE TESTS (Intentional violations must fail closed)
    print("\n════════════════════════════════════════════════════════════════════")
    print(" NEGATIVE TESTS (Verifying fail-closed behavior)")
    print("════════════════════════════════════════════════════════════════════\n")

    # Neg 1: deterministic_rule missing rule_name
    total_count += 1
    bad_inference = load_json(FIXTURES_DIR / "triage-inference-deterministic.fixture.json")
    bad_inference["rule_name"] = None
    try:
        validator = validator_for(schemas["triage-inference.schema.json"])(schemas["triage-inference.schema.json"])
        validator.validate(bad_inference)
        print("❌ Negative test failed: deterministic_rule without rule_name was accepted", file=sys.stderr)
        return 1
    except jsonschema.ValidationError:
        print("✔ Neg test 1 OK: deterministic_rule without rule_name is rejected as expected")
        passed_count += 1

    # Neg 2: maintainer_decision missing actor
    total_count += 1
    bad_decision = load_json(FIXTURES_DIR / "maintainer-decision-accept.fixture.json")
    del bad_decision["actor"]
    try:
        validator = validator_for(schemas["maintainer-decision.schema.json"])(schemas["maintainer-decision.schema.json"])
        validator.validate(bad_decision)
        print("❌ Negative test failed: maintainer decision without human actor was accepted", file=sys.stderr)
        return 1
    except jsonschema.ValidationError:
        print("✔ Neg test 2 OK: decision without human actor is rejected as expected")
        passed_count += 1

    # Neg 3: invalid band "P4"
    total_count += 1
    bad_band = load_json(FIXTURES_DIR / "triage-inference-deterministic.fixture.json")
    bad_band["band"] = "P4"
    try:
        validator = validator_for(schemas["triage-inference.schema.json"])(schemas["triage-inference.schema.json"])
        validator.validate(bad_band)
        print("❌ Negative test failed: invalid band P4 was accepted", file=sys.stderr)
        return 1
    except jsonschema.ValidationError:
        print("✔ Neg test 3 OK: invented band P4 is rejected as expected")
        passed_count += 1

    # Neg 4: candidate P0 label emitted with a non-candidate rule must fail closed
    total_count += 1
    bad_candidate = load_json(FIXTURES_DIR / "triage-inference-p0-candidate.fixture.json")
    bad_candidate["rule_name"] = "rule:feature_request"
    try:
        validator = validator_for(schemas["triage-inference.schema.json"])(schemas["triage-inference.schema.json"])
        validator.validate(bad_candidate)
        print("❌ Negative test failed: candidate P0 label with wrong rule was accepted", file=sys.stderr)
        return 1
    except jsonschema.ValidationError:
        print("✔ Neg test 4 OK: candidate P0 label requires rule:candidato_p0_requiere_revision_humana")
        passed_count += 1

    # Neg 5: silent data loss must never be emitted as a final P0 by a deterministic rule
    total_count += 1
    bad_final_p0 = load_json(FIXTURES_DIR / "triage-inference-p0-candidate.fixture.json")
    bad_final_p0["band"] = "P0"
    try:
        validator = validator_for(schemas["triage-inference.schema.json"])(schemas["triage-inference.schema.json"])
        validator.validate(bad_final_p0)
        print("❌ Negative test failed: final P0 with candidate rule was accepted", file=sys.stderr)
        return 1
    except jsonschema.ValidationError:
        print("✔ Neg test 5 OK: deterministic candidate rule cannot emit a final P0 band")
        passed_count += 1

    print("\n────────────────────────────────────────────────────────────────────")
    print(f" FINAL RESULT: {passed_count}/{total_count} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0

if __name__ == "__main__":
    sys.exit(main())
