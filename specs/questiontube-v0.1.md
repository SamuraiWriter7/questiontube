# QuestionTube Protocol Specification v0.1

**Protocol:** QuestionTube  
**Version:** 0.1.0  
**Codename:** Git for Questions  
**Status:** Draft — Implementation and Validation Pending

---

## 1. Purpose

QuestionTube is a minimal, Git-inspired protocol for recording and validating the structural evolution of questions.

It provides three fundamental record types:

1. Question
2. Derivation
3. Contribution

QuestionTube treats questions as identifiable nodes in a directed graph.

Derivations represent directed edges between registered questions.

Contributions represent records associated with registered questions.

The protocol does not evaluate the semantic correctness, usefulness, or economic value of a question.

Its primary purpose is to establish a reproducible structural validation model.

### Core principle

> Question evolution must remain traceable without requiring centralized control over the direction of inquiry.

---

## 2. Normative Language

The terms MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are used as normative requirements.

- **MUST:** Mandatory for conformance.
- **MUST NOT:** Prohibited.
- **SHOULD:** Recommended unless a documented reason exists.
- **SHOULD NOT:** Discouraged unless a documented reason exists.
- **MAY:** Optional.

A conforming implementation MUST satisfy all mandatory requirements in this specification.

---

## 3. Scope

### 3.1 Included in v0.1

QuestionTube v0.1 defines:

- Question identification.
- Question registration within a validation dataset.
- Directed question derivation.
- Reference integrity.
- Duplicate identifier detection.
- Directed cycle detection.
- Contribution identification.
- Contribution-to-question references.
- Contribution verification-status recording.
- JSON Schema validation.
- Positive and negative validation fixtures.
- Automated validation expectations.

### 3.2 Excluded from v0.1

QuestionTube v0.1 does not define:

- Git-style merge operations.
- Conflict resolution.
- Cross-repository synchronization.
- Distributed consensus.
- Semantic equivalence between questions.
- Question quality scoring.
- Identity authentication.
- Cryptographic signatures.
- Verification evidence authentication.
- Economic contribution valuation.
- Royalty calculation or redistribution.
- Autonomous AI execution.

Implementations MAY provide these capabilities externally.

However, external functionality MUST NOT alter the meaning of QuestionTube v0.1 validation results.

---

## 4. Data Model

QuestionTube v0.1 defines a validation dataset containing three collections.

```text
QuestionTube Dataset
    |
    +-- questions[]
    |
    +-- derivations[]
    |
    +-- contributions[]
```

The dataset is the unit of structural validation.

### 4.1 Dataset Structure

A dataset MUST be represented as a JSON object.

Required top-level fields:

| Field | Type | Requirement |
|---|---|---|
| `protocol` | string | MUST equal `questiontube` |
| `version` | string | MUST equal `0.1.0` |
| `questions` | array | REQUIRED |
| `derivations` | array | REQUIRED |
| `contributions` | array | REQUIRED |

The arrays MAY be empty.

However, every reference in a derivation or contribution MUST resolve to a question within the same dataset.

### 4.2 Example Dataset

```json
{
  "protocol": "questiontube",
  "version": "0.1.0",
  "questions": [
    {
      "type": "question",
      "question_id": "Q001",
      "content": "How can questions evolve?",
      "creator_id": "human-001"
    },
    {
      "type": "question",
      "question_id": "Q002",
      "content": "How can question derivations be validated?",
      "creator_id": "human-002"
    }
  ],
  "derivations": [
    {
      "type": "derivation",
      "parent_question_id": "Q001",
      "child_question_id": "Q002",
      "relationship": "derived_from"
    }
  ],
  "contributions": [
    {
      "type": "contribution",
      "contribution_id": "C001",
      "question_id": "Q002",
      "contributor_id": "human-002",
      "verification_status": "unverified"
    }
  ]
}
```

This dataset contains:

- Two registered questions.
- One directed derivation.
- One contribution.

The dataset is valid if it satisfies the JSON Schema and all applicable structural invariants.

---

## 5. Question Record

A Question represents an identifiable unit of inquiry.

### 5.1 Required Fields

| Field | Type | Requirement |
|---|---|---|
| `type` | string | MUST equal `question` |
| `question_id` | string | REQUIRED, non-empty |
| `content` | string | REQUIRED, non-empty |
| `creator_id` | string | REQUIRED, non-empty |

