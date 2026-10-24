# Run directories

A prepared run stores `manifest.json`, the exact config snapshot, and a dataset snapshot. The manifest includes SHA-256 hashes, environment versions, UTC creation time, Git state, and enabled model revisions. Keep large artifacts in backed-up research storage; Git ignore is not a backup.

Future training code must write predictions, class support, metrics, exclusions, timing, and failure/completion state. Never mark a prepared run as a completed experiment merely because its directory exists.
