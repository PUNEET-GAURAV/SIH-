# DocShield AI — Solution Specification (v2)

## 1. Project
- SIH Problem: SIH26188 — AI-Based Fake Identity & Document Screening System
- Ministry: Ministry of Home Affairs | Agency: SSB, Police-II Division
- Category: Software
- **Positioning**: An officer decision-support and investigation-assistance system. It is NOT an authentication system and does NOT issue automated accept/reject decisions.

## 2. Core Principle

DocShield AI never declares a document genuine or fake, and never declares a person fraudulent. It independently evaluates four dimensions and fuses them into an explainable report:

1. **Document consistency** — internal standards conformity (MRZ, checksums, VIZ/MRZ agreement)
2. **Structural conformity** — layout/geometry vs. known template (when a template is known)
3. **Manipulation evidence** — signals of digital tampering
4. **Identity consistency** — live face vs. document photo similarity

One-line pitch:
> DocShield AI does not replace an officer by declaring a document fake; it turns a document, a face, and multiple independent signals into a structured evidence report that tells the officer what looks inconsistent, where it looks inconsistent, and why it deserves closer investigation.

## 3. Pipeline

```
RGB Capture
   │
   ▼
[1] Capture Quality Gate  ──► RECAPTURE_REQUIRED (exit)
   │ (ACCEPT / DEGRADED)
   ▼
[2] Preprocessing (perspective correction, normalization)
   │
   ▼
[3] Document Classification (type/template/UNKNOWN_DOCUMENT_MODE)
   │
   ├──────────────► [4a] OCR + Field Extraction
   ├──────────────► [4b] MRZ Parse + Deterministic Validation
   └──────────────► [4c] Barcode/QR Decode (if present, else NOT_APPLICABLE)
   │
   ▼ (fan-out, run concurrently — each independent, each degrades gracefully)
   ├──────────────► [5a] Template / Structural Validation (disabled if UNKNOWN)
   ├──────────────► [5b] Forensics: Copy-Move (SIFT/ORB)
   └──────────────► [5c] Forensics: Localized Manipulation (CNN, if model available)
   │
   ▼ (independent branch, gated on a live face being captured)
[6] Face: Detection → Quality → PAD → ArcFace Similarity
   │
   ▼
[7] Evidence Fusion (rule-based, confidence/reliability/applicability-aware)
   │
   ▼
[8] Explainable Screening Report → Officer Decision → Hash-Chained Audit Log
```

Stages 4a–4c and 5a–5c run concurrently once preprocessing is done; stage 6 runs independently and does not block document-side evidence. Fusion waits on whichever branches are applicable and marks the rest `NOT_APPLICABLE` or `UNAVAILABLE` rather than blocking.

## 4. Assessment Dimensions and Outputs

| Dimension | Checks | Output states |
|---|---|---|
| Document Consistency | MRZ structure/checksums, date logic, field formats, MRZ↔VIZ | `PASS / REVIEW / FAIL` |
| Structural Conformity | template geometry, field zones, aspect ratio (known templates only) | `CONFORMING / DEVIATION / UNKNOWN` |
| Manipulation Evidence | copy-move, localized manipulation CNN, geometric anomaly | `LOW / MEDIUM / HIGH` |
| Identity Consistency | face quality, PAD, ArcFace cosine similarity | `MATCH / UNCERTAIN / MISMATCH` |

Every individual signal additionally carries `status`, `confidence`, `reliability`, `applicable`, `source`, `explanation`, `region`, `model_version` (see §9).

## 5. Stage 1 — Capture Quality Gate

Checks: document boundary detection, four-corner visibility, blur, motion blur, glare, shadow, exposure, resolution, perspective distortion, occlusion, multiple/incomplete documents.

States: `ACCEPT`, `PROCESS_WITH_DEGRADED_CONFIDENCE`, `RECAPTURE_REQUIRED`.

**Rule**: poor quality must never be converted into manipulation evidence. If a downstream module cannot run reliably because of quality, it reports `reliability` low or `status: UNCERTAIN` — never `SUSPICIOUS`.

