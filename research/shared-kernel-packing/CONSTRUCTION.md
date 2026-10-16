# Construction

## Declared preload-move stage (`vendor/pm/`)
Applied after the PR2857 four-kernel stage. `patch-{base,extra}.json` declares: 16 A edits (2 replaced preload gates `457+=498 -> 456-=498`, `458+=510 -> 459-=510`; 14 inserted: the 5 kernel gates of each quartet, the delivery entries `457+=499 [42]` / `458+=510 [42]`, and the undo gates `467-=500`, `465-=512`), 2 B edits (carrier raises of helpers 499 and 510 by the entry line 42), 344 zero-frame compensation rewrites and `start_extra` {457:[42], 458:[42]}. `preload_move.apply` checks every old gate, re-derives the frame profile, width inventory and inverse cleanup and requires the declared hashes. `preload_move_review.py` is independent of it and runs the inherited exact auditor (forward and dual replay) plus twelve fault controls, each rejected.

## Fill (`data/`)
T74: two interleaved copies of PR2857's T37 chronology, 666 calls, 271728 roles, produced by a fixed-count per-pattern flow (`data/fill-producer/`, solver output; not reconstructed here) and checked literally by `tools/audit_owners2857.py` and `review/review_current.py`. The producer labelled helpers by sorted width; `data/fill-producer/HELPER-RELABEL.json` is the per-width-class relabelling to the true helper widths derived from the shipped words.
