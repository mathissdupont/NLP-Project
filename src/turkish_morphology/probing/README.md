# Probing handoff

Lead: Samet; reviewer: Halil. Implement linear classifiers and majority/character baselines here. Use `data.validation.probe_training_records` after release validation for real-only training selection.

Tune on development data only; fix task labels and record support. Train possessor probes on possessed forms only. Join cached vectors by verified example IDs rather than assuming row order. Probe fitting is not implemented yet.
