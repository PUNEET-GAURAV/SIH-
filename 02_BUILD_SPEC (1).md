# DocShield AI — Build Specification (v2)

This is the engineering implementation contract. `01_SOLUTION_SPEC.md` defines *what* and *why*; this file defines *how*. Do not restate schemas already defined there — reference them.

## 1. MVP / Stretch / Future Matrix (single source of truth)

| Feature | Tier | Reason |
|---|---|---|
| Session/document CRUD, basic auth+RBAC | MVP | required for any workbench |
| Quality gate (blur/glare/resolution/perspective/corners) | MVP | classical CV, no training needed, prevents false suspicion |
| Perspective correction | MVP | required by everything downstream |
| Document classification (2 known templates + UNKNOWN) | MVP | scoped small, keeps template validation demoable |
| OCR (PaddleOCR) + field normalization | MVP | core evidence source |
| MRZ parser + checksums (pure Python, unit tested) | MVP | deterministic, high-confidence, cheap to build |
| MRZ↔VIZ consistency | MVP | strongest, most defensible signal in the whole system |
| Template/structural validation (1–2 templates) | MVP | scoped small |
| Copy-move detection (SIFT/ORB) | MVP | classical, reliable, easy to demo |
| Localized manipulation CNN (EfficientNet-B0) | MVP, with disclosed generalization limits | genuinely novel but must be trained on MIDV-2020 + synthetic edits with document-level split |
| Geometric anomaly (from template residuals) | MVP | free — derived from Stage 4 output |
| Face detect/quality/ArcFace similarity (InsightFace) | MVP | pretrained, offline-capable, well-supported |
| PAD, tested against 3 attack types only | MVP, honest scope | anything more is not testable in the timeframe |
| Rule-based evidence fusion engine | MVP | this is the actual product novelty |
| Explainable workbench UI (7 tabs) | MVP | judged heavily on this |
| Officer decision actions | MVP | required for the human-in-the-loop story |
| Hash-chained audit log + verify endpoint | MVP | cheap, high credibility payoff |
| Mock/demo mode, 6 scenarios | MVP | required for a reliable live demo |
| Docker Compose deployment | MVP | required for judged reproducibility |
| Barcode/QR decode | Stretch | low effort, not present on all doc types |
| JPEG/DCT compression evidence | Stretch | unreliable after recompression, easy to overclaim |
| Additional document templates | Stretch | each template needs its own reference metadata |
| ONNX/TensorRT optimization | Stretch | performance polish, not correctness |
| FAISS identity linking / duplicate detection | Stretch | needs its own retention/consent story |
| Noise residual / font-glyph / splice analysis | Future | research-grade, not reliably demoable |
| NFC / ePassport PKI | Future | separate crypto verification path |
| UV/IR/hologram multispectral | Future | needs special hardware |
| Morph/deepfake detection | Future | separate research problem |
| Government watchlist integration | Future | no legal access in a prototype |
| Cross-checkpoint network / federated sync | Future | out of scope entirely |

## 2. Repository Structure

