# Route A Temporal V1

## Purpose

This document starts the real ChronoRAG main-line Route A as a separate research track from the official FEVER short paper.

It is intentionally a planning document only. No new experiment is launched here.

## Minimal Research Question

The first real Route A question is:

- **Can a lightweight retrieval-and-reranking pipeline reduce the use of stale evidence in temporally updated or conflicting knowledge scenarios?**

This is a different question from the FEVER short paper.

The FEVER short paper asks:
- can title-aware lexical reranking improve strict evidence-page ranking?

Route A asks:
- can a small trustworthy retrieval stack distinguish updated evidence from outdated evidence and prefer the more reliable current evidence?

## Minimal Modules

Route A V1 should contain only the minimum modules needed to test that question:

1. candidate retrieval backbone
- reuse BM25 retrieval infrastructure already exercised in the FEVER short paper

2. temporal update / conflict signal
- a lightweight rule-based or pattern-based temporal score
- goal: detect whether a candidate appears outdated or updated relative to the query

3. source reliability weighting
- a lightweight rule-based reliability prior
- goal: prefer stronger sources when evidence conflicts or partially overlaps

4. final reranking layer
- combine retrieval score, temporal signal, and reliability signal

5. evaluation layer
- not FEVER strict gold-page ranking as the final target
- instead, a task-specific notion of “updated evidence preferred over stale evidence”

## First-Round Exclusions

The first Route A round should explicitly **not** include:

- Route B evidence graph construction
- Route C generation
- sentence-level attribution
- refusal / abstention
- dense retrieval
- large parameter sweeps
- full ChronoRAG system claims

These are downstream phases, not part of Route A Temporal V1.

## First-Round Acceptance Criteria

Route A V1 should be considered minimally successful only if it can demonstrate all of the following:

1. the pipeline runs end to end on a small but real temporal-conflict benchmark or curated subset
2. the temporal signal changes ranking behavior in a measurable way
3. updated evidence is preferred over stale evidence often enough to beat a retrieval-only baseline
4. source reliability changes at least some conflict cases in a sensible direction
5. outputs are inspectable through per-query artifacts, not only aggregate metrics

## Assets To Reuse From The FEVER Short Paper

The FEVER short paper should be reused only as backbone infrastructure, not as the Route A research claim.

Reusable assets:
- [search.py](/D:/HUYAOYANG/Work/ChronoRAG/src/retrieval/search.py)
  BM25 retrieval entry point
- [build_bm25.py](/D:/HUYAOYANG/Work/ChronoRAG/src/retrieval/build_bm25.py)
  index build / load support
- [eval_main.py](/D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_main.py)
  current orchestration skeleton
- [official_strict_revalidation.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/official_strict_revalidation.py)
  example of post-hoc reranking evaluation discipline
- [significance_analysis.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/significance_analysis.py)
  example of statistical packaging discipline
- run directory conventions already used in `runs/`
- notes / tables discipline already used for the short paper line

What should **not** be reused as the Route A claim:
- FEVER strict gold-page framing itself
- title-overlap-specific method story

## Recommended Immediate Next Artifact

Before any Route A Temporal V1 experiment is run, the next artifact should be a task contract document that defines:

- dataset candidate
- input query schema
- evidence schema
- temporal label definition
- stale vs updated success criterion
- evaluation metrics

That document should be created before code or long-running experiments are changed.
