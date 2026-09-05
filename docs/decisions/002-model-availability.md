# ADR 002: AI Model Availability Strategy

## Status: Accepted

## Context
The system uses multiple AI models (PaddleOCR, InsightFace/ArcFace, EfficientNet-B0). Not all may be available at runtime due to:
- Missing model weights
- Missing pip packages
- Insufficient hardware

## Decision
Every AI module implements the adapter interface pattern (build spec §4):
1. **Interface** — abstract base class defining the contract
2. **Real implementation** — wraps the actual model library
3. **Mock implementation** — deterministic, labeled `is_mock: true`

At startup, the system:
1. Checks for model file presence via manifest
2. Attempts to import the model library
3. Falls back to `MODEL_UNAVAILABLE` status if either fails
4. Uses mock adapter only when `MOCK_MODE=true`

## Consequences
- System never crashes due to missing models
- Business logic never imports model libraries directly
- Swapping implementations requires no changes to services/routes
- Missing models are surfaced clearly, never hidden behind fake results
- EfficientNet-B0 forensic CNN will use mock adapter until training data (MIDV-2020) is obtained and model is trained
