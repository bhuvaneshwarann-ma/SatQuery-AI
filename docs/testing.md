# Testing & Quality Assurance Plan — SatQuery AI

## 1. Document Overview
This document specifies the testing strategy, test levels, validation scenarios, and acceptance verification procedures for **SatQuery AI**.

---

## 2. Testing Levels & Strategy

### 2.1 Unit Testing
* **Input Validator**: Test rejection of corrupt files, unsupported formats, invalid dimensions, and missing channels.
* **Agentic Router**: Verify deterministic classification across benchmark query prompts for each capability.
* **Coordinate & Evidence Transformer**: Validate conversion of normalized coordinates into display bounding boxes and image masks.
* **Confidence Estimator**: Validate range and calibration of output confidence scores ($0.0 \le c \le 1.0$).

### 2.2 Integration Testing
* **End-to-End Query Pipeline**: Submit query and asset -> verify correct tool dispatch -> assert valid answer, visual evidence, and execution trace.
* **Multi-Asset Pairing**: Test bi-temporal ($T_1, T_2$) and optical-SAR multi-image workflows.
* **Error & Fallback Handling**: Verify that low-confidence queries or corrupt inputs return structured error responses rather than unhandled exceptions.

### 2.3 Model & Domain Verification
* Test against standard benchmark sample tiles (e.g., port scenes, urban expansion, disaster zones).
* Evaluate hallucination resistance when queried about non-existent objects or details beyond sensor resolution.

### 2.4 Performance & Latency Benchmarks
* Single-image query response time target: $\le 5$ seconds.
* Paired-image query response time target: $\le 10$ seconds.
* GPU memory stability during continuous queries.

---

## 3. Test Cases Matrix

| Test ID | Category | Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-01** | Validation | Upload valid PNG/GeoTIFF | Asset ingested, dimensions returned, status `validated` |
| **TC-02** | Validation | Upload corrupt/non-image file | HTTP 422 with clear diagnostic error |
| **TC-03** | Validation | Bi-temporal query with single image | Rejected with `INVALID_IMAGE_PAIR` |
| **TC-04** | Router | Query: *"Locate all vessels in the harbor"* | Routed to `rs_object_grounding` pipeline |
| **TC-05** | Router | Query: *"What changes occurred between T1 and T2?"* | Routed to `bi_temporal_change` pipeline |
| **TC-06** | Grounding | Object detection on port image | Returns valid coordinates + visual overlay |
| **TC-07** | Change | Registered flood pair ($T_1, T_2$) | Highlights flooded areas + quantitative summary |
| **TC-08** | Optical-SAR | Cloud-covered optical + SAR pair | Correctly extracts structure signatures from SAR |
| **TC-09** | Observability| Any valid analytical query | Execution trace populated with latencies and stages |
| **TC-10** | Safety | Query requesting invisible sub-pixel details | High uncertainty flag or disclaimer returned |

---

## 4. Evaluator Demonstration Verification Checklist
- [ ] Test scenario 1: Single-image VQA on remote-sensing scene.
- [ ] Test scenario 2: Single-image object grounding with visual bounding boxes.
- [ ] Test scenario 3: Bi-temporal change detection with visual difference mask.
- [ ] Test scenario 4: Optical-SAR cross-modal reasoning under cloud cover.
- [ ] Test scenario 5: Input validation reject for invalid inputs.
- [ ] Test scenario 6: Execution trace inspection and confidence verification.
