#!/usr/bin/env python3
"""
QuestionTube v0.1.0 — Reference Validator

Validates QuestionTube datasets and test fixtures.

Features:
- JSON Schema Draft 2020-12 validation
- Unique Question and Contribution IDs
- Derivation reference integrity
- Duplicate derivation detection
- Directed cycle detection
- Contribution reference integrity
- Verification-state consistency
- PASS/FAIL expectation matching
- Deterministic error classification

Exit codes:
    0: All fixture expectations matched
    1: Validation mismatch or runner error

Dependency:
    pip install "jsonschema>=4.18,<5"
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


PROTOCOL_VERSION = "0.1.0"
FIXTURE_VERSION = "0.1.0"

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    ROOT / "schemas" / "questiontube-v0.1.schema.json"
)

EXAMPLES_DIR = ROOT / "examples"

ERROR_CODES = {
    "SCHEMA_VALIDATION_ERROR",
    "DUPLICATE_QUESTION_ID",
    "UNKNOWN_QUESTION_REFERENCE",
    "DUPLICATE_DERIVATION",
    "DERIVATION_CYCLE",
    "DUPLICATE_CONTRIBUTION_ID",
    "UNKNOWN_CONTRIBUTION_QUESTION",
    "VERIFICATION_STATE_MISMATCH",
}


class ValidationFailure(Exception):
    """Represents an expected dataset validation failure."""

    def __init__(self, code: str, message: str):
        if code not in ERROR_CODES:
            raise ValueError(
                f"Unknown validation error code: {code}"
            )

        self.code = code
        self.message = message

        super().__init__(f"{code}: {message}")


class RunnerError(Exception):
    """Represents a fixture or test-runner failure."""


@dataclass
class CaseResult:
    fixture: str
    case_id: str
    expected_result: str
    actual_result: str
    expected_error: str | None
    actual_error: str | None
    matched: bool
    detail: str = ""


def load_json(path: Path) -> Any:
    """Load a JSON file with explicit error reporting."""

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError as exc:
        raise RunnerError(
            f"File not found: {path}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise RunnerError(
            f"Invalid JSON in {path}: "
            f"line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    except OSError as exc:
        raise RunnerError(
            f"Unable to read {path}: {exc}"
        ) from exc


def load_schema() -> Draft202012Validator:
    """Load and check the QuestionTube JSON Schema."""

    schema = load_json(SCHEMA_PATH)

    try:
        Draft202012Validator.check_schema(schema)

    except SchemaError as exc:
        raise RunnerError(
            f"Invalid JSON Schema: {exc.message}"
        ) from exc

    return Draft202012Validator(schema)


def validate_schema(
    dataset: Any,
    validator: Draft202012Validator,
) -> None:
    """Validate a dataset against JSON Schema."""

    errors = list(validator.iter_errors(dataset))

    if not errors:
        return

    errors.sort(
        key=lambda error: (
            "/".join(str(x) for x in error.absolute_path),
            error.message,
        )
    )

    error = errors[0]

    location = "/".join(
        str(part) for part in error.absolute_path
    )

    if not location:
        location = "<root>"

    raise ValidationFailure(
        "SCHEMA_VALIDATION_ERROR",
        f"{location}: {error.message}",
    )


def build_question_registry(
    questions: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build a registry and detect duplicate Question IDs."""

    registry: dict[str, dict[str, Any]] = {}

    for question in questions:
        question_id = question["question_id"]

        if question_id in registry:
            raise ValidationFailure(
                "DUPLICATE_QUESTION_ID",
                f"Duplicate Question ID: {question_id}",
            )

        registry[question_id] = question

    return registry


