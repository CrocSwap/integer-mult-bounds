# Paired concentration of PR2857's rank-nine residues

**Publication status:** this verified gain over pinned PR2857 was superseded
in reported conditional kappa by pending [PR2863](https://github.com/CrocSwap/integer-mult-bounds/pull/2863),
head `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`, before this submission.
Its reported T185 saving is `0.001720100805416885927944 - 10^-46 - 10^-70`.
This package preserves the simpler T74 construction, separate checker implementations,
full replay evidence and bounded negative search; it makes no current-record claim.
PR2863's full certificate was not reproduced here. See `PUBLICATION-REFRESH.json`.

This scoped derivative of PR2857 interleaves two copies of its T37 allocation
and moves one width-seven helper. The complete profile changes by
`H2 + H16 - 2H9` relative to the doubled original. The local words are unchanged.

The exact conditional integer-multiplication exponent saving is

```
kappa = 0.001720097402339781716060 - 10^-46 - 10^-70
```

Against the pinned PR2857 construction at
`0b2e2537b368a0cade07ce3f71452ea018ebe394`, the exact improvement is
`48353434319693/62500000000000000000000 = 7.73654949115088e-10`.
See `CLAIM.json` for the complete rational and decimal. This is an exponent
saving, not a measured speedup. It is author-checked conditional finite evidence,
not maintainer acceptance or a formal complete multiplication theorem.

## What changes

A source call at time t is duplicated at times 2t and 2t+1 with replica offset
37. In the resulting T74 allocation, helper 297 of call 658 moves from
`[owner=35,child=16,port=37,offset=0]` to
`[owner=72,child=16,port=37,offset=7]`. The two bins' idle ranks change from
9,9 to 16,2. Strict concavity proves the recurrence price decreases for every
`0<a<1`; the actual chronology, family exclusion, capacities and all 271,728
roles are independently checked. `PROOF.md` gives the construction, count,
recurrence argument and retained conditional obligations.

The complete derived profile is
`{1:1611720,2:427573,3:183550,4:85248,5:26196,8:5328,16:1,48:26758}`.
The source and derivative have respectively 333 and 666 calls; their live stock
is 33,152 and 66,304. The derivative's physical stock is 66,794. The unchanged
block norm admission prices T74's prefix, precision and private-buffer costs.

## Reproduce

The bounded standard-library check uses committed pinned inputs, regenerates
all allocation payloads, checks chronology independently, encloses the exact
moment, and runs source/owner/endpoint corruption controls:

```sh
python3 -B scripts/research_package.py --package research/shared-kernel-pair-concentration --check-only
python3.12 -B scripts/research_package.py --package research/shared-kernel-pair-concentration
```

For a full reproduction, use an isolated environment and the pinned requirements:

```sh
python3.12 -m venv /tmp/integer-mult-pair-venv
/tmp/integer-mult-pair-venv/bin/python -m pip install -r research/shared-kernel-pair-concentration/requirements-reproduction.txt
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git 0b2e2537b368a0cade07ce3f71452ea018ebe394 e9307b48d7d1b690939935ecef0f8e524e6d92f4
/tmp/integer-mult-pair-venv/bin/python -B research/shared-kernel-pair-concentration/reproduce.py --repo "$PWD" --work /tmp/integer-mult-pair-fresh --jobs 2
```

The work path must not exist. The wrapper exports and authenticates the entire
pinned PR2857 source tree, reproduces its complete documented release, generates
this allocation, performs independent checks, and invokes PR2857's unchanged
complete admission adapter. Discovery is followed by a frozen strict release.
The final binding additionally compares the full rational against the reproduced
PR2857 headline; the inherited adapter's historical comparator is PR2848.

The baseline replay freshly runs both current native chains. The candidate
reuses those exact authenticated unchanged words and native outputs. Two older
native chains and the retained parent proof use PR2857's explicit source-bound
cache. This is not a cold replay of every historical predecessor. The initial
PR2853 baseline in this session did run all four native chains fresh.

`evidence/` contains executed receipts, source manifests, control counts and
command logs. `EXPERIMENTS.md` records failed and superseded approaches.
Repository-wide `make verify` and selected `make frontier1094-verify` were also
run on pinned initial and refreshed main. Both failed on the unmodified tested base; `REPOSITORY-CHECKS.md` records the exact blockers. No check was weakened.

## Frontier and scope

`FRONTIER.json` separates the reviewed main selected record from pending
constructions and numerical targets at the research checkpoint;
`PUBLICATION-REFRESH.json` records the newer pre-submission comparison. The new
result remains dependent on pending PR2857 and its inherited lineage. The census
was paginated directly from GitHub; detailed review/check coverage is listed
explicitly and is not represented as a complete audit of every open PR.

The all-size compiler, common-label/mutable-source, whole-call hosting,
precision/tape, exact-recovery, analytic-transfer, corrected recurrence and
bit H1–H5 assumptions remain. See `PROOF.md`. No selected record or frozen
predecessor is changed.

## Open next questions

See the structured questions in `TASK.json`. The former question about the
remaining fixed-inventory gap is superseded by PR2863's claimed exact packing
optimum. Independently reproduce that witness and its scoped primal/dual before
any further packing search. There is no evidence here for a further gain from
same-call pair swaps. Further research should address a named inherited all-size
obligation or change the local contract with all consumer and restoration costs
included.

## Credit

The construction directly reuses Yiyang (@Lyy-iiis)'s PR2857 shared kernels,
owner allocation and complete transport. Jeremy Kothe supplied the PR2833 word
lineage. Philippe Van Velzen's concurrent PR2853 inspired and was the first
baseline for this run; Marius-Paul Dumitrean's PR2856 vacancy-relay work was
read before this paired-residue construction and is closely related in method.
Marius-Paul also contributed the PR2843 allocation lineage; Dugongue supplied
the PR2839 block norm interface; Tekalign contributed native/admission tools.
The outer lineage includes Vlado Vojdanovski, Chafik Boukhalfa, dataisfire,
DreamingOfClouds, eumemic and all contributors credited in the retained NOTICEs.
No exclusive priority claim is made for vacancy concentration or helper choice.

Substantial OpenAI Codex assistance was used for research, implementation,
independent checker implementations, exact computation and packaging. These
are separate code implementations, not independent human review. Apache-2.0;
source licenses and notices are retained.
