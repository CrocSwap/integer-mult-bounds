# Two-target output basis recovery

The constructor adds a new output-side representation change on top of the
frozen response-subspace/overlapping-entrance candidate. It preserves the complete
raw rational operator and saves the paid local histogram
{1:+1,3:-1,4:-1,6:+1}; one net extra literal scalar gate is charged.

Portable replay, from this directory:

    python reconstruct.py SOURCE_CANDIDATE OUTPUT_DIR --source-sha256 SOURCE_SHA256

OUTPUT_DIR must be new. Only Python's standard library is used. The output is
candidate.json and RECEIPT.json. The constructor pins the unchanged source hash,
replays all1021 arbitrary-dirty input columns, checks nested paths and cleanup,
and rejects omission of either of the two basis-adapter gates.

The source B word must match the explicitly asserted original feed/recovery
positions. This deliberately refuses an unrelated changed word rather than
silently finding approximate replacements. Importing reconstruct.py provides
the pure-copy function transform(candidate), returning the changed dictionary
and receipt without writing files.

The discovery screen is a bounded native C++ exact rational basis search with a
floating paid nomination score. Its candidate acceptance evidence comes from
reconstruct.py, followed by the root's independent local scalar/phase and global
price/assembly checks. The stage alone claims no kappa and no Lean certification.

PROOF.md contains the sufficient algebra, literal positions, changed path costs,
and scope. combined194-receipt.json binds the final194-gauge source and resulting
candidate. The older173 and119 experiments are preserved for provenance; they
are not extra discoveries or additive gains.