def validate_derivation_references(
    derivations: list[dict[str, Any]],
    questions: dict[str, dict[str, Any]],
) -> None:
    """Check that every derivation endpoint exists."""

    for derivation in derivations:
        parent = derivation["parent_question_id"]
        child = derivation["child_question_id"]

        if parent not in questions:
            raise ValidationFailure(
                "UNKNOWN_QUESTION_REFERENCE",
                f"Unknown parent Question: {parent}",
            )

        if child not in questions:
            raise ValidationFailure(
                "UNKNOWN_QUESTION_REFERENCE",
                f"Unknown child Question: {child}",
            )


def validate_duplicate_derivations(
    derivations: list[dict[str, Any]],
) -> None:
    """Reject repeated directed derivation edges."""

    seen: set[tuple[str, str]] = set()

    for derivation in derivations:
        edge = (
            derivation["parent_question_id"],
            derivation["child_question_id"],
        )

        if edge in seen:
            raise ValidationFailure(
                "DUPLICATE_DERIVATION",
                f"Duplicate derivation: {edge[0]} -> {edge[1]}",
            )

        seen.add(edge)


def validate_derivation_cycles(
    derivations: list[dict[str, Any]],
    questions: dict[str, dict[str, Any]],
) -> None:
    """
    Detect directed cycles with iterative depth-first search.

    States:
        0 = unvisited
        1 = visiting
        2 = completed

    A connection to a visiting node indicates a cycle.
    """

    graph: dict[str, list[str]] = defaultdict(list)

    for derivation in derivations:
        parent = derivation["parent_question_id"]
        child = derivation["child_question_id"]

        graph[parent].append(child)

    state = {question_id: 0 for question_id in questions}

    for start in questions:
        if state[start] != 0:
            continue

        state[start] = 1

        # Each stack entry stores a node and an iterator
        # over its outgoing edges.
        stack = [(start, iter(graph[start]))]

        while stack:
            node, children = stack[-1]

            try:
                child = next(children)

            except StopIteration:
                state[node] = 2
                stack.pop()
                continue

            child_state = state[child]

            if child_state == 1:
                raise ValidationFailure(
                    "DERIVATION_CYCLE",
                    f"Directed cycle detected: "
                    f"{node} -> {child}",
                )

            if child_state == 0:
                state[child] = 1
                stack.append(
                    (child, iter(graph[child]))
                )


def validate_contribution_ids(
    contributions: list[dict[str, Any]],
) -> None:
    """Reject duplicate Contribution IDs."""

    seen: set[str] = set()

    for contribution in contributions:
        contribution_id = contribution["contribution_id"]

        if contribution_id in seen:
            raise ValidationFailure(
                "DUPLICATE_CONTRIBUTION_ID",
                f"Duplicate Contribution ID: "
                f"{contribution_id}",
            )

        seen.add(contribution_id)


def validate_contribution_references(
    contributions: list[dict[str, Any]],
    questions: dict[str, dict[str, Any]],
) -> None:
    """Ensure contributions reference registered questions."""

    for contribution in contributions:
        question_id = contribution["question_id"]

        if question_id not in questions:
            raise ValidationFailure(
                "UNKNOWN_CONTRIBUTION_QUESTION",
                f"Contribution references unknown "
                f"Question: {question_id}",
            )


def validate_verification_states(
    contributions: list[dict[str, Any]],
) -> None:
    """Check verification-state metadata consistency."""

    for contribution in contributions:
        contribution_id = contribution["contribution_id"]

        status = contribution["verification_status"]

        verification = contribution.get("verification")

        if status == "unverified":
            if "verification" in contribution:
                raise ValidationFailure(
                    "VERIFICATION_STATE_MISMATCH",
                    f"{contribution_id}: unverified "
                    f"contribution contains verification metadata",
                )

        elif status in {"verified", "rejected"}:
            if not isinstance(verification, dict):
                raise ValidationFailure(
                    "VERIFICATION_STATE_MISMATCH",
                    f"{contribution_id}: {status} "
                    f"contribution requires verification metadata",
                )

            verifier_id = verification.get("verifier_id")
            evidence_ref = verification.get("evidence_ref")

            if (
                not isinstance(verifier_id, str)
                or not verifier_id.strip()
                or not isinstance(evidence_ref, str)
                or not evidence_ref.strip()
            ):
                raise ValidationFailure(
                    "VERIFICATION_STATE_MISMATCH",
                    f"{contribution_id}: incomplete "
                    f"verification metadata",
                )


