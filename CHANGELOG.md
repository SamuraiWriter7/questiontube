# Changelog

All notable changes to QuestionTube are documented in this file.

QuestionTube is a minimal, Git-inspired protocol for recording and validating the structural evolution of questions.

This project follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as a versioning guideline.

---

## [Unreleased]

### Planned

- Explore explicit question merge semantics in v0.2.
- Define merge provenance and structural integrity requirements based on observed needs.

These items are proposals and are not part of v0.1.0.

---

## [0.1.0] - 2026-11-10

### Added

#### Core Protocol

- Introduced QuestionTube as a minimal "Git for Questions" protocol.
- Defined three fundamental record types:
  - Question
  - Derivation
  - Contribution
- Established a dataset-based validation model.
- Defined protocol version identification and record requirements.

#### Question Management

- Added unique Question ID validation within each dataset.
- Defined question content and creator identification fields.
- Added detection of duplicate Question IDs.

#### Derivation Graph

- Introduced directed derivation relationships between registered questions.
- Added parent and child Question reference validation.
- Added duplicate derivation detection.
- Added directed cycle detection, including:
  - Self-referencing derivations.
  - Two-node cycles.
  - Multi-node cycles.
- Supported branching derivations and multiple-parent relationships without introducing merge semantics.

#### Contribution Records

- Added unique Contribution ID validation.
- Added Contribution-to-Question reference integrity checks.
- Defined three verification states:
  - `unverified`
  - `verified`
  - `rejected`
- Added verification metadata requirements for verified and rejected contributions.
- Distinguished recorded verification status from independently authenticated verification evidence.

#### JSON Schema

- Added JSON Schema Draft 2020-12 definitions for:
  - QuestionTube datasets.
  - Question records.
  - Derivation records.
  - Contribution records.
  - Verification metadata.
- Added validation for required fields, data types, allowed values, and conditional verification metadata.
- Prohibited undefined record properties.

#### Reference Validator

- Added `scripts/validate_examples.py`.
- Implemented dataset-level structural validation.
- Added deterministic error classification and precedence.
- Implemented iterative depth-first search for directed cycle detection.
- Added positive and negative fixture expectation matching.
- Added non-zero process exit status for validation mismatches and runner errors.

#### Validation Fixtures

- Added 9 positive validation cases covering:
  - Simple derivation.
  - Branching derivation.
  - Multi-step derivation.
  - Multiple-parent derivation.
  - Unverified contribution.
  - Verified contribution.
  - Rejected contribution.
  - Multiple contributions.
  - Contribution on a derived question.

- Added 15 negative validation cases covering:
  - Self-referencing derivations.
  - Two-node, three-node, and four-node cycles.
  - Unknown parent and child Question references.
  - Duplicate Question IDs.
  - Duplicate derivation edges.
  - Duplicate Contribution IDs.
  - Unknown Contribution question references.
  - Missing verification metadata.
  - Prohibited verification metadata.
  - Unsupported verification status.
  - Missing required Question fields.

#### GitHub Actions

- Added `.github/workflows/validate.yml`.
- Configured automated validation on:
  - Push.
  - Pull request.
  - Manual workflow dispatch.
- Added Python 3.11 setup.
- Added JSON Schema validation dependencies.
- Added Python syntax checks.
- Added fixture coverage checks.
- Confirmed successful GitHub Actions execution.

### Security and Trust Boundaries

- Clarified that structural validity does not prove semantic correctness.
- Clarified that creator and contributor identifiers do not authenticate real-world identities.
- Clarified that verification metadata does not establish evidence authenticity.
- Excluded economic valuation, settlement, and royalty redistribution from v0.1.

### Scope Limitations

QuestionTube v0.1.0 does not include:

- Git-style merge operations.
- Conflict resolution.
- Cross-repository synchronization.
- Distributed consensus.
- Identity authentication.
- Cryptographic signatures.
- Independent evidence verification.
- Question quality scoring.
- Autonomous AI execution.
- Royalty calculation or redistribution.

These exclusions preserve the minimal scope of the initial protocol.

---

## Versioning Policy

QuestionTube uses the following versioning approach:

- **PATCH:** Documentation corrections and compatible bug fixes.
- **MINOR:** Backward-compatible protocol extensions.
- **MAJOR:** Changes that break existing protocol compatibility.

During the initial `0.x` development phase, compatibility is not guaranteed across minor versions.

Schema changes, validation rule changes, and error classification changes must be documented explicitly.

---

## Project Principle

> Questions may evolve freely, but their recorded structural relationships must remain verifiable.

**QuestionTube — Git for Questions**

*Trace the question. Validate the derivation. Preserve the contribution.*
