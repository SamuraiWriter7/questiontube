# QuestionTube

**Git for Questions — A Minimal Protocol for Verifiable Question Evolution**

QuestionTube is an open, Git-inspired protocol for recording and validating how questions originate, derive, and evolve through contributions.

Instead of treating questions as isolated text, QuestionTube represents them as a verifiable graph of relationships.

The goal is simple:

> Make the evolution of questions traceable, structurally consistent, and independently reproducible.

**Current version:** v0.1.0  
**Status:** Initial specification — validation pending

---

## 1. Why QuestionTube?

Traditional version control systems track changes to files and source code.

However, questions also evolve.

A question may:

- Originate from a person or system.
- Generate another question.
- Branch into multiple lines of inquiry.
- Receive contributions from different participants.
- Become the foundation for further investigation.

These relationships are often lost when questions are stored only as documents, conversations, or prompts.

QuestionTube introduces a minimal structure for recording question evolution without requiring a centralized question-management platform.

### Core idea

```text
Question Q001
    |
    | derives
    v
Question Q002
    |
    | derives
    v
Question Q003
```

Each question has an identifiable origin.

Each derivation links existing questions.

Each contribution references a registered question.

The resulting graph can be validated automatically.

---

## 2. Design Principles

QuestionTube v0.1 follows five principles.

### 2.1 Questions First

The question is the primary unit of the protocol.

AI systems, applications, and participants may assist in processing questions, but they do not replace the question as the central structural object.

### 2.2 Minimal Structure

QuestionTube defines only the fields and relationships necessary for structural validation.

It does not attempt to implement a complete collaboration platform.

### 2.3 Verifiable Relationships

A derivation must reference existing questions.

Invalid references, duplicate question identifiers, and cyclic derivations must be rejected.

### 2.4 Separation of Claims and Evidence

A contribution's verification status is a recorded claim.

A status such as `verified` does not, by itself, establish that independent verification occurred.

Evidence verification and trust assessment remain separate concerns.

### 2.5 Incremental Evolution

New capabilities are introduced only when they address a demonstrated requirement.

Version 0.1 focuses on registration, derivation, contribution recording, and structural validation.

Merge and conflict resolution are reserved for future versions.

---

## 3. Core Architecture

QuestionTube consists of three primary record types.

```text
+---------------------------+
|         Question          |
|                           |
| ID                        |
| Content                   |
| Creator                   |
+-------------+-------------+
              |
              v
+---------------------------+
|        Derivation         |
|                           |
| Parent Question           |
| Child Question            |
| Relationship              |
+-------------+-------------+
              |
              v
+---------------------------+
|       Contribution        |
|                           |
| Target Question           |
| Contributor               |
| Verification Status       |
+-------------+-------------+
              |
              v
+---------------------------+
|     Graph Validation      |
|                           |
| Schema Validation         |
| Reference Integrity       |
| Cycle Detection           |
| Contribution Integrity    |
+---------------------------+
```

The diagram illustrates the logical validation flow.

Question, Derivation, and Contribution are separate record types. Contributions reference questions and do not themselves create derivation edges.

---

## 4. Question

A Question represents an identifiable unit of inquiry.

### Minimum requirements

Every Question must contain:

- A unique question identifier.
- The content of the question.
- An identifiable creator or originating entity.

### Example

```json
{
  "type": "question",
  "question_id": "Q001",
  "content": "How can questions evolve through collaboration?",
  "creator_id": "human-001"
}
```

Question identifiers must be unique within the validation dataset.

QuestionTube does not require globally unique identifiers across independent repositories in v0.1.

---

## 5. Derivation

A Derivation represents a directed relationship between two existing questions.

### Example

```json
{
  "type": "derivation",
  "parent_question_id": "Q001",
  "child_question_id": "Q002",
  "relationship": "derived_from"
}
```

This relationship means that Q002 is derived from Q001.

### Structural requirements

A valid derivation must satisfy the following conditions:

1. The parent question exists.
2. The child question exists.
3. The parent and child are different questions.
4. The relationship does not introduce a directed cycle.

### Valid graph

```text
Q001
 |
 +----> Q002
 |
 +----> Q003
          |
          v
         Q004
```

### Invalid graph

```text
Q001 ---> Q002
 ^         |
 |         v
 +-------- Q003
```

The second graph contains a directed cycle and must be rejected.

QuestionTube v0.1 permits multiple questions to derive from the same parent.

It also permits a question to have multiple incoming derivation relationships, provided that the resulting graph remains acyclic.

Such relationships do not imply Git-style merge semantics.

---

## 6. Contribution

A Contribution records an identifiable contribution associated with an existing question.

### Example

```json
{
  "type": "contribution",
  "contribution_id": "C001",
  "question_id": "Q002",
  "contributor_id": "human-002",
  "verification_status": "unverified"
}
```

### Minimum requirements

A contribution must include:

- A unique contribution identifier.
- A reference to an existing question.
- An identifiable contributor.
- A valid verification status.

### Verification states

| Status | Meaning |
|---|---|
| `unverified` | Verification has not been recorded as completed. |
| `verified` | Verification has been recorded as completed. |
| `rejected` | The contribution has been recorded as rejected. |

These states describe recorded status only.

They do not establish the authenticity of verification evidence, the identity of the verifier, or the validity of the contribution's content.

QuestionTube v0.1 does not perform independent evidence authentication.

---

## 7. Structural Invariants

A conforming v0.1 validation dataset must satisfy the following invariants.