## 6. Stage 2 — Document Classification

Classes for MVP: passport (TD3), one national/driving-licence-style ID (TD1), `UNKNOWN`. Additional classes are Stretch.

Method: lightweight visual classifier + MRZ presence/structure + aspect ratio/layout heuristics. If confidence < configured threshold → `UNKNOWN_DOCUMENT_MODE`.

`UNKNOWN_DOCUMENT_MODE` behavior: generic OCR still runs, MRZ still attempted if present, generic forensics (copy-move, quality-based) still run, template-specific validation is **disabled**, and mandatory human review is flagged in the report.

## 7. Stage 3 — OCR / MRZ / Barcode

- OCR: PaddleOCR. Pipeline: perspective correction → preprocessing → detection → recognition → bounding boxes → field normalization. OCR output is evidence, never ground truth — every field carries a confidence score.
- MRZ: parsed and validated with a **pure deterministic Python parser** (no LLM/ML) — ICAO check digits, document-number/DOB/expiry/composite checksums, country-code syntax, date syntax. A checksum failure is reported as `internal inconsistency`, not forgery — it is explicitly documented that OCR error and poor capture are common causes and must be considered before it is treated as evidence.
- Barcode/QR: decoded when present and cross-checked against OCR/MRZ. Absence of a barcode is `NOT_APPLICABLE`, never a negative signal. Decode failure on an adequate-quality image is `UNCERTAIN`, not `SUSPICIOUS`.

## 8. Stage 4 — Structural Validation

Applies only to known templates (MVP: the 1–2 templates shipped with the prototype). Compares candidate document (after normalization/alignment) against reference template metadata: field bounding boxes, photo/MRZ zones, aspect ratio, geometric tolerance.

**Rule**: template mismatch means structural deviation, not proof of forgery — different legitimate editions, print variance, and residual perspective error are real causes and must be named as such in the explanation text. Templates are versioned (`template_id`, `template_version`).

## 9. Stage 5 — Forensics

Each detector is **independent** and emits the shared evidence schema (§13). No detector output is thresholded directly into a fraud verdict.

- **Copy-Move (MVP)** — SIFT/ORB descriptor matching → geometric (affine) verification → spatial clustering. Classical CV, no training data required, reliable to demo. Repetitive legitimate security patterns (guilloché backgrounds, repeated micro-text) are explicitly suppressed/downweighted via a known-pattern mask.
- **Localized Manipulation Detector (MVP, honest-limitations)** — compact CNN (EfficientNet-B0) trained on MIDV-2020 + synthetic tampering (text/photo replacement, inpainting, copy-paste) with document-level train/val/test split. Output: suspicion score + heatmap + region + confidence. The spec explicitly acknowledges this model will **not generalize perfectly** to unseen forgery techniques or print-scan pipelines outside its training distribution — this limitation is stated in the report UI, not hidden.
- **Geometric/Structural Anomaly (MVP)** — derived from template alignment residuals and OCR box deviations; no separate model needed, reuses Stage 4 output.
- **Compression/DCT (Stretch)** — only applicable when raw, un-recompressed JPEG bytes are available from the original capture. Explicitly marked `NOT_APPLICABLE` after screenshot, messaging-app recompression, or print-scan. Never presented as a primary signal.
- **Noise residual / font-glyph / splice / morph / metadata analysis** — **Future**. Not attempted in MVP; listed as research directions only.

## 10. Stage 6 — Face / Identity

Pipeline: live camera → face detection (RetinaFace/InsightFace) → face quality (blur, pose, occlusion, size, illumination) → Presentation Attack Detection (PAD) → ArcFace embedding → cosine similarity → identity-consistency state.

**Explicitly distinguished**: face verification (visual resemblance between live face and document photo) is not document authentication and not legal identity/citizenship determination.

Poor face quality → `IDENTITY_UNCERTAIN`, never `MISMATCH`.

## 11. Presentation Attack Detection

