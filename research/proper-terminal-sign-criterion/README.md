# No hidden positive bill for fully crossing helper paths

For the proper-terminal helper rank bill of Nick Petalas's
[PR #7331](https://github.com/CrocSwap/integer-mult-bounds/pull/7331), a positive
interior bill cannot hide behind a nonpositive left endpoint, for **any finite
number of unit-charged paths reaching the terminal**. This resolves its first
open question on that domain. It does not improve κ.

For real `0<t<1`, `T>0`, a nonempty list `0<=a_i<=T<=b_i`, and `A=max a_i`, set

```text
H_ab(x) = (x-a)^t + (b-x)^t - (b-a)^t
G(x)    = H_0T(x) - sum_i H_ai,bi(x),    A <= x <= T.
```

Then `G` is positive somewhere on `[A,T]` **if and only if `G(A)>0`**.
The same criterion applies at the left endpoint of any permitted closed
subinterval. The proof establishes that each ratio `H_ab/H_0T` is nondecreasing in
`x`: convex endpoint remainders divided by a positive concave bridge have the
required monotonicity. Thus `G/H_0T` is nonincreasing, even when `G` itself is not.
See [PROOF.md](PROOF.md) for the all-real argument and zero-length boundaries.

The predecessor's four-path example still has a negative interior maximum
above both endpoint values. The new result decides the **sign**, not the
maximizing dimension. Paths ending before `T`, signed or arbitrary fractional
charges, native legality and a complete implementation invoice are outside the
claim. A positive fractional-weight counterexample shows why the unit-charge
hypothesis cannot simply be dropped at the zero endpoint.

## Reproduction and evidence

Python 3.12, standard library, from the repository root:

```sh
python3.12 -W error -I -B research/proper-terminal-sign-criterion/verify.py
python3.12 -W error -I -B research/proper-terminal-sign-criterion/independent_check.py
python3.12 -B scripts/research_package.py --package research/proper-terminal-sign-criterion
python3.12 -B scripts/check_research_commit.py --package research/proper-terminal-sign-criterion --check-modes --check-source-history
```

The registered manifest repeats both direct commands with `-O`; explicit
exceptions keep every acceptance check active. The primary checker uses integer
nth-root enclosures at exponents `1/4,1/3,1/2,2/3,3/4`: 1,440 ratio comparisons,
450 normalized-bill comparisons, 225 zero-start bills, 90 endpoint checks,
342 root controls and eight rejecting domain/direction controls. The separate
checker imports neither it nor predecessor code. At `t=1/2`, integer square-root
bounds cover 1,050 ratio comparisons, all 2,900 multisets of one to three paths
in the stated grid (`T=2..6`, `a=0..T-1`, `b=T..T+2`), 11,600 normalized-bill
comparisons and 11,275 interior signs for 2,255 nonpositive-left fixtures.
It also verifies the four-path counterexample and six scope/direction controls.
These finite checks corroborate the proof; they do not establish its quantified
claim by extrapolation.

The baseline source-binding check passed after materializing 147 missing
tracked files, covering 221 selected inputs/pointers. It is not a scientific
replay of selected PR7000. No selected-family cold replay, native execution,
Lean, Docker, supplier admission or human/kernel proof review is claimed.

## Sources, overlap and task scope

Base: `e54523517d0f03e58352e647c403a5af3e525a57`, fetched and pulled from canonical
CrocSwap main. Revision 8's catalogue still references PR5599; the contextual
picker correctly reports that mismatch against selected PR7000 and conditional
κ `363005817/100000000000`. The full original `p104-side-correction` card is
preserved in [TASK.json](TASK.json); the actual scope is explicitly changed to
this abstract sign lemma. A useful fully charged split still needs its own
word, legality, ownership, restoration and ordinary-cost evidence.

PR7331 is pinned at `e5383f5c2973c9520918cbe6ebe9c6e6867e5771`.
[Its retained proof](sources/pr7331-PROOF.md) is byte-equal to the immutable
published source; [SOURCE-PINS.json](SOURCE-PINS.json) records the URL and digest.
This retains the question, formula and witness, not an assertion that every
predecessor proof step was audited. No predecessor executable is imported.
The pending head is not represented as an ancestor; only the base catalogue
and selected record are Git provenance in [SOURCES.json](SOURCES.json).
All scientific runtime inputs are package-local.

The live handoff board and start-here conventions were read. The all-state
`7331` title/body search found #7331, #7332 and #7396: the latter two concern
literal helper cuts/quiet lifts, not this all-path sign theorem. The latest 20
PR titles were inspected through #7459. This bounded coverage is not proof of
novelty and does not cover every diff or unpublished result. The local sparse
overlap helper searched 41 of 10,178 HEAD note paths; 10,139 were omitted, and
its offline remote cache was not treated as current. Browser access
was signed out, so no advance public claim was posted. The repository permits
an unclaimed bounded session; this package supplies the public finding.

## Open next questions

1. **Mixed paths ending before the terminal.** Characterize the sign of the
   bill on `[max a_i, min(T,min b_i)]` when some `b_i<T`. This would tell which
   real helper bills can use endpoint screening. Start with two paths straddling
   `T` and check normalized derivative signs; the present endpoint ordering
   proof no longer applies.
2. **Apply the criterion to a pinned actual cut.** Authenticate every charged
   path's endpoints and evaluate the lower bill. A nonpositive value can prune
   its full feasible interval. A positive value still leaves native legality,
   ownership, restoration and the complete signed invoice to establish.

Prepared by **apoursh**, with substantial **OpenAI Codex and subagent** assistance
in the proof, implementation and independent checks. Nick Petalas / petalas
supplied PR7331's proper-terminal question and counterexample; unpaidmoon
supplied PR7283's rank-bill formula and earlier endpoint theorem. CubeJerry's
helper-split exploration and DreamingOfClouds's PR6902 two-chain work retain
credit. Concavity and tangent inequalities are classical; no literature-priority
claim is made. New work and retained predecessor prose are Apache-2.0.
