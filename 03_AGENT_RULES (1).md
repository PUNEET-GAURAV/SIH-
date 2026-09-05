# DocShield AI — Coding Agent Rules (v2)

You are the senior full-stack AI/CV engineer implementing DocShield AI. Read `01_SOLUTION_SPEC.md` (what/why) and `02_BUILD_SPEC.md` (how) before any architectural change. This file is guardrails only — it does not restate schemas defined in those two files; if you need a schema, go read it there instead of inventing one.

## NON-NEGOTIABLE RULES

1. **Never fabricate AI output.** If a real model is unavailable or unusable, return `MODEL_UNAVAILABLE` from that adapter, or use a clearly labeled mock adapter (`is_mock: true`) in mock mode. Never present random or hardcoded numbers as inference. Never phrase a mock result as if a real model produced it (bad: "EfficientNet detected manipulation" when EfficientNet did not run; good: "DEMO / MOCK FORENSIC RESULT").

2. **Never claim authenticity.** Forbidden strings anywhere in code, copy, logs, or UI: "document is genuine", "document is definitely fake", "fraud confirmed", "fake person", "criminal", "forged person". Use: "high concern", "possible manipulation", "inconsistency detected", "manual verification recommended", "identity uncertain".

3. **Preserve uncertainty.** Every module distinguishes `PASS / FAIL / UNCERTAIN / NOT_APPLICABLE / UNAVAILABLE`. Never collapse `UNCERTAIN` or `UNAVAILABLE` into `FAIL`.

4. **Quality first.** If capture quality is inadequate, explain why and request recapture. Never let a downstream failure caused by poor image quality read as tampering evidence — reduce `reliability`, don't raise `concern`.

5. **Unknown-document safety.** Insufficient classification confidence → `UNKNOWN_DOCUMENT_MODE`: generic checks only, template-specific claims disabled, mandatory manual review flagged.

6. **Deterministic checks stay deterministic.** MRZ parsing/checksums/date/format validation are pure Python with unit tests — never routed through an LLM or any learned model.

7. **Forensic evidence is never proof.** Never write `if detector_score > X: fake = True`. Every detector emits `{signal, status, confidence, applicable, explanation}`; only the fusion engine (rule-based, see build spec §1/§3) turns evidence into a concern level.

8. **Face verification ≠ authentication.** It compares live face to document photo only. It never establishes legal identity, citizenship, or document authenticity — don't let any code path or copy imply otherwise.

9. **PAD, not "liveness."** Use the term Presentation Attack Detection. Never claim universal spoof/liveness coverage — only the attack types actually tested (see solution spec §11) may be referenced as tested.

10. **Audit everything consequential.** Log session creation, document processing, evidence generation, officer decision, override, escalation, audit verification. Never log raw biometric/video payloads — hash or reference only.

## WHEN SOMETHING IS IMPOSSIBLE

Do not fake it. Instead: (1) identify the missing dependency, (2) implement the adapter interface anyway so it's swappable later, (3) return a safe `UNAVAILABLE`/`UNCERTAIN` state, (4) provide a clearly labeled mock path if needed for the demo, (5) document the limitation in the milestone delivery notes (build spec §17/§18).

Applies specifically to: real model unavailable → `MODEL_UNAVAILABLE` state, never a guessed score. Dataset unavailable → document it, don't synthesize a fake evaluation number. An API/endpoint requested by an earlier draft that conflicts with the orchestrator's stage ordering → implement it as an internal service call, not a public endpoint (see solution spec §24), and say so in delivery notes. External dependency fails at runtime → the calling module returns `UNAVAILABLE`, the pipeline continues with reduced reliability elsewhere, it never aborts the whole session silently. Feature too large for MVP → move it to Stretch/Future per the matrix in build spec §1 and say so, don't half-implement it inside the MVP path. Confidence is low anywhere → surface it, don't round it up. OCR/face-detection fails → `UNAVAILABLE` for that signal, not an inferred negative. Forensic signals conflict → surface the contradiction in the evidence report (solution spec §12), don't silently pick a winner. Tests fail → fix or explicitly document as a known limitation before the next milestone; never comment out a failing test to get green CI.

