PR53 skip-prefix graph with joint frame compilation
=================================================

Conditional local witness: kappa = 4669442391 / 10^14 > 2^-15.
This is 3.10003% above PR54's reported 4529040672 / 10^14.
These are asymptotic exponent savings, not measured runtime improvements.

From the repository root, with Python 3 and a C++17 compiler:

    python3 scripts/experiments/verify_skip_frame.py

The verifier independently replays the serialized physical XOR words on
every input and dirty basis vector in both orientations, checks every
original-envelope frame inclusion and terminal output, reconstructs all
transitions from the actual XOR word, freshly computes the ordered fixed-I+J
profiles with bounded-minor/CRT checks, and verifies the exact recurrence,
47 strict assembly inequalities, seven margins and eventual cutoff arithmetic.

To regenerate the producer words separately:

    python3 scripts/experiments/skip_frame_compiler.py --h 23 --output /tmp/skip23.json --word /tmp/skip23.json.gz
    python3 scripts/experiments/skip_frame_compiler.py --h 25 --output /tmp/skip25.json --word /tmp/skip25.json.gz

The word contents reproduce the certificates/skip-frame-word-{23,25}.json.gz
records exactly after decompression. Gzip headers may name different files.
The compiler groups identical rational frames, synthesizes invertible binary
maps on whole regions, retains compatible incoming signals, and clears
retired signal components while preserving arbitrary dirty state. It does
not assume zero-initialized scratch or free endpoint/copy operations.

Roles: h23 = 31,416; h25 = 41,264. Physical width W = 153,481,944.
The exact bit saving is 116741511 / 2500000000000. The data-pair count
4,073,300, rank deficit 1,846,900, and maximum child width 529 are unchanged.

Scope: the new verifier regenerates every new auxiliary profile. The unchanged
data geometry, complex branch, all-size residual compiler and finite-alphabet
tape/analytic/routing/recovery interfaces remain inherited from pinned PR48.
The full data-pair calculation is not repeated by this command. This is a
finite conditional witness, not formal verification of those interfaces.

Source: Avi Eisenberg / ikeboy with Anthropic Claude assistance supplied PR53's
skip-prefix graph (3ffd4021995c959ac02d12920e0279ae97dd03c7). Chafik Boukhalfa,
Rohan Arun, RaD / hipotures, icekylinx and earlier contributors supplied the
inherited pipeline; all original credits remain under references/frame-compiler.
This local joint frame compiler and integration used OpenAI Codex assistance.
PR54 was tested as a graph alternative; its paid clones are not used here.

The publication branch contains the selected skip-prefix witness and its
pinned dependencies.

Finite mechanism
----------------
For each identical original envelope, independent requested output rows,
selected independent incoming signals, and unit-vector completion form an
invertible binary matrix on every incoming physical role. Gaussian elimination
synthesizes that matrix as literal XOR gates in the shared frame. Dependent
outputs are delivered to distinct fresh or signal-cleared roles. Every retained
continuation goes to a strictly later region with a containing frame.

Clearing a retired role removes its input-dependent signal, not its arbitrary
dirty value. If L is the resulting invertible mixer, V the injection and J the
read-only scatter, the exact output identities give J L V = I. The chronological
word L,J,L^-1,V,L,J,L^-1,V cancels the contribution of any initial dirty vector
and restores every auxiliary. The verifier checks this full word and its dual
on all basis vectors, independently of the compiler's internal symbol tracking.

Each role has a monotone frame path. Every nonidentity transition in the
compiler's event list must equal the multiset reconstructed from XOR incidences.
The inherited fixed-I+J projector formulas and bounded-minor checks then give
the actual contiguous recursive children, including copied centers and endpoint
corrections. Their total rank is mW-N+L, with m=575, N=4073300, L=2226400.
The exact moment at the reported bit saving is strictly below one; the inherited
balanced assembly at kappa=4669442391/10^14 checks all 47 inequalities and seven
positive margins. The all-size transfer and analytic hypotheses above remain
assumptions rather than conclusions of these finite computations.
