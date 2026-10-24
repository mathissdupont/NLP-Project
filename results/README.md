# Experiment artifacts

`runs/` holds local immutable run directories; `figures/` holds derived plots. Generated artifacts are initially ignored by Git. Promote reviewed aggregate tables/figures deliberately, with their input run IDs and generating command.

There are no empirical results yet. The `prepare-run` utility records inputs with status `prepared`; completion and evaluation must be implemented by the research pipeline.