```
docshield-ai/
├── frontend/
├── backend/
│   ├── routes/        # thin — request/response only, no business logic
│   ├── services/       # orchestration + business logic
│   ├── models/         # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── repositories/    # DB access
│   └── utils/
├── ai/
│   ├── quality/
│   ├── document_classifier/
│   ├── ocr/
│   ├── mrz/
│   ├── template/
│   ├── forensics/
│   ├── face/
│   ├── fusion/
│   └── common/           # shared adapter interfaces (see §4)
├── data/{templates,synthetic,demo_watchlist}/
├── models/                # local model weights, gitignored, with a manifest
├── tests/
├── scripts/
├── docker/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 3. Backend Module Contracts

Each module returns the corresponding schema from `01_SOLUTION_SPEC.md` §§4–13. Restated here only where the build needs extra operational detail:

- **quality**: pure OpenCV/scikit-image, no model dependency. Must run in <200ms on a 12MP image on CPU (measure, don't assume).
- **document_classifier**: for MVP, a small CNN or even a rule/heuristic classifier over 2 known classes is acceptable — do not over-invest here relative to forensics/fusion.
- **ocr**: wraps PaddleOCR; must expose a stable internal interface (`OCRProvider`) independent of the specific engine.
- **mrz**: zero ML. Pure functions, one function per check, one unit test per function.
- **template**: homography-based alignment against 1–2 stored reference templates; versioned (`template_id@version`).
- **forensics**: each detector is a separate class implementing `ForensicDetector`; orchestrator calls all applicable ones concurrently (`asyncio.gather` / thread pool — CPU-bound work goes to a process pool, not asyncio alone).
- **face**: wraps InsightFace (RetinaFace detector + ArcFace embedding). PAD is a separate adapter (`PADDetector`) so it can be swapped independently of the embedding model.
- **fusion**: pure Python, no ML, fully unit-testable rule engine. This is the module with the highest test coverage requirement in the project.

## 4. Model Abstraction (Adapter Interfaces)

Business logic never imports a concrete model library directly — only these interfaces:

```
DocumentClassifier.classify(image) -> ClassificationResult
OCRProvider.extract(image) -> OCRResult
MRZParser.parse(mrz_text) -> MRZResult          # pure Python, no adapter needed but kept consistent
ForensicDetector.analyze(image, context) -> list[ForensicSignal]
FaceVerifier.compare(live, doc_photo) -> FaceResult
PADDetector.assess(live_frames) -> PADResult
```

Each has: a **mock implementation** (deterministic, `is_mock=True`), a **real implementation** (actual model), and later, optionally, an **ONNX implementation**. Swapping implementations must never require touching `services/` or `routes/`.

## 5. Orchestrator

One workflow (`services/screening_orchestrator.py`):

```
create session → capture → quality gate (exit early on RECAPTURE_REQUIRED)
→ preprocess → classify
→ [OCR, MRZ, Barcode] concurrently
→ deterministic validation
→ [template, forensics] concurrently
→ face branch (independent, if live capture present)
→ fusion
→ persist report
→ (officer decision, later) → audit
```

Use FastAPI `BackgroundTasks` or a simple async task runner for the long-running pipeline; a synchronous single-process call is acceptable for MVP as long as the UI shows progressive per-stage status (poll `GET /screening/{id}` or SSE).

## 6. Error Handling

Every module returns one of: `success | uncertain | unsupported | model_unavailable | invalid_input`. Exceptions are caught at the module boundary and converted to `model_unavailable` — they never silently become a suspicious/negative evidence value. Example: OCR raising an exception → `ocr.status = UNAVAILABLE`, not `document.status = FAIL`.

## 7. Configuration

All thresholds in `config/*.yaml`, not in code:

```yaml
quality: { min_resolution: ..., max_blur: ..., max_glare: ... }
classification: { min_confidence: ... }
face: { match_threshold: ... }
fusion:
  weights: { mrz_viz: ..., manipulation: ..., template: ..., face: ... }
```

Every value is labeled a **prototype default**, not a scientifically derived threshold, and is easy to tune from one file.

## 8. Database

PostgreSQL + Alembic migrations. Entities and relationships as in `01_SOLUTION_SPEC.md` §23. UUID PKs, UTC timestamps, indexes on `session_id`/`document_id`, JSONB for the evidence payload (schema in §13 of the solution spec), raw biometric video never persisted unless a config flag explicitly enables it for the current demo.

## 9. Audit

Append-only service producing `{event_id, session_id, actor_id, timestamp, event_type, payload_hash, previous_hash, entry_hash}`. A dedicated `GET /audit/{session_id}/verify` endpoint recomputes the chain and reports the first broken link, if any. Never log raw video/biometric payloads — log a hash/reference only.

## 10. Frontend

Pages: Dashboard, New Screening, Screening Workbench, Case History, Audit View, Settings. Workbench layout and tab set: see solution spec §25. Keep components modular (`DocumentViewer`, `EvidenceTabs/*`, `AssessmentPanel`, `AuditTimeline`).

## 11. Mock Mode

`MOCK_MODE=true` env flag. Every mock adapter output includes `is_mock: true` and the frontend renders a persistent `DEMO MODE` badge whenever any output on screen originated from a mock adapter. A mock output is never phrased as if a real model ran (see agent rules §1).

## 12. Testing

- Unit: MRZ check digits, date validation, field normalization, MRZ/VIZ matching, template geometry, hash chain, every fusion rule.
- Integration: full pipeline happy path; poor-quality capture; unknown document; OCR failure; model-unavailable; face-uncertain; each of the 6 demo scenarios end-to-end.
- Frontend: loading/error/empty states, evidence rendering, officer decision flow, audit rendering.

## 13. API Contract

Envelope:
```json
{ "success": true, "data": {}, "error": null, "request_id": "..." }
```
Errors:
```json
{ "success": false, "data": null, "error": {"code": "OCR_UNAVAILABLE", "message": "...", "retryable": false}, "request_id": "..." }
```
Public endpoint list: solution spec §24. All inputs validated via Pydantic; stack traces never reach the frontend; every response carries a `request_id` for correlation with logs/audit.

## 14. Performance

Benchmark on stated hardware (document it — e.g., "Ryzen 5 / 16GB, CPU-only inference"). Measure and report per-module latency, end-to-end latency, memory, and model load time — never invent numbers before they're measured. Lazy-load heavy models, reuse loaded model instances across requests, resize images before expensive processing where safe, run independent forensic modules concurrently, cache immutable template metadata in-process (no Redis needed at this scale).

## 15. Deployment

`docker compose up` brings up frontend, backend, postgres. Model weights are mounted separately (documented licensing/size), not baked into the image or silently downloaded at runtime. Provide `.env.example`, `/health` endpoint, startup validation (DB reachable, required model files present or explicitly in `MODEL_UNAVAILABLE`/mock state), migrations run on startup, seed script for demo data.

## 16. Observability

Every session gets a correlation ID (`request_id`/`session_id`). Log: pipeline stage, execution time, model version, status, error, evidence generated. Never log document images or biometric payloads — reference by ID/hash only.

## 17. Development Order (Milestones)

1. Frontend shell + backend + DB + session creation
2. Upload/capture + quality gate + perspective correction
3. OCR + MRZ parser + deterministic validation
4. Template engine + MRZ/VIZ consistency
5. Forensics (copy-move first, then localized-manipulation CNN)
6. Face verification + PAD
7. Fusion + evidence report
8. Audit + officer decisions
9. Mock mode (6 scenarios) + polish + tests + Docker

(Full recommended coding-agent build order, with rationale, is in the master response §10 — this is the milestone-level summary for tracking.)

## 18. Definition of Done

A feature is complete only if: it works locally end-to-end; it has API input validation; it has explicit error handling (no exception → suspicious-result conversion); its output is persisted where appropriate; the UI displays it with visible uncertainty where applicable; evidence/explanation is shown, not just a status; tests exist and pass; no claim in the UI or docs is unsupported by what actually ran.

## 19. Anti-Buzzword Rule

Do not add Kubernetes, Kafka, Redis, Neo4j, blockchain, federated learning, an LLM agent, RAG, or quantum ML unless a specific, measured requirement emerges during the build. None currently exists.

## 20. Priority Order When Choices Conflict

correctness > safety/uncertainty handling > reproducibility > offline functionality > explainability > simplicity > performance > visual polish.
