# Data lifecycle

- `raw/`: Unmodified source inventories and provenance; generated/downloaded contents are ignored by Git.
- `processed/`: Versioned, validated nominal JSONL; generated contents are ignored until deliberately released.
- `splits/`: Frozen split manifests; generated contents are initially ignored.
- `examples/`: Tracked illustrative records, always separate from research observations.
- `source_registry.json`: Source metadata and redistribution decisions.

See [DATA_SPEC.md](../docs/DATA_SPEC.md). No research dataset has been built or frozen yet. Ignored files are local artifacts, not a data publication or backup mechanism.
