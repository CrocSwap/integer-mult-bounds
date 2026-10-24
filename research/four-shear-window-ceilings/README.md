# Four-shear ceilings for twelve receiver windows

**All twelve windows have certified zero headroom at C=0.00302015. No new kappa.** Assignment B independently covers every word of at most four unit shears on the same three persistent fields and fixed boundaries used by fork PR15. Even a favourable geometric relaxation cannot improve their paid moment. [RESULT.json](RESULT.json) retains the exact source-bound receipt; [VALIDATION.md](VALIDATION.md) records the passing hosted replay.

## Complete alphabet and scope

The twelve generators are y_i += sign*y_j for i != j and sign in {-1,1}. Every word of lengths zero through four is enumerated, including cancellations: 22,621 words. For each of the four sign choices exactly 84 words have the required exact integer 3 by 3 receiver endpoint, comprising two length-two, two length-three and eighty length-four words. No heuristic pruning or floating-point equality is used.

The source has 128 eligible adjacent pairs. Only the explicitly bounded first twelve are tested; all are in phase B. Each has all 84 matching words admitted by the dimension screen. Ten windows have one relaxed paid profile, and the two at indices 10575 and 10579 have four. Every profile's directed gain upper bound is nonpositive; the best is exactly zero. The original path is included, so the optimistic ceiling is attained by the incumbent. This does not cover the other 116 windows or joint changes to overlapping windows.

## Why the relaxation is a valid ceiling

For each endpoint-matching word, propagate mandatory lower subspaces forward. At a contact of fields i,j, every legal common frame contains the sum of their current lower bounds; update both to that sum. Propagate permissible upper subspaces backwards from the fixed exits, replacing both operands' bounds by their intersection. Induction gives L_j contained in F_j contained in U_j for every actual monotone path. If L_j is not contained in U_j, the word is impossible under this contract.

For surviving words, enumerate every integer contact dimension between dim(L_j) and dim(U_j), nondecreasing along each operand's path and bounded by its fixed terminal dimension. Charge each positive entrance/intermediate gap and every remaining exit gap. The sum of charged ranks equals total terminal-minus-entrance rank mass. Forgetting simultaneous incidence constraints can add profiles, never remove a legal one. Thus minimum relaxed paid moment is a lower bound on legal cost, and old cost minus that lower bound is an upper bound on possible gain.

All distinct relaxed profiles are retained. Directed rational intervals bound signed old-minus-new costs, with identical profiles treated as exact equality. The independent power method uses binary-reduced logarithms and an alternating expansion of r*exp(-C log r). Optimistic positive profiles would not establish a construction; here none exists. Individual window gains must never be summed across overlapping operations or shared resources.

## Reproduction and independence

Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/four-shear-window-ceilings
python -I -O -B research/four-shear-window-ceilings/verify.py --self-test
```

The registered source-bound replay passed on CPython 3.12.15, including normal verification, optimised controls and preservation of committed inputs. Seven source files are pinned by Git blob and SHA256. The inherited constructor emits candidate data only; no predecessor proof engine or PR15 acceptance routine is imported. Window extraction, scalar enumeration, relaxation and interval arithmetic are separately implemented. Normal replay compares the full retained receipt without rewriting it. Exact small-domain controls include 68 actual geometric paths plus exit-charge, incompatible-exit and equality checks.

## Task and overlap

Canonical base f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc, priority revision 7; PR4470 source b9a13c1673e0e9697de410de16e8bbf3207a7363. TASK.json records the refined independent-moment assignment. PR4121 uses older T360 sources; #4091's fixed-inventory ceiling is not transferred outside its hypotheses. PR4529/4532/4533 concern compiler gates and ranks. Searches were targeted, not exhaustive overlap pagination or proof of novelty. The historical baseline helper was not run. No selected record or frozen input changed.

## Open next questions

Do not reseed this exact domain. A useful next experiment must change the length cap, coefficient alphabet, adjacency, owned-field allowance or producer/consumer boundary explicitly and reprice the complete contract. Another window is outside the certificate but should have a concrete structural reason for investigation. Physical lowering, full native correctness and consumer transfer remain necessary for any later positive candidate. TASK.json records the next question and blockers.

## Credit

Credit zxv's receiver-sharing and productive-helper work, Cinna Davis's PR4470, Jacob Alan Sussman, GamingPuzzled's earlier finite census and the retained native/Clifford/geometry/outer contributors. Prepared for Chris R / Clear1nsight with substantial OpenAI assistance, Apache-2.0. Separate implementations in one session do not imply separately launched agents, independent human review or formal acceptance.
