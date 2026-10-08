# Pending live carriers as paid clearing controls

This is a finite construction experiment on PR #62's scalar graph and PR #57's
joint frame compiler. It extends the clearing basis with live carriers whose
next use is already scheduled. Combining it with PR #60's descending-rank
retired-slot order, with descending equal-rank slot ties at h=25, gives the
selected exact coarse witness

    bit saving = 5103199 / 10^11
    kappa      = 5102938 / 10^11
    W          = 137151806

The unchanged role counts are 27,918 and 36,586. Both serialized words pass
the independent complete input/dirty-basis replay in both orientations, and
their actual frame transitions pass the inherited fixed-I+J bounded-minor/CRT
profiler. `selected-arithmetic.json` records the exact moment, all 47 strict
assembly constraints and seven margins. These are conditional finite checks,
not formal verification or independent acceptance of the multiplication
theorem. `selected-manifest.json` pins the delivery files. Ascending ties at
both dimensions give the slightly smaller kappa 5102898/10^11, recorded as a preceding local experiment.

## The changed operation

The inherited compiler represents the clean-input signal on each physical
scratch slot as a binary vector. Retired slots can be cleared by an invertible
sequence of XORs when their vector is in the span of compatible retired slots
and the current region's output anchors. Clearing means that the clean-input
signal becomes zero; arbitrary initial scratch is **not** assumed zero.

The new `pending` map records, for each live physical slot, the region of its
already assigned next use. On entering that region, each incoming slot is
removed from `pending`. Assigning a retained signal or an outgoing copy creates
its new pending use. Designated final output slots retain their terminal frame.

Consider a current region with frame E, and a pending carrier in current frame
F whose next assigned use has frame G. It may be added to the clearing basis
only if

    F is contained in E, and E is contained in G.

Adding an unused candidate to the *compile-time* Gaussian-elimination basis
does not perform a scalar operation. If an actual clearing expression uses
that carrier, the compiler calls its existing literal `xor` routine. This
records and charges both source and target frame incidences, including F -> E
on the live control. The carrier is only an XOR control and its clean signal
is unchanged. Its later use can still raise it from E to G. Repeated use is
subject to the same inclusion test with its then-current frame, so the entire
physical frame path remains nested.

This introduces no free copies, source-dependent runtime choice, or uncharged
frame jump. Candidate selection happens once while constructing a fixed finite
word. Every operation in that word is still a literal two-slot XOR.

## Dirty state and frames

The compiler's block transformations remain invertible on all incoming dirty
coordinates. Each additional clearing operation is invertible too. Therefore
the complete mixer M is invertible. The inherited word has the form

    M, J, inverse(M), V, M, J, inverse(M), V.

Its dirty-scratch cancellation argument only requires the mixer to be a fixed
invertible word and its clean signal map to give the required injection. The
new controls preserve those properties. This argument is supplemented by
independent serialized replay on **every** input and dirty basis vector for
both h=23 and h=25 and both orientations; see `selected-replay-*.json`.

Frame preparation independently reconstructs every transition from the actual
XOR list, checks it against the auxiliary event log, and checks every inclusion.
All frames remain the inherited original-envelope projectors. Consequently
the same fixed-I+J formulas and bounded-minor/CRT argument apply without a new
projector formula or denominator bound. The ranked/global profiles use 6,049
and 7,997 CRT-checked matrices and report zero modular disagreements.

Neither W nor total rank changes. The actual fixed-basis child profiles change
because different clearing expressions promote different slots at different
points. This is the source of the finite moment improvement; counting roles
alone misses it.

## The selected finite profile improves every concave power

There is also an exact comparison independent of the selected parameter grid.
Let d_t be the selected child multiplicity minus PR #63's pinned multiplicity.
The integer certificate `concavity-screen.json` checks

    sum(t*d_t) = 0,
    C_k = sum(min(t,k)*d_t) <= 0 for every integer 1 <= k <= 529,

with a strict inequality for some k. Its smallest C_k is -619850. The source
profile is pinned to PR #63 commit `aa7701b68540b7863d3b66a414e4319915d6282d`
in `comparison-pr63.json`. For any f with f(0)=0 and decreasing discrete
increments, the identity

    sum(d_t*f(t)) = sum_(k=1..528) (2*f(k)-f(k-1)-f(k+1))*C_k