Terminology: **Presentation Attack Detection (PAD)**, not generic "liveness." MVP is tested against exactly three attack types the team can reproduce and evaluate: printed photograph, phone/tablet screen replay, video replay. The report and any public materials state plainly that PAD coverage is limited to tested attack categories and does not claim universal spoof resistance. Untested attack types default to `UNCERTAIN`, routed to manual review.

## 12. Evidence Fusion (the core contribution)

Fusion is **rule-based and confidence/reliability/applicability-aware**, not a black-box score and not a simple average.

Fusion rules:
- Poor upstream capture quality reduces `reliability` of every downstream signal derived from that capture — it does not increase concern.
- Signals sharing a root cause (e.g., OCR failure and MRZ failure from the same blur) are **not** double-counted as two independent strong signals; the fusion engine groups signals by upstream dependency before weighting.
- `NOT_APPLICABLE` and `UNAVAILABLE` signals are excluded from scoring, not treated as neutral-negative.
- Contradictory signals (e.g., structural PASS + forensic HIGH) are surfaced explicitly in the report as a contradiction, not silently resolved.

Output: `LOW CONCERN / REVIEW REQUIRED / HIGH CONCERN` with a `recommendation` of `CLEAR / REQUEST_RECAPTURE / SECONDARY_INSPECTION / ESCALATE`. No probability-of-fraud number is produced — the team has no statistically calibrated dataset to justify one, and inventing one would be a false precision claim.

## 13. Evidence Schema

```json
{
  "signal": "mrz_viz_mismatch",
  "status": "mismatch",
  "value": "DOB differs: MRZ=1998-04-02, VIZ=1998-04-12",
  "confidence": 0.94,
  "reliability": 0.91,
  "applicable": true,
  "source": "OCR+MRZ",
  "region": [x, y, w, h],
  "explanation": "Date of birth in the machine-readable zone differs from the visual zone.",
  "model_version": "mrz_parser_v1",
  "preprocessing_version": "prep_v1",
  "timestamp": "..."
}
```

## 14. Explainability

Every flagged case must answer: What was flagged? Where? Which module produced it? How confident and how reliable? Was it applicable? What supports/contradicts it? What should the officer do next?

## 15. Identity Linking (Stretch)

PostgreSQL + FAISS over face embeddings for approximate duplicate detection, plus fuzzy name/DOB matching. Output is always labeled `POSSIBLE DUPLICATE IDENTITY — INVESTIGATION LEAD`, never "same person." Requires an explicit retention/consent/RBAC story before it is enabled even in demo form; if time-constrained, this stays Stretch/Future and is not part of the judged MVP.

## 16. Watchlist (Prototype)

Synthetic/local demo watchlist only. The system never claims access to a real government database. Production integration is described only as a future secure-adapter architecture.

## 17. NFC / ePassport (Future)

Chip read + certificate/signature validation is a separate, cryptographically-grounded verification path, explicitly out of MVP scope.

## 18. Multispectral (Future)

MVP is RGB-only. UV/IR/hologram/OVI inspection is future work; the spec does not assume every document class has the same security features.

## 19. Privacy & Security

Data minimization, configurable retention, discard of raw video when not required, encryption at rest and in transit, RBAC, audit logging, secure deletion, no unsupported legal/compliance claims (no "military-grade," no "GDPR-compliant" unless actually verified).

## 20. Tamper-Evident Audit Trail

Simple hash chain: `H_n = hash(event_n + H_{n-1})`. Called a **tamper-evident, hash-chained audit log** — explicitly not called blockchain, and not claimed to be absolutely immutable (a party with database write access could still rewrite the chain; the property being claimed is detectability of retroactive tampering, not cryptographic immutability against a privileged attacker).

## 21. Offline-First Architecture

React → FastAPI → local inference (CPU) → local PostgreSQL → encrypted offline queue → sync when network available. Core inference (quality, OCR, MRZ, template, forensics, face, fusion) works fully offline. Only future watchlist/government-integration and optional sync are network-dependent.

