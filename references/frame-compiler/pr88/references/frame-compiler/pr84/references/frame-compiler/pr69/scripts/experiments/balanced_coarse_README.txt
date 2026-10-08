Balanced coarse sums: finite physical witness

Run from the repository root with Python 3 and a C++17 compiler available:

    python3 scripts/experiments/verify_balanced_coarse.py

An independent dense global-support audit also checks the scalar graph:

    python3 scripts/experiments/pr62_exploration/audit_balanced_coarse.py \
        --check certificates/balanced-coarse-independent-audit.json

Regenerate each physical word with the pinned compiler, for example:

    python3 scripts/experiments/balanced_coarse_compiler.py --h 23 \
        --output /tmp/balanced-coarse-23-receipt.json \
        --word /tmp/balanced-coarse-23.json.gz

Repeat with --h 25 and corresponding output paths.

Assertions must remain enabled. The verifier independently replays both saved
physical XOR words on the complete input and dirty basis in both orientations,
checks every original-envelope frame incidence, reconstructs transitions,
recomputes fixed-I+J profiles with bounded-minor CRT controls, and checks the
exact recurrence, all 47 strict assembly inequalities and seven margins.
It binds the source manifests, compiler record, words and verification code.
It also excludes the complete pinned predecessor child network at the new
bit saving using an exact lower moment bound.

The fixed rational witness is

    bit saving = 513710137 / 10000000000000
    kappa      = 1284209371 / 25000000000000 = 0.00005136837484.

The local change factors a four-edge coarse sum into two two-edge column sums
and then their sum. Each sum still takes three additions before interning;
existing interning can now share the column sums with strip computations.
The intermediate envelopes and physical carrier opportunities also change.
The resulting words use 27,698 roles at dimension 23 and 36,300 at dimension
25; actual transition profiles and every dirty coordinate are checked.

The surrounding interval graph is PR62 (Avi Eisenberg / ikeboy with
Anthropic Claude assistance), joint frame compilation is PR57 (eumemic with
OpenAI Codex assistance), and descending-rank reclamation is PR60 (Chafik
Boukhalfa with OpenAI Codex assistance). Dominik Scholz's contemporaneous
PR63 uses those three ingredients before the balanced coarse-sum change.
The pinned ranked-interval comparison is an independent reproduction of
that predecessor, with finer rational rounding. PR64 reports a still finer
arithmetic refinement of the same predecessor words; the certificate labels
that comparison as reported, without claiming to replay the PR64 sources. The new factorization and
this finite integration were prepared with OpenAI Codex assistance.

Outputs use the certificates/balanced-coarse- prefix. The exact composition
is in balanced-coarse-kappa.json and the completed replay record is in
balanced-coarse-validation.json. The producer and inherited sources are
hash-pinned under references/frame-compiler/balanced-coarse; original
attribution and license notices are preserved.

Scope: this is a finite conditional certificate. The data profile and its
ten exact rational recoveries, ordered affine residual compiler, fixed-tape
recursion, scalar overhead, balanced transfer, analytic, routing and recovery
interfaces remain inherited dependencies. It is not an unconditional proof
of an improved integer-multiplication theorem or a global optimality claim.