### 5.2 Identifier Requirements

A Question ID MUST be unique within the dataset.

QuestionTube v0.1 does not require global uniqueness across repositories.

A conforming validator MUST reject duplicate Question IDs.

A Question ID MUST NOT be interpreted as proof of creator identity.

### 5.3 Example

```json
{
  "type": "question",
  "question_id": "Q001",
  "content": "How can questions evolve through collaboration?",
  "creator_id": "human-001"
}
```

---

## 6. Derivation Record

A Derivation represents a directed relationship between two registered questions.

The direction is:

```text
Parent Question
      |
      v
Child Question
```

### 6.1 Required Fields

| Field | Type | Requirement |
|---|---|---|
| `type` | string | MUST equal `derivation` |
| `parent_question_id` | string | REQUIRED |
| `child_question_id` | string | REQUIRED |
| `relationship` | string | MUST equal `derived_from` |

### 6.2 Reference Integrity

For every derivation:

- The parent question MUST exist.
- The child question MUST exist.
- Parent and child MUST NOT have identical IDs.

Unknown references MUST be rejected.

### 6.3 Directed Acyclic Graph

The set of derivations MUST form a directed acyclic graph (DAG).

A validator MUST detect:

1. Direct self-reference.
2. Cycles involving two questions.
3. Cycles involving three or more questions.

#### Valid

```text
Q001 ---> Q002 ---> Q004
  |
  +----> Q003
```

#### Invalid: Self-Reference

```text
Q001 ---> Q001
```

#### Invalid: Indirect Cycle

```text
Q001 ---> Q002
 ^          |
 |          v
 +--------- Q003
```

### 6.4 Multiple Parents

A question MAY have multiple parent questions.

Example:

```text
Q001 -----+
          |
          v
         Q003
          ^
          |
Q002 -----+
```

This is a valid graph if no cycle exists.

Multiple incoming derivations do not automatically constitute a Git-style merge operation.

Merge semantics are outside the scope of v0.1.

### 6.5 Duplicate Derivations

The ordered pair:

```text
(parent_question_id, child_question_id)
```

MUST be unique within the dataset.

Duplicate derivation edges MUST be rejected.

This prevents redundant relationship records without requiring derivation identifiers.

---

## 7. Contribution Record

A Contribution represents an identifiable contribution associated with an existing question.

### 7.1 Required Fields

| Field | Type | Requirement |
|---|---|---|
| `type` | string | MUST equal `contribution` |
| `contribution_id` | string | REQUIRED |
| `question_id` | string | REQUIRED |
| `contributor_id` | string | REQUIRED |
| `verification_status` | string | REQUIRED |

### 7.2 Contribution Identifier

Every Contribution ID MUST be unique within the dataset.

Duplicate Contribution IDs MUST be rejected.

### 7.3 Question Reference

Every Contribution MUST reference a registered question.

A Contribution referencing an unknown question MUST be rejected.

### 7.4 Verification Status

Allowed verification states:

| Status | Meaning |
|---|---|
| `unverified` | Verification has not been recorded as completed |
| `verified` | Verification has been recorded as completed |
| `rejected` | The contribution has been recorded as rejected |

No other status values are permitted in v0.1.

### 7.5 Verification Metadata

A Contribution MAY contain:

```json
{
  "verification": {
    "verifier_id": "human-003",
    "evidence_ref": "evidence-001"
  }
}
```

When `verification_status` equals `verified` or `rejected`, the `verification` object MUST be present.

For these two states, `verification` MUST include:

- `verifier_id`
- `evidence_ref`

Both fields MUST contain non-empty strings.

When `verification_status` equals `unverified`, the `verification` object MUST NOT be present.

This rule defines recorded metadata consistency.

It does not establish the authenticity or independence of the verifier.

### 7.6 Valid Unverified Contribution

```json
{
  "type": "contribution",
  "contribution_id": "C001",
  "question_id": "Q002",
  "contributor_id": "human-002",
  "verification_status": "unverified"
}
```

### 7.7 Valid Verified Contribution

```json
{
  "type": "contribution",
  "contribution_id": "C002",
  "question_id": "Q002",
  "contributor_id": "human-002",
  "verification_status": "verified",
  "verification": {
    "verifier_id": "human-003",
    "evidence_ref": "evidence-002"
  }
}
```

