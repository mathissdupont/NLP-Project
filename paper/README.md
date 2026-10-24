# Manuscript workspace

`main.tex` is a venue-neutral English manuscript skeleton. `references.bib` contains three verified starting citations from ACL Anthology. No empirical results or publication claims have been inserted. Team names are listed for course identification; manuscript authorship order is not decided.

Suggested build with an installed LaTeX distribution, from `paper/`:

```text
latexmk -pdf main.tex
```

This requires `latexmk`, a PDFLaTeX-compatible distribution, and BibTeX. The current development machine has not provided these tools, so the scaffold is not claimed to have been rendered or visually checked. Select and verify a venue template only after deciding where to submit.

Writing leads and review responsibilities are in `docs/TEAM_PLAN.md`. Each result statement should trace to a frozen run and each external claim to a checked reference.
