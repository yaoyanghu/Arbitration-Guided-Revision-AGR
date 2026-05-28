# Deployment Notes

- Primary compatibility path: `/home/huyaoyang/Projects/ChronoRAG`
- Rented server current user: `root`
- Suggested migration strategy:
  - keep repository root named `ChronoRAG`
  - set `CHRONORAG_ROOT` on each server
  - avoid machine-specific absolute paths in Python code

The rented server can also expose a compatibility symlink:

```bash
/root/ChronoRAG -> /home/huyaoyang/Projects/ChronoRAG
```
