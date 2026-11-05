# Post-seal source binding of the marked reversal derivation

Reviewed 2026-11-05 around23:54UTC, after both first drafts were sealed. This is a source-aware cross-review, not a third independent derivation. No source/new machine, constructor, rule enumeration, sampler, census, import, compilation, test, numerical experiment or kernel was executed. Only inert files and metadata hashes/time were read. Existing notes, seals and package files were not edited.

Read source6127 head `116dbe505704a4aca043364b8cff97580990d6dd`, exact retained directory `research/marked-tape-ddg-reversal/`, with these local SHA256 bindings:

- PROOF.md `a182430c3360c6c89daa49141a9233a566fd425d1a869a4686382323c0cdaf19` (source Git5a042f225103a33d7192cdbaa7aa5e9e77d5c4c8).
- machine.py.txt `34be31b9322fffd854ad7fec554762c1c551abebaa61650e83259da25c64db78` (Gitab970cf8ad640fbfdbc9f503bce485ff6750747a).
- verify.py.txt `f3cb2dd82c1c62ad6cf6380b6c6d8bcd32fc0ece0d6c04699917d66a136e447f` (Git5e46534753d890330810c1d3c9e44b2b8df2da01).
- README.md `384a8f2686bd3c40c4d75d6af916367fa186626c8be2393fefaa24f4083c02cc`.
- Peer MARKED-CODE-DRAFT.md `3a534d51f43f59dac24b7790d4dac97fe06e1b36983926219a9c1c888bc72987`.

My abstract first draft remains immutable at SHA256 `4a0b72eecc3db3d4c265d622ab9b1a0f97a690b2a6499cd452fb9777dfdeb8a6`.

## Verdict and phase convention

Qualified PASS: the actual fixed-source local rules bind the abstract marked-path theorem under the source entry invariant and credited6102 predecessor lemma. No source correction is requested. The root/sampling inverse premises remain credited rather than independently re-audited or executed.

One convention must be stated explicitly. My abstract terminal(phi,i) names the PARENT phase phi of the leaf edge. Actual `forward_rules` enters `('back',next_phase,target)`, storing phi+1 modulo156. Its reverse key `('read',next_phase,target),bit,A` recovers the parent phase phi. These annotations are in bijection and give exactly the same inverse relation after the one-step phase shift; the first draft should not be read as asserting literal tuple equality with the source's terminal control.

## Actual rules and reached-path invariant

`build_rules` supplies an ENTRY read on binary s, moves left to PREPARE, writes the owned underscore at s-1 to#, moves right and enters F(0,0). It does not assume a persistent prepared marker for free or overwrite arbitrary protected data. `forward_rules` reads one actual resident coin, moves right, and either enters the next pending F or XORs the leaf into arbitrary A and enters its annotated B in that SAME transition.

`reverse_rules` installs B on binary0/1 as a same-symbol-write left move to R. R on the consumed resident bit follows the actual source edge backwards with zero movement. The sole marker rule is R(0,0) on#, which writes underscore, moves right and returns HALT. Thus the exact reverse invariant B(source state after k, phase k mod156), head s+k, is the one used by the abstract proof. Positive-depth root wraps see a binary predecessor and continue. Only the owned marker ends the rewind.

The first reverse B reads s+T before moving left. Therefore the minimal readable interval is[s-1,s+T], not merely the consumed cells[s,s+T-1]. The source's infinite binary suffix supplies it. This is already an existing source assumption/control: `short_paths` leaves a guard bit, `wrap_paths` appends zero, and `controls` rejects the single-bit fixture without lookahead. It is not a new discovered source defect. The graph consumes only T coins; an ignored lookahead read remains a real physical access.

Only the marker's symbol value changes on the first tape. The literal transition format nevertheless writes a replacement symbol even when equal to the old one, and the observer assigns it on every step. The counted two marker writes are symbol changes, not evidence of compatibility with a hardware capability that forbids same-value writes. Both heads return to their original positions. Finite control returns from ENTRY to the fixed HALT ABI port; it is not restored to ENTRY and no free control reset is inferred.

## One-step partial injectivity is separately justified

The peer's interpretation of `check_local_injectivity` is sound. A resulting control determines the unique incoming displacement d, so the previous head position is current head minus d. The written first-tape symbol is visible at that previous position and the output symbol at its stationary second-tape head. Uniqueness of `(target,written,out)` then selects at most one source rule, recovering the previous control, symbols and head; all other cells were unchanged. Both clauses are required, and this proves one-step injectivity wherever a rule is defined, not totality.

The actual rule families satisfy the structural conditions with the inherited edge premise: PREPARE receives left moves; F receives right moves, with the prepare marker range disjoint from recurrent binary writes at root; leaf B receives right moves and retains the XOR label/phase needed for predecessor uniqueness; internal B receives zero-moving R updates, invertible by forward determinism; R receives left B moves; HALT receives the marker-clearing right move. Internal and leaf B destinations are disjoint by source target identifiers. The finite verifier checks the generated instances, but this cross-review did not enumerate or execute that check.

This global partial-step property is stronger than endpoint injection but still distinct from termination or a full-state total hardware permutation. The path invariant proves successful return for valid entry and finite T. The endpoint on data is `(x,A)->(x,A XOR i(x))`, with original tape/owned blank restored. The transcript is still part of the data that makes this map injective. Arbitrary ambient/output correlations are allowed pointwise; symbol restoration does not make the transcript conditionally fresh or permit a new independent sample from the same prefix.

## Limits, observer and credit

The observer's head coordinates, fixture lengths, max_steps and saved initial tape are outside the finite rule key. Its caps are test limits, not a hidden stopping counter or all-path bound. The source's tariffs and controller/rule inventory remain original results. This note associates rule families with their written path semantics; it does not execute or independently rediscover3T+4,2T+4, finite counts, wrap fixtures or the source mean.

The peer first draft accurately distinguishes same-symbol writes, lookahead, ENTRY→HALT, source control intentions, reached endpoint and global partial-step injection. No forward shared quotient, global freshness, constant total resident space, physical binary lowering, actual caller ownership layout, native invoice or all-five selected admission follows. Source6072 sampling/mean and6102 phase/coin inverse remain premises with their credit. Nick Petalas6127 retains the actual marked-machine construction and resource theorem; all original notices, caller/reversal lineage and AI-assistance disclosures remain. No public action, source edit, κ/frontier/adoption change or human/kernel acceptance is requested or implied.
