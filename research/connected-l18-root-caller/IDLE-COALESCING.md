# Exact optimum of the optimistic L18 same-role idle-coalescing relaxation

Scope: the 38 independent root fields and 18 stage masks in `root_L18.json`, bound to `caller_L18.json` by exact masks and SHA-256 in `idle_coalescing.py`. No new native word or kappa is claimed. This closes only the proposed native profile plus coalescing-only repair at the stated comparison point. A cheaper native, changed root, changed role encoding, changed idle count, or arbitrary noncoordinate shared-direction decomposition is outside the result. Actual rank-one idle bases may rotate; this theorem does not constrain all such rotations.

The masks contain 217 role/stage incidences. At each stage arbitrarily choose any two eligible mask-coordinate roles as hosts, leaving exactly 181 idle incidences. No actual host-position restrictions are imposed. For each role r, coalesce ALL its idle incidences, even across actual chronological barriers, into one paid rank `8 d_r` child for free, where d_r is its idle degree. Do not combine independent roles. At k=0.00362701882 the relaxed cost is sum_r f(d_r), with f(d)=(8d)^(1-k), f(0)=0. All root targets, three thin jobs, 18 HOSTs, and proposed native cost remain fixed. Coalescing setup, uncomputation, chronology and ordinary costs are free.

## Compression proves the exact optimum

Let E_r be the set of stages where role r is eligible, and I_r subset E_r its idle stages. Every stage has exactly its mask size minus two idle roles.

If E_j is a strict subset of E_i, replace I_i by I_i union I_j and I_j by I_i intersection I_j. The new sets are eligible. At every stage the total number of idle roles stays unchanged. Their sizes have the same sum as before, with the union at least as large as either old size and the intersection at most as large. Concavity of f makes their total cost nonincreasing.

Whenever I_j was not already contained in I_i, this operation strictly increases the finite integer potential sum_r |E_r| |I_r|: precisely |I_j minus I_i|(|E_i|-|E_j|)>0. Repeated compression therefore terminates. Some optimum satisfies I_j subset I_i for every strict eligibility inclusion.

The two host roles at a stage must consequently be closed downwards under strict eligibility inclusion: if i is hosted and E_j is a strict subset of E_i, every eligible j must also be hosted. The checker enumerates all two-element subsets of each mask under this exact condition. Seventeen stages have a unique allowed pair. The bridge stage has exactly two:

- hosts {16,37}, giving idle degrees (1,3) on roles (16,19);
- hosts {19,37}, giving degrees (2,2) there.

All other degrees agree. Concavity gives f(1)+f(3)<=2f(2), so the first case is optimal. This proves the finite relaxation's optimum without trusting a solver.

The optimal host pairs in stage order are:

[2,3], [5,6], [8,9], [8,9], [11,12], [14,15], [14,15], [17,18], [16,37], [20,21], [20,21], [23,24], [26,27], [26,27], [29,30], [32,33], [32,33], [35,36].

The optimal degree vector in role order 0..37 is:

[18,9,7,7,8,6,6,7,4,4,5,3,3,4,1,1,1,0,0,3,0,0,4,2,2,6,3,3,7,5,5,9,6,6,10,8,8,0].

The degree histogram is {0:5, 1:3, 2:2, 3:5, 4:4, 5:3, 6:5, 7:4, 8:3, 9:2, 10:1, 18:1}. Thus the coalesced paid ranks are 8 times these degrees, with zero-degree roles omitted.

## Full bill at the assigned gate

The maximum idle saving over 181 separate H8 jobs is enclosed by exact rational arithmetic in [9.70728992517695569956124850500966948053128943, 9.70728992517695569956124850500966948053400299].

The required saving is computed directly from the pinned F profile plus H1, all eighteen native calls, the caller targets and all nonnative jobs. Exact rational intervals give a requirement greater than10.08182803487564 and a strict shortfall greater than0.37453810969868 per port, before ordinary and outer margins. The best coalesced native gate is below17.6706347875832 per stage. This is not a general root, fusion or native ceiling.

Ignoring stage eligibility would give an apparent saving of 10.765030666707, enough to pass. Therefore degree caps alone do not establish the negative result; incidence constraints are essential.

## Pins and reproduction

Root SHA-256: be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34.
Caller SHA-256: f4090329f219edd493b4ca592128521e867a355fb528556b15201e759783568b.

Run `python3 -I -O -B idle_coalescing.py` from the package directory, or pass `--package-root PATH`. An optional `--receipt PATH` compares a retained JSON receipt without writing it. Standard library only; it imports no solver or producer, verifies hashes and caller/root masks, checks the 17+2 compressed assignment census, and computes rational enclosures. Logarithms use the positive atanh series with geometric tail bound after reduction to z<=1/3. Exponentials use odd/even alternating Taylor sums for exp(-x), x<1. No floating-point solver output is trusted.

Three controls actively reject an ineligible host, one deleted real idle incidence (via the per-stage incidence validator), and an eligible but non-downward-closed hostset (via the compressed-assignment validator). A separate scope control confirms that the looser degree-only relaxation incorrectly leaves this route open. The exploratory MILP files are not proof dependencies.

The portable checker also binds `inputs/base_invoice.json` by SHA-256
87a41b13bdd9248d538805f76a970f51335567845dfc0070698b6979a08b70d6.
It derives the required saving directly as 18*((local_paid-helpers)/104+1)
minus the caller target moment plus 181 H8+3 H1, using rational intervals.
The result is greater than 10.08182803487564 and yields a shortfall greater
than 0.37453810969868. Ordinary and outer charges remain omitted in this
favorable necessary screen; they cannot rescue the failed inequality.
The F invoice is the retained source profile reviewed in NATIVE.md, not an
emitted or authenticated F-to-HOST conversion word. The base native is
attributed to PR #6824, retained by PR #6833 head
51f54e3c31f2f3a3e056a483b3ed66ae916ad06a and copied through #6936.
