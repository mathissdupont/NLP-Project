# Research decision log

Dates use the team's Europe/Istanbul calendar. This log records local planning, not external preregistration.

| ID | Date | Decision | Rationale | State / evidence |
| --- | --- | --- | --- | --- |
| D001 | 2026-10-24 | English README and planned manuscript; Turkish internal team plan | Keep the research accessible and the team workflow practical | Initial direction; README and TEAM_PLAN.md |
| D002 | 2026-10-24 | Core nominal study first, verbal morphology later | Separate noun possession from verbal person/tense; keep the first study manageable | Draft protocol |
| D003 | 2026-10-24 | Start the pilot with BERTurk, frozen weights, isolated words, mean pooling | Establish correctness and cost before expanding the model matrix | Proposed settings in configs/pilot.toml |
| D004 | 2026-10-24 | Pair/root-disjoint partitions and documented nonce screening | Reduce leakage and avoid claiming verified pretraining novelty | Data contract and integrity checks |
| D005 | 2026-10-24 | First schema supports regular, non-alternating stems | Make root/segment identity explicit before adding morphophonological alternation | Schema v0.1.0 |
| D006 | 2026-10-24 | Initial work-package allocation | Give every member implementation, review, reading, and writing responsibilities | Proposal in TEAM_PLAN.md; team review pending |

For a new entry include: question; considered options; decision; contributors; date; affected files; whether main-test results had already been inspected; and impact on earlier results. Mark superseded decisions rather than silently rewriting history.