| ID | Invariant |
|---|---|
| QT-001 | Every Question ID is unique. |
| QT-002 | Every Derivation references an existing parent and child Question. |
| QT-003 | The derivation graph contains no directed cycles, including self-loops. |
| QT-004 | Every record conforms to its applicable JSON Schema definition. |
| QT-005 | Every Contribution references an existing Question. |
| QT-006 | Contribution verification fields are structurally consistent with the defined verification states. |
| QT-007 | Validation fixtures produce their declared expected results. |

For QT-006, structural consistency means that required fields and permitted status values satisfy the schema and specification.

It does not imply that verification evidence has been independently authenticated.

For QT-007, an expected failure must be caused by the intended invalid condition, rather than by an unrelated parsing error or validator failure.

These invariants define the minimum validity requirements for QuestionTube v0.1.

---

## 8. Repository Structure

```text
questiontube/
├── README.md
├── CHANGELOG.md
├── specs/
│   └── questiontube-v0.1.md
├── schemas/
│   └── questiontube-v0.1.schema.json
├── examples/
│   ├── pass/
│   │   ├── derived-question.json
│   │   └── verified-contribution.json
│   └── fail/
│       └── cyclic-derivation.json
├── scripts/
│   └── validate_examples.py
└── .github/
    └── workflows/
        └── validate.yml
```

The initial repository contains ten files.

The examples are validation fixtures rather than a persistent question database.

Additional test cases may be represented within existing fixture files without changing the core protocol.

---

## 9. Validation

QuestionTube includes a Python validator for checking structural integrity.

### Validation responsibilities

The validator must:

1. Load the validation fixtures.
2. Validate records against the JSON Schema.
3. Build a question registry.
4. Detect duplicate question identifiers.
5. Verify derivation references.
6. Detect direct and indirect derivation cycles.
7. Verify contribution references and status consistency.
8. Compare actual validation results with declared expectations.

The validation dataset is treated as a complete graph for the purpose of reference checks.

References to questions outside that dataset are invalid in v0.1.

### Run locally

```bash
python scripts/validate_examples.py
```

The validator is intended to run with Python 3.11 or later.

The exact dependency requirements and fixture format are defined by the accompanying implementation.

### Expected behavior

Fixtures under `examples/pass/` must validate successfully.

Fixtures under `examples/fail/` must fail for their declared reason.

An expected invalid fixture is counted as a successful test only when the validator identifies the intended violation.

Unexpected success, unexpected failure, or incorrect failure classification must cause the validation run to fail.

### GitHub Actions

The repository includes:

```text
.github/workflows/validate.yml
```

The workflow runs the validator automatically as configured by the workflow definition.

Passing GitHub Actions establishes that the implemented test suite completed successfully.

It does not constitute a formal security audit or independent certification of the protocol.

---

## 10. Scope of v0.1

### Included

- Question identification and registration.
- Directed question derivation relationships.
- Reference integrity checking.
- Cycle detection.
- Contribution recording.
- Contribution verification-status recording.
- JSON Schema validation.
- Positive and negative validation fixtures.
- Automated validation through GitHub Actions.

### Not included

- Git-style merge operations.
- Merge conflict resolution.
- Question-content semantic equivalence.
- AI-generated question quality assessment.
- Identity authentication.
- Cryptographic signatures.
- Independent verification of contribution evidence.
- Economic contribution valuation.
- Royalty calculation or redistribution.
- Distributed consensus.
- Cross-repository synchronization.
- Question execution or autonomous AI orchestration.

These exclusions are intentional.

QuestionTube v0.1 defines structural integrity, not a complete trust, collaboration, or economic system.

---

## 11. Relationship to Other Protocols

QuestionTube is designed to remain independent of higher-level participation, provenance, and value-distribution systems.

### QuestionTube

Manages question identities, derivation relationships, and contribution references.

### Toikatsu

May manage participation activities, consent, contribution recognition, and handoff procedures.

### Person-Provenance

May provide additional information about the origins, intentions, and identities associated with participation.

### Royalty OS

May use externally verified contribution records for attribution, settlement, and redistribution.

These systems are conceptually complementary.

No normative interoperability contract with them is defined in QuestionTube v0.1.

Future integrations may reference QuestionTube identifiers without modifying its core graph semantics.

---

## 12. Roadmap

### v0.1 — Minimal Question Graph

- Question registration.
- Derivation recording.
- Contribution recording.
- Structural integrity validation.
- Reproducible validation fixtures.

### v0.2 — Question Merge

Potential scope:

- Explicit merge relationships.
- Multi-source question integration.
- Merge provenance.
- Minimal merge integrity rules.

The exact requirements of v0.2 will be determined after v0.1 validation and review.

Future capabilities are proposals, not commitments.

---

## 13. Conformance and Limitations

QuestionTube v0.1 is a structural specification.

A dataset is structurally valid only when it satisfies the applicable schema and graph invariants.

Structural validity does not guarantee:

- The truth of a question's premises.
- The quality or usefulness of a question.
- The authenticity of a creator or contributor.
- The legitimacy of a recorded verification.
- The fairness of contribution recognition.
- The security of an external system.

Implementations must not treat graph validation as proof of these properties.

The reference implementation and its tests define an initial conformance baseline, subject to future review and correction.

---

## 14. Project Philosophy

Questions are not merely inputs to AI systems.

They can be persistent structural objects that develop through human and machine collaboration.

QuestionTube does not attempt to determine which questions are valuable.

Instead, it provides a minimal foundation for observing how questions relate, derive, and accumulate recorded contributions.

The governing principle is:

> Preserve the structure of question evolution without controlling the direction of inquiry.

**QuestionTube — Git for Questions.**

*Trace the question. Validate the derivation. Preserve the contribution.*