def validate_dataset(
    dataset: Any,
    validator: Draft202012Validator,
) -> None:
    """
    Validate one QuestionTube dataset.

    Error precedence:
      1. Schema
      2. Duplicate Question IDs
      3. Unknown derivation references
      4. Duplicate derivations
      5. Derivation cycles
      6. Duplicate Contribution IDs
      7. Unknown Contribution references
      8. Verification-state consistency
    """

    validate_schema(dataset, validator)

    if dataset["version"] != PROTOCOL_VERSION:
        raise ValidationFailure(
            "SCHEMA_VALIDATION_ERROR",
            "Unsupported protocol version",
        )

    questions = build_question_registry(
        dataset["questions"]
    )

    derivations = dataset["derivations"]
    contributions = dataset["contributions"]

    validate_derivation_references(
        derivations,
        questions,
    )

    validate_duplicate_derivations(derivations)

    validate_derivation_cycles(
        derivations,
        questions,
    )

    validate_contribution_ids(contributions)

    validate_contribution_references(
        contributions,
        questions,
    )

    validate_verification_states(contributions)


def validate_fixture_envelope(
    fixture: Any,
    path: Path,
    expected_directory: str,
) -> list[dict[str, Any]]:
    """Check fixture structure before executing test cases."""

    if not isinstance(fixture, dict):
        raise RunnerError(
            f"{path}: fixture root must be an object"
        )

    if set(fixture) != {"fixture_version", "cases"}:
        raise RunnerError(
            f"{path}: invalid fixture envelope fields"
        )

    if fixture["fixture_version"] != FIXTURE_VERSION:
        raise RunnerError(
            f"{path}: unsupported fixture version"
        )

    cases = fixture["cases"]

    if not isinstance(cases, list) or not cases:
        raise RunnerError(
            f"{path}: cases must be a non-empty array"
        )

    seen_case_ids: set[str] = set()

    required_fields = {
        "case_id",
        "expected_result",
        "dataset",
    }

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise RunnerError(
                f"{path}: case {index} must be an object"
            )

        if not required_fields.issubset(case):
            raise RunnerError(
                f"{path}: case {index} missing required fields"
            )

        allowed_fields = required_fields | {"expected_error"}

        if not set(case).issubset(allowed_fields):
            raise RunnerError(
                f"{path}: case {index} contains unknown fields"
            )

        case_id = case["case_id"]

        if (
            not isinstance(case_id, str)
            or not case_id.strip()
        ):
            raise RunnerError(
                f"{path}: case {index} has invalid case_id"
            )

        if case_id in seen_case_ids:
            raise RunnerError(
                f"{path}: duplicate case_id: {case_id}"
            )

        seen_case_ids.add(case_id)

        expected_result = case["expected_result"]

        if expected_result not in {"PASS", "FAIL"}:
            raise RunnerError(
                f"{path}: {case_id} has invalid "
                f"expected_result"
            )

        if expected_directory == "pass":
            if expected_result != "PASS":
                raise RunnerError(
                    f"{path}: PASS directory contains "
                    f"FAIL expectation: {case_id}"
                )

        if expected_directory == "fail":
            if expected_result != "FAIL":
                raise RunnerError(
                    f"{path}: FAIL directory contains "
                    f"PASS expectation: {case_id}"
                )

        if expected_result == "FAIL":
            error_code = case.get("expected_error")

            if error_code not in ERROR_CODES:
                raise RunnerError(
                    f"{path}: {case_id} has invalid "
                    f"expected_error"
                )

        else:
            if "expected_error" in case:
                raise RunnerError(
                    f"{path}: PASS case {case_id} must not "
                    f"declare expected_error"
                )

        # A dataset may intentionally violate JSON Schema.
        # Therefore dataset validation happens per case,
        # not during fixture-envelope validation.

    return cases