holds because the linear mass term vanishes. For f(t)=t^(1-a), 0<a<1, every
coefficient on the right is strictly positive. The new sum is therefore
strictly smaller. Since m and W are unchanged, the selected finite moment is
strictly below PR #63's for **every** saving 0<a<1. This is a comparison of
certified finite child distributions, not a claim that the whole multiplication
machine has been formally verified. Run `check_dominance.py` to reconstruct
every integer in this comparison. The capped-mass comparison format follows
the concurrent PR #64 verification package by `rfu08` (with substantial OpenAI
Codex assistance); the identity and this candidate's integer certificate are
reconstructed here for the different profile.

## Retained assumptions

This supplies a changed finite word and its explicit frame schedule. It does
not reprove the general residual compiler, finite-alphabet multitape recursion,
copied-center transfer, two-stage data geometry, analytic precision, semantic
bulk/routing/recovery interfaces or their eventual cutoffs. These are the same
conditional dependencies stated in PR #62 and PR #57. The original graph,
data blocks, copied centers, endpoint copy and complex saving remain inherited.

The general extension of the reclamation argument is the local inclusion and
invertibility argument above. It does not assert that all pending-carrier
choices are legal: both inclusions and the pending-use lifecycle are essential.
No optimality is claimed for candidate order or the resulting child profile.
The two axis dimensions and both resulting words are fixed finite objects.
The asymptotic argument uses these words through the inherited finite-network
interface, with every extra scalar XOR contributing to its finite operation
constant. This experiment does not claim a free all-size search or an improved
uniform runtime for finding the words.

## Reproduction

From the repository root, with Python assertions enabled:

```sh
python3 research/global-anchor-screen/selected_compile.py --h 23 --work-dir /tmp/global-anchor-selected
python3 research/global-anchor-screen/selected_compile.py --h 25 --work-dir /tmp/global-anchor-selected
python3 scripts/experiments/binary_frame_profile_prepare.py /tmp/global-anchor-selected/word-23.json.gz /tmp/global-anchor-ranked-23.bin
python3 scripts/experiments/binary_frame_profile_prepare.py /tmp/global-anchor-selected/word-25.json.gz /tmp/global-anchor-ranked-25.bin
c++ -O3 -std=c++17 -I references/frame-compiler/pr48/scripts/partial_swap scripts/experiments/binary_frame_profiles.cpp -o /tmp/global-anchor-profiler
/tmp/global-anchor-profiler /tmp/global-anchor-ranked-23.bin
/tmp/global-anchor-profiler /tmp/global-anchor-ranked-25.bin
python3 research/global-anchor-screen/evaluate.py /tmp/global-anchor-ranked-23.bin.profiles.json /tmp/global-anchor-ranked-25.bin.profiles.json --prefix selected-
python3 research/global-anchor-screen/check_dominance.py
```

On the current macOS host, add
`-isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk` to the
compiler command because its default SDK does not link with the installed
toolchain. This is a host workaround, not a mathematical source change.

The selected driver fixes descending-rank ties to increasing slot index at
h=23 and decreasing slot index at h=25. The h=25 choice is the independent
incremental research lane's round-two ordering refinement.

The integrated `make global-anchor-verify` target reproduces both words in a
temporary directory, independently reconstructs the actual profiles, checks
the exact moment and assembly, and reruns the all-power comparison.

## Attribution

Avi Eisenberg supplied PR #62's interval-strip and pair-assembly graph, with
Anthropic Claude assistance. eumemic supplied PR #57's joint compiler with
OpenAI Codex assistance. Chafik Boukhalfa supplied PR #60's ranked reclamation
rule with OpenAI Codex assistance. Dominik Scholz requested this research; the
pending-live-carrier experiment and its code/proof were prepared with
substantial OpenAI GPT-6 Astra/Codex assistance. All prior credits remain in
the imported source and repository NOTICE, including icekylinx, Rohan Arun,
RaD/hipotures, James Chang, Zhihao Chen, Aurel Prosz, Swapnil Jain, Douglas
Colkitt, OpenAI, Harvey and van der Hoeven. Apache-2.0.
