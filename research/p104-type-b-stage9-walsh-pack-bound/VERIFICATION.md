# Verification

The lead verifies the binary Gaussian eigenvectors and exact Walsh–C identity, derives the all-width residue count, and recomputes the directed eight-port price from the inherited exact quote. The independent engine applies each binary Gaussian factor on all 256 Walsh basis columns with signed Gaussian-integer arithmetic, checks both forward and adjoint, authenticates the literal C and port constants, and reconstructs the exact whole invoice delta from #7334. Both engines use one fixed clock, eight mapped ports and a 30-second cap. The width-one gate is exhaustive and has zero unresolved columns. The all-width statement uses the algebraic proof in [PROOF.md](PROOF.md).

`replay.py` authenticates files by package-relative path and rejects duplicate JSON keys. It regenerates both expected receipts, verifies agreement, then mutates the actual selected stage-9 mask to stage 10 in a disposable caller copy. The real independent replay rejects that caller. Separate phase controls reject sign reversal and omission. No scientific engine depends on prior generated temporary files or network access.

The original lead run took 0.03s. The original independent calculation and its relocated replay each took 0.08s and returned identical results. The original independent output reported PASS before its shell wrapper hit a reserved variable while recording exit. The clean repeated replay recorded exit 0. Package verification recomputes the scientific results with paths adapted to this directory.

The exact source addresses and byte hashes are in [PROVENANCE.json](PROVENANCE.json). The replay uses POSIX CPython 3.12 and its standard library.
