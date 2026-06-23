# Paper-Safe Method Naming

| Internal/unsafe name | Paper-safe display name | Placement | Required note |
|---|---|---|---|
| TP-FP | TP-FP RAG | Main | Frozen top-2 evidence |
| AGR-full | AGR | Main | Proposed method |
| Self-Refine-FP | Self-Refine-FP adaptation | Main | Fixed-pool adaptation |
| RARR-FP | RARR-FP adaptation | Main with footnote | Research restricted to frozen evidence; no external retrieval |
| FaithfulRAG-FP | FaithfulRAG-inspired FP control | Appendix | No reusable official implementation was found |
| CRAG-FP | CRAG-inspired FP evaluator control | Appendix | Corrective retrieval removed |

Forbidden labels: `official RARR-FP`, `official FaithfulRAG-FP`, `official CRAG-FP`, and unqualified `CRAG`.