### 7.8 Invalid Verified Contribution

```json
{
  "type": "contribution",
  "contribution_id": "C003",
  "question_id": "Q002",
  "contributor_id": "human-002",
  "verification_status": "verified"
}
```

This record is invalid because the required verification metadata is missing.

### 7.9 Verification Limitations

QuestionTube v0.1 records verification claims.

It does not independently authenticate verification evidence.

The presence of:

```text
verification_status = verified
```

MUST NOT be interpreted as independently confirmed verification.

The protocol does not require a verifier to be different from the contributor in v0.1.

Independent verification policies MAY be enforced by external systems.

---

## 8. Structural Invariants

The following invariants are mandatory.

### QT-001 — Unique Question IDs

Each Question ID MUST appear at most once within a dataset.

Violation:

```text
Q001
Q001
```

Expected result:

```text
FAIL: DUPLICATE_QUESTION_ID
```

### QT-002 — Derivation Reference Integrity

Every parent and child question referenced by a Derivation MUST exist in the dataset.

Violation:

```text
Registered: Q001
Derivation: Q001 -> Q002
```

Q002 is not registered.

Expected result:

```text
FAIL: UNKNOWN_QUESTION_REFERENCE
```

### QT-003 — Acyclic Derivation Graph

The directed derivation graph MUST contain no cycles.

Violation:

```text
Q001 -> Q002
Q002 -> Q003
Q003 -> Q001
```

Expected result:

```text
FAIL: DERIVATION_CYCLE
```

A self-loop MUST also be rejected.

### QT-004 — Schema Conformance

Every validation dataset and its records MUST satisfy the JSON Schema.

Malformed structures, missing required fields, unsupported values, and prohibited additional fields MUST be rejected.

Expected result:

```text
FAIL: SCHEMA_VALIDATION_ERROR
```

### QT-005 — Contribution Reference Integrity

Every Contribution MUST reference an existing Question.

Contribution IDs MUST also be unique.

Possible results:

```text
FAIL: UNKNOWN_CONTRIBUTION_QUESTION
FAIL: DUPLICATE_CONTRIBUTION_ID
```

### QT-006 — Verification State Consistency

Contribution verification metadata MUST match the declared verification status.

Requirements:

- `unverified` MUST NOT contain verification metadata.
- `verified` MUST contain valid verification metadata.
- `rejected` MUST contain valid verification metadata.

Expected result:

```text
FAIL: VERIFICATION_STATE_MISMATCH
```

### QT-007 — Fixture Expectation Consistency

Validation fixtures MUST declare their expected result.

A positive fixture MUST pass.

A negative fixture MUST fail with its declared error code.

Unexpected success, unexpected failure, or mismatched error codes MUST cause the test runner to fail.

---

## 9. Validation Fixture Format

The v0.1 repository uses JSON validation fixtures.

To preserve the minimal file structure, each fixture file MAY contain multiple test cases.

### 9.1 Fixture Envelope

A fixture envelope MUST contain:

| Field | Type | Requirement |
|---|---|---|
| `fixture_version` | string | MUST equal `0.1.0` |
| `cases` | array | REQUIRED, non-empty |

Each case MUST contain:

| Field | Type | Requirement |
|---|---|---|
| `case_id` | string | REQUIRED |
| `expected_result` | string | `PASS` or `FAIL` |
| `dataset` | object | REQUIRED |

A case with `expected_result` equal to `FAIL` MUST also include:

```json
"expected_error": "ERROR_CODE"
```

A case with `expected_result` equal to `PASS` MUST NOT include `expected_error`.

Case IDs MUST be unique within a fixture file.

### 9.2 Positive Fixture Example

```json
{
  "fixture_version": "0.1.0",
  "cases": [
    {
      "case_id": "valid-derivation",
      "expected_result": "PASS",
      "dataset": {
        "protocol": "questiontube",
        "version": "0.1.0",
        "questions": [
          {
            "type": "question",
            "question_id": "Q001",
            "content": "What is question evolution?",
            "creator_id": "human-001"
          },
          {
            "type": "question",
            "question_id": "Q002",
            "content": "How can derivations be tracked?",
            "creator_id": "human-002"
          }
        ],
        "derivations": [
          {
            "type": "derivation",
            "parent_question_id": "Q001",
            "child_question_id": "Q002",
            "relationship": "derived_from"
          }
        ],
        "contributions": []
      }
    }
  ]
}
```

