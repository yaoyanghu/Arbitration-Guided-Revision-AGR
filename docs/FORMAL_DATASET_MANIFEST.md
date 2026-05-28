# Formal Dataset Manifest

## HOH Formal

- queries file: [hoh_formal_1024.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/processed/hoh_formal_1024.jsonl)
- corpus file: [hoh_formal_1024_corpus.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/corpus/hoh_formal_1024_corpus.jsonl)
- query count: `1024`
- corpus count: `2125`
- selection rule:
  - deterministic first-1024 slice from the connected HOH raw training file
  - includes both current and stale evidence documents when available

## TempRAGEval Formal

- queries file: [temprageval_formal_1244.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/processed/temprageval_formal_1244.jsonl)
- corpus file: [temprageval_formal_1244_corpus.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/corpus/temprageval_formal_1244_corpus.jsonl)
- query count: `1244`
- corpus count: `1773`
- selection rule:
  - use the full currently available authenticated TempRAGEval test file in the workspace
  - keep both evidence slots when present

## Rules

- these formal files are frozen and must not be silently replaced by new exploratory subsets
- pilot files remain separate and must not be mixed into formal tables
