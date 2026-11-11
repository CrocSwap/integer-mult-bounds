# Arbitrary-slot single-role BIT idle fusion

**NO VERIFIED GAIN. Conditional κ change 0%.** On the exact #7001
paired E-free caller, every pair of disjoint-mask IDLE_ONE events
requires a rank-two correction after deletion. One one-role idle
changes the scalar operator by rank at most one, at any clock.
The complete 256-pair scope has zero compatible savings. The
fixed target κ = 0.0040075385047236 remains short by about
60.10389921914735 raw units. #7277 at κ = 0.003645669928698 remains
the complete comparable witness.

## Rank certificate

Fix one 38-role port group and specialize the formal caller at
q=1 and nonzero body symbols in a finite extension of F₂. Write
the operator around two idle events as L D_j M D_i R, with M
the intervening word and L,R the unchanged outer words. Deleting
both idles leaves L M R. The difference after inserting one
one-role diagonal idle anywhere in the deleted word is of the
form A(D−I)B. Its rank is at most one at every specialization.

For original idle factors D_i = I + α e_r e_r^T and
D_j = I + β e_s e_s^T, take off-axis entries
l = (M e_r)_u ≠ 0 with u ≠ s and
h = (e_s^T M)_v ≠ 0 with v ≠ r. The inner difference
D_j M D_i − M on rows (u,s) and columns (r,v) has determinant
αβlh. All 256 disjoint pairs have such a nonzero minor in
GF(128), with nonzero idle corrections. The outside factors
L,R are invertible at the probe because each stage scalar is
nonzero and every remaining shear or swap is invertible.
The exact symbolic equality required by a replacement would
survive this specialization. A direct whole-operator replay
over a different GF(256) specialization also finds rank two
for all 256 pairs.

The disjoint stock is exhaustive within this scope. The 240
overlapping-mask pairs, additional ordinary edits, changes to
other caller factors, and a genuinely multi-role child are
outside it. No physical site is tested.

## Whole signed price

There are 32 literal IDLE_ONE events, each repeated over 111
port groups, giving 444 paid jobs at each rank 7,14,…,56.
Write H(r)=r^(1−κ). Concavity gives
H(a+b) ≥ H(2)(H(a)+H(b))/2. Even granting every compatible
rank-additive pair free setup and routing, the disjoint-pair
saving upper is about 305.93670924546 before support. The rank
obstruction then reduces the declared stock upper to exactly
zero. The independent verifier reconstructs the 36-copy bill
of 107,352 paid and 19,950 productive jobs, authenticates all
62,474 native contact incidences and rejects a missing paid
MOVE and a missing original idle.

## Reproduction

Use CPython 3.12 with assertions. From a clean checkout:

    python3.12 -B scripts/research_package.py --package research/bit-single-role-idle-rank-bound
    python3.12 -B scripts/check_research_commit.py --package research/bit-single-role-idle-rank-bound --check-modes --check-source-history

From a Git-free official export root:

    python3.12 -I -B research/bit-single-role-idle-rank-bound/replay.py --root .

The exact caller, native word and signed receipt are declared
by stable source path with Git blob and SHA-256 pins. Duplicate
JSON and source-path controls reject. The replay needs no prior
temporary state, external interpreter path or network.

## Open next questions

Can one charged two-role child supply the necessary rank-two
correction while preserving both arbitrary-input fields? First
reprice the compatible paid stock including extra ordinary
operators, ownership and restoration. Then check one exact
signed native prototype only if the total can reach the target.

Credit #7001 and #6726 for the retained exact inputs, #6834
and #6980 for the caller lineage, and #7277 for the complete
comparison. #7163 concerns native full-fibre reflection volume,
and #7190 and #7201 treat equal-mask alignment and cover
assumptions. They are different from the fixed remaining
caller and disjoint masks used here. OpenAI Codex and subagents
materially assisted.