### 9.3 Negative Fixture Example

```json
{
  "fixture_version": "0.1.0",
  "cases": [
    {
      "case_id": "three-node-cycle",
      "expected_result": "FAIL",
      "expected_error": "DERIVATION_CYCLE",
      "dataset": {
        "protocol": "questiontube",
        "version": "0.1.0",
        "questions": [
          {
            "type": "question",
            "question_id": "Q001",
            "content": "Question one",
            "creator_id": "human-001"
          },
          {
            "type": "question",
            "question_id": "Q002",
            "content": "Question two",
            "creator_id": "human-002"
          },
          {
            "type": "question",
            "question_id": "Q003",
            "content": "Question three",
            "creator_id": "human-003"
          }
        ],
        "derivations": [
          {
            "type": "derivation",
            "parent_question_id": "Q001",
            "child_question_id": "Q002",
            "relationship": "derived_from"
          },
          {
            "type": "derivation",
            "parent_question_id": "Q002",
            "child_question_id": "Q003",
            "relationship": "derived_from"
          },
          {
            "type": "derivation",
            "parent_question_id": "Q003",
            "child_question_id": "Q001",
            "relationship": "derived_from"
          }
        ],
        "contributions": []
      }
    }
  ]
}
```

### 9.4 Fixture Requirements

Fixture files under:

```text
examples/pass/
```

MUST contain only cases expecting `PASS`.

Fixture files under:

```text
examples/fail/
```

MUST contain only cases expecting `FAIL`.

The validator MUST report a mismatch if a case produces an unexpected outcome.

Invalid schema test cases MAY contain intentionally malformed dataset objects.

Such malformed objects MUST NOT prevent other test cases from being executed.

Malformed fixture envelopes themselves are test-runner errors, not valid negative test results.

---

## 10. Validation Algorithm

A conforming validator MUST perform the following operations for each case.

### Step 1 — Load Fixture

Parse the fixture envelope.

Validate its structure and case expectations.

### Step 2 — Validate Dataset Schema

Validate the dataset against the QuestionTube JSON Schema.

Schema errors MUST be reported before graph-level validation.

### Step 3 — Build Question Registry

Construct a registry mapping Question IDs to Question records.

Reject duplicate Question IDs.

### Step 4 — Validate Derivation References

For every Derivation:

- Check parent existence.
- Check child existence.
- Reject duplicate derivation edges.

### Step 5 — Detect Cycles

Build a directed adjacency representation.

The validator MUST detect cycles of arbitrary finite length.

Depth-first search with visitation states or an equivalent correct algorithm MAY be used.

Cycle detection MUST NOT be limited to direct self-reference.

### Step 6 — Validate Contributions

For every Contribution:

- Check Contribution ID uniqueness.
- Check referenced Question existence.
- Check verification-state consistency.

### Step 7 — Compare Expectations

Compare the actual validation result with the fixture's declared expected result.

A negative test passes only when the intended error is detected.

### Step 8 — Produce Summary

Report at least:

- Total cases.
- Matched expectations.
- Mismatched expectations.
- Per-case expected and actual results.

The validator MUST exit with a non-zero status when any test expectation is not satisfied.

---

## 11. Error Classification

QuestionTube v0.1 defines the following validation error codes.

| Error Code | Meaning |
|---|---|
| `SCHEMA_VALIDATION_ERROR` | Dataset does not conform to JSON Schema |
| `DUPLICATE_QUESTION_ID` | Repeated Question ID |
| `UNKNOWN_QUESTION_REFERENCE` | Derivation references an unknown Question |
| `DUPLICATE_DERIVATION` | Repeated directed derivation edge |
| `DERIVATION_CYCLE` | Directed cycle detected |
| `DUPLICATE_CONTRIBUTION_ID` | Repeated Contribution ID |
| `UNKNOWN_CONTRIBUTION_QUESTION` | Contribution references an unknown Question |
| `VERIFICATION_STATE_MISMATCH` | Verification metadata inconsistent with status |

### 11.1 Error Precedence

Validation MUST use the following precedence:

1. Schema validation.
2. Duplicate Question IDs.
3. Unknown derivation references.
4. Duplicate derivations.
5. Derivation cycles.
6. Duplicate Contribution IDs.
7. Unknown Contribution question references.
8. Verification-state consistency.