## 22. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React, TypeScript, Tailwind, shadcn/ui | |
| Backend | FastAPI, Pydantic, Python | |
| CV | OpenCV, scikit-image, NumPy | |
| AI (MVP) | PyTorch (CNN forensics), PaddleOCR, InsightFace/ArcFace | |
| AI (Stretch) | FAISS (identity linking only — not core) | moved out of core stack |
| Database | PostgreSQL | |
| Storage | local encrypted storage (MinIO optional) | |
| Deployment | Docker / Docker Compose | |
| Optimization (Stretch) | ONNX Runtime, TensorRT | |

No Kubernetes, Kafka, Redis, Neo4j, blockchain, or LLM agents anywhere in this project unless a specific measured requirement emerges (none has, as of this spec).

## 23. Database (entities)

`ScreeningSession(1—N)Document(1—N)OCRField`, `Document(1—1)MRZResult`, `Document(1—1)TemplateResult`, `Document(1—N)ForensicResult`, `Document(1—0/1)BarcodeResult`, `ScreeningSession(1—1)FaceVerification`, `ScreeningSession(1—N)Evidence`, `ScreeningSession(1—1)ScreeningAssessment`, `ScreeningSession(1—N)AuditLog`. All UUID PKs, all timestamps UTC.

## 24. API (public surface)

```
POST /screening/create
POST /screening/{id}/document          # upload/capture
POST /screening/{id}/process           # runs quality→...→fusion; progress via polling/SSE
GET  /screening/{id}
GET  /screening/{id}/evidence
GET  /screening/{id}/audit
POST /officer/decision
GET  /audit/{session_id}/verify
```

Per-stage endpoints from the original draft (`/document/quality`, `/ocr/extract`, `/mrz/validate`, `/document/structure`, `/forensics/analyze`, `/face/verify`, `/evidence/fuse`) are **internal service calls inside the orchestrator**, not separate public REST endpoints — exposing them publicly would let a client skip stages or reorder them, which the fusion engine assumes never happens. They may be exposed behind an auth-gated debug flag for testing only.

## 25. UI — Officer Workbench

Left: document viewer with overlays. Center: evidence tabs (Overview, OCR, MRZ, Structure, Forensics, Face, Audit). Right: assessment panel + officer actions (Clear / Secondary Inspection / Escalate / Request Recapture). Priority order for the default view: overall concern → why flagged → visual evidence → raw technical detail (expandable). Banner always visible: "AI screening result — not an authenticity determination."

## 26. Demo Scenarios (6, deterministic)

1. Genuine → LOW CONCERN
2. Altered DOB → MRZ/VIZ mismatch + localized manipulation → HIGH CONCERN
3. Expired, internally consistent → REVIEW REQUIRED
4. Correct document, wrong live face → identity mismatch → REVIEW/HIGH depending on confidence
5. Poor capture → RECAPTURE_REQUIRED
6. Unknown document type → generic analysis only → mandatory manual review

All mock outputs carry `is_mock: true`; UI shows a persistent `DEMO MODE` badge.

## 27. Evaluation

OCR: CER, WER, field accuracy. Document detection: IoU, corner error. Forensics: precision/recall/F1, localization IoU (measured only on the synthetic test set the team actually built — no invented numbers). Face: ROC-AUC, FAR, FRR at the configured threshold. System: p50/p95 latency, RAM, model size, on stated benchmark hardware. Where a metric isn't measured yet, the spec states the measurement methodology instead of a number.

## 28. Red-Team Test List

Photoshop/GIMP edit, screenshot, print-scan, messaging-app recompression, low light, glare, perspective distortion, blur, recompression, copy-move, text replacement, photo replacement. Failures are reported honestly in project docs, not hidden.

## 29. MVP / Stretch / Future

See build-spec §1 feature matrix (single source of truth — not duplicated here).

## 30. Final Positioning

DocShield AI is an offline-capable, AI-assisted document screening and investigation system combining deterministic document-standard checks, OCR/MRZ intelligence, structural conformity analysis (where a template is known), localized manipulation evidence, and face consistency into a single explainable evidence report for an authorized officer.

DocShield AI is **not**: an automated passport authenticator, a connection to any government database, a replacement for the officer, a guaranteed fake-detector, a legal decision-maker, or an RGB-based cryptographic authenticator.
