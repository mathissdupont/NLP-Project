# Representation extraction handoff

Lead: Fatmanur; reviewer: Samet. Implement token alignment, frozen encoder evaluation, all-layer extraction, and target-word pooling here.

Outputs must preserve example IDs and include checkpoint/tokenizer commit, layer index, pooling method, dataset/config hashes, subword counts, rejected/truncated examples, vector shape/dtype, and runtime/hardware. Reuse a cache only when these identities match. Extraction is not implemented yet.