If multiple violations exist, the validator MUST report the highest-precedence applicable error as the primary result.

Additional diagnostic information MAY be reported.

### 11.2 Schema and Semantic Validation

JSON Schema is responsible for structural validation, including:

- Required fields.
- Data types.
- Allowed enum values.
- Basic field constraints.
- Verification metadata presence rules.

The Python validator is responsible for dataset-level relationships, including:

- Identifier uniqueness.
- Reference integrity.
- Duplicate derivation edges.
- Directed cycle detection.

For consistent error classification, verification-state consistency rules MUST also be explicitly checked by the validator.

If a verification-state mismatch also violates JSON Schema, the primary result MUST be `SCHEMA_VALIDATION_ERROR` under the precedence rules.

A negative fixture expecting `VERIFICATION_STATE_MISMATCH` MUST therefore target a violation that is not already rejected by the applicable schema.

---

## 12. JSON Schema Requirements

The file:

```text
schemas/questiontube-v0.1.schema.json
```

MUST define the dataset structure.

The schema MUST use JSON Schema Draft 2020-12.

It MUST define the three record types:

- Question
- Derivation
- Contribution

It MUST reject unknown properties unless explicitly permitted by this specification.

The schema MUST enforce:

- Required fields.
- String non-emptiness.
- Permitted record types.
- Permitted relationship values.
- Permitted verification states.
- Conditional verification metadata requirements.

Dataset-level graph consistency MUST be enforced by the Python validator.

---

## 13. Security and Trust Boundaries

QuestionTube v0.1 validates structural relationships.

It does not authenticate the identity of participants.

The following distinctions MUST be preserved:

| Recorded Property | Not Guaranteed |
|---|---|
| Creator ID | Authentic creator identity |
| Contributor ID | Authentic contributor identity |
| Verification status | Independent verification |
| Evidence reference | Evidence authenticity |
| Valid derivation | Semantic validity |
| Valid contribution | Economic or intellectual value |

Implementations MUST NOT describe structural validity as proof of trustworthiness.

Systems requiring authentication, authorization, or evidence verification SHOULD implement separate trust mechanisms.

---

## 14. Interoperability

QuestionTube v0.1 uses JSON records and stable identifiers within a dataset.

External systems MAY reference:

- Question IDs.
- Contribution IDs.
- Derivation relationships.

QuestionTube does not define an external API, network transport, identity federation, or settlement interface in v0.1.

Potential integrations include:

- Question participation protocols.
- Provenance systems.
- AI collaboration systems.
- Contribution assessment frameworks.
- Value redistribution systems.

No dependency on these external systems is required for v0.1 conformance.

---

## 15. Versioning

This specification defines protocol version:

```text
0.1.0
```

Dataset version values MUST match the supported protocol version.

The reference validator MUST reject unsupported versions through schema validation.

Changes to required fields, validation semantics, or error classification require an explicit specification update.

---

## 16. Future Extension Boundary

### v0.2 Candidate: Question Merge

Future versions MAY introduce:

- Explicit merge records.
- Multi-source derivation consolidation.
- Merge provenance.
- Conflict representation.
- Merge validation rules.

These capabilities MUST NOT be assumed by v0.1 implementations.

QuestionTube development SHOULD follow observed requirements rather than speculative feature expansion.

---

## 17. Conformance

A QuestionTube v0.1 dataset is conformant when:

1. It satisfies the JSON Schema.
2. All Question IDs are unique.
3. All derivation references resolve.
4. No duplicate derivation edges exist.
5. The derivation graph is acyclic.
6. All Contribution IDs are unique.
7. All Contribution question references resolve.
8. All verification metadata is structurally consistent.

A QuestionTube v0.1 validator is conformant when it correctly enforces these rules and reports validation failures according to the defined error classification.

The reference implementation is intended to demonstrate these properties through reproducible test fixtures.

Conformance does not imply security certification, identity verification, or semantic correctness.

---

## 18. Final Principle

QuestionTube does not prescribe which questions should be asked.

It does not assign authority over inquiry.

It does not determine the value of a question.

It defines a minimal structure for preserving and validating relationships between questions.

> Questions may evolve freely, but their recorded structural relationships must remain verifiable.

**QuestionTube v0.1 — Git for Questions**

*Trace the question. Validate the derivation. Preserve the contribution.*