## ARCHITECTURE RULES

Backend: FastAPI, Pydantic, SQLAlchemy, PostgreSQL. Service boundaries, not microservices. Frontend: React, TypeScript, Tailwind, shadcn/ui, modular components. AI: every model behind an adapter interface (`DocumentClassifier`, `OCRProvider`, `MRZParser`, `ForensicDetector`, `FaceVerifier`, `PADDetector` — build spec §4) so implementations swap without touching business logic.

## FILE ORGANIZATION

Business logic never lives in route files. `routes/` stays thin (request/response only); logic lives in `services/`.

## API RULES

Validate all inputs. Return the stable envelope (build spec §13). Use `request_id` for correlation. Never leak stack traces to the frontend. Document endpoints via OpenAPI.

## DATABASE RULES

UUID PKs. UTC timestamps. Migrations required for every schema change. Indexes on session/document IDs. Never store raw biometric material unless a config flag explicitly enables it for the current run. Keep demo/mock data clearly separated from anything resembling production-shaped records.

## SECURITY RULES

Password hashing where credentials exist, JWT/session security appropriate to a prototype, RBAC, CORS config, file-type validation, file-size limits, path-traversal protection, safe temp-file handling, secure deletion where practical, secrets only via environment variables. Never commit API keys, passwords, certificates, private keys, or real personal document samples.

## FRONTEND RULES

The officer should understand the case within seconds. Priority: overall concern → why flagged → visual evidence → raw technical detail (expandable). Don't overwhelm the default view with ML jargon.

## EVIDENCE UI

Each card shows: Signal, Status, Confidence, Reliability, Applicability, Source, Explanation, Region. Never render a heatmap as if it were ground truth — allow opacity adjustment, show region coordinates, allow zoom, but label it as model output.

## FUSION RULES

Weight by confidence, reliability, and applicability. Reduce reliability when upstream quality is poor. Group and downweight signals that share a root cause instead of double-counting them. Never blindly average incompatible signal types.

## MOCK DATA RULES

Six deterministic scenarios (solution spec §26): `genuine, altered_dob, expired, wrong_face, poor_capture, unknown_document`. Every mock output includes `is_mock: true`; the UI shows a persistent `DEMO MODE` badge whenever anything on screen is mock-derived.

## MODEL MANAGEMENT

No silent large-model downloads at runtime. Maintain a model directory + manifest, validate presence at startup, and fail into a graceful `UNAVAILABLE` state rather than crashing or blocking. If licensing is unclear, document how the user installs the model themselves — never redistribute it.

## PERFORMANCE RULES

Lazy-load heavy models, reuse loaded instances, avoid repeated image decoding, resize before expensive processing when safe, run independent forensic modules concurrently, cache immutable template metadata in-process.

## TESTING PRIORITY

Before adding new features, confirm: MRZ tests pass, fusion tests pass, API health works, DB migrations run cleanly, the full demo workflow (all six scenarios) works end-to-end.

## NO UNNECESSARY COMPLEXITY

Do not introduce Kubernetes, Kafka, Redis, Neo4j, blockchain, or LLM agents unless a specific, measured requirement emerges during the build. FAISS is Stretch-only (identity linking), never core infrastructure.

## DELIVERY FORMAT

At the end of each milestone, report: what changed, files changed, how to run it, tests run (and their results), known limitations, next recommended milestone. Known limitations are reported honestly, including forensic-model generalization gaps and PAD's limited tested-attack coverage — these are expected, not failures to hide.

## FINAL AGENT OBJECTIVE

Build a polished, demonstrable, technically honest SIH prototype. The winning quality is not the number of AI models. It is: reliable processing + multiple independent evidence sources + clearly represented uncertainty + strong visual explanation + real human officer control + offline capability + reproducible engineering.
