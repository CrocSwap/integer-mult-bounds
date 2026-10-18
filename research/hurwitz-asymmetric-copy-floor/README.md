# Scoped negative result: asymmetric Hurwitz E8 copy floor

Every scalar-total binary decoder on #620's ten quaternionic E8 lines has
copy charge at least **10 quaternionic rank units = 40 rational rank units**.
The bound is sharp for every fitting matrix, including all 992 nonsymmetric
completions. Allowing arbitrary reader/source asymmetry and any number of
totals therefore does not repair this unit's negative optimistic deficit.
**No new kappa or physical supplier is claimed.**

The new ingredient is a short weighted rank argument over the 32 choices
of one line from each orthogonal pair. It resolves the asymmetric case
explicitly left open by Joel Pulikkan / GamingPuzzled's #620 extension-ring
report, using a method independent of its unfinished SAT run.

From the repository root, with Python 3.10+ and no third-party dependencies:

    python3 -B research/hurwitz-asymmetric-copy-floor/verify.py

Expected final line:

    PASS_HURWITZ_ASYMMETRIC_COPY_FLOOR: cost 10; 1048576 support pairs; 1024 decoders; 8 negative controls

The command reconstructs all 240 roots and ten quaternionic lines, checks
3,025 Gram blocks with two exact rational implementations, exhausts all
reader/source supports and fitting matrices, runs the controls, and compares
the complete result with [RESULTS.json](RESULTS.json). To regenerate a
separate receipt, append --write /tmp/hurwitz-results.json.

[PROOF.md](PROOF.md) specifies the model, proves the bound and sharpness, and
prices the optimistic budget. Its all-total lower bound is a written rank
argument; finite replay is not a formal proof of the multiplication theorem.
[SOURCES.json](SOURCES.json) pins the inherited files, and
[CLAIM.md](CLAIM.md) records seed 49, the bounded scope and overlap checks.
The completed checks and their limits are in [VALIDATION.md](VALIDATION.md).

Base: 66849e1475c930fd7732b1a0067ffee7e1e95f60.
The accepted conditional kappa at this base remains
51110230636731/31250000000000000 (#626 with #543). Its construction and
selected pointer are untouched. Only this research directory is added.

The source hashes check context; no predecessor code or SAT solver is
imported. The package distinguishes #620's retained reviewed head from its
later open head. See [NOTICE.md](NOTICE.md) for attribution, source status
and substantial AI-assistance disclosure.