def execute_case(
    case: dict[str, Any],
    fixture_name: str,
    validator: Draft202012Validator,
) -> CaseResult:
    """Execute one case and compare its expected outcome."""

    case_id = case["case_id"]

    expected_result = case["expected_result"]
    expected_error = case.get("expected_error")

    actual_result = "PASS"
    actual_error = None
    detail = ""

    try:
        validate_dataset(
            case["dataset"],
            validator,
        )

    except ValidationFailure as exc:
        actual_result = "FAIL"
        actual_error = exc.code
        detail = exc.message

    if expected_result == "PASS":
        matched = actual_result == "PASS"

    else:
        matched = (
            actual_result == "FAIL"
            and actual_error == expected_error
        )

    return CaseResult(
        fixture=fixture_name,
        case_id=case_id,
        expected_result=expected_result,
        actual_result=actual_result,
        expected_error=expected_error,
        actual_error=actual_error,
        matched=matched,
        detail=detail,
    )


def discover_fixtures() -> list[tuple[Path, str]]:
    """Discover positive and negative fixture files."""

    fixtures: list[tuple[Path, str]] = []

    for directory_name in ("pass", "fail"):
        directory = EXAMPLES_DIR / directory_name

        if not directory.is_dir():
            raise RunnerError(
                f"Missing fixture directory: {directory}"
            )

        paths = sorted(directory.glob("*.json"))

        if not paths:
            raise RunnerError(
                f"No JSON fixtures found in {directory}"
            )

        for path in paths:
            fixtures.append(
                (path, directory_name)
            )

    return fixtures


def print_case_result(result: CaseResult) -> None:
    """Print a deterministic result line."""

    marker = "MATCH" if result.matched else "MISMATCH"

    expected = result.expected_result
    actual = result.actual_result

    if result.expected_error:
        expected += f"({result.expected_error})"

    if result.actual_error:
        actual += f"({result.actual_error})"

    print(
        f"[{marker}] "
        f"{result.fixture}::{result.case_id} "
        f"expected={expected} "
        f"actual={actual}"
    )

    if not result.matched and result.detail:
        print(f"  detail: {result.detail}")


def run() -> int:
    """Run the complete QuestionTube validation suite."""

    print("=== QuestionTube v0.1.0 Validation ===")
    print()

    validator = load_schema()

    fixtures = discover_fixtures()

    results: list[CaseResult] = []

    for path, directory_name in fixtures:
        relative_path = path.relative_to(ROOT).as_posix()

        print(f"[fixture] {relative_path}")

        fixture = load_json(path)

        cases = validate_fixture_envelope(
            fixture,
            path,
            directory_name,
        )

        for case in cases:
            result = execute_case(
                case,
                relative_path,
                validator,
            )

            results.append(result)

            print_case_result(result)

        print()

    total = len(results)
    matched = sum(result.matched for result in results)
    mismatched = total - matched

    positive_cases = sum(
        result.expected_result == "PASS"
        for result in results
    )

    negative_cases = sum(
        result.expected_result == "FAIL"
        for result in results
    )

    print("=== Validation Summary ===")
    print(f"Total cases      : {total}")
    print(f"Positive cases   : {positive_cases}")
    print(f"Negative cases   : {negative_cases}")
    print(f"Matched          : {matched}")
    print(f"Mismatched       : {mismatched}")

    if total == 0:
        print("[FAIL] No test cases executed")
        return 1

    if mismatched:
        print()
        print("[FAIL] Validation expectations not satisfied")
        return 1

    print()
    print("[PASS] All validation expectations matched")

    return 0


def main() -> int:
    """CLI entry point."""

    try:
        return run()

    except RunnerError as exc:
        print(f"[RUNNER ERROR] {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        print(
            f"[UNEXPECTED ERROR] "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
