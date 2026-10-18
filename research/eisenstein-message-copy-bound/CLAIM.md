# Sprint claim

- Track: structural decoder research. OS-random assignment seed: **41**.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13 05:47:37 UTC. Budget: 50 minutes; verification begins by 06:25 UTC. Expected finish: 06:37 UTC.
- Object: the 40-line Eisenstein E8 (Witting) decoder geometry in GamingPuzzled PR #620, with arbitrary scalar binary totals and the source/reader pairing-rank copy charge.
- Hypothesis: a weighted nonorthogonality-clique certificate gives a useful unconditional finite copy-cost lower bound without a full-rank-total assumption.
- Method: independently reconstruct exact rational geometry; enumerate geometric flats and all maximum cliques; check a rational uniform weight over every flat pair. Stop after this finite domain, whether or not the bound helps.
- Deliverable: one scoped research note with proof, source pins, portable exact checker, certificate and negative controls; no new kappa claim.

## Selection and overlap

Three candidates considered: (0) vector-valued full-E8 decoder factors; (1) mixed-port E8 extensions; (2) the Eisenstein extension geometry. Seed 41 modulo 3 selects candidate 2. Candidate 0 is close to #765 tensor-basis work; candidate 1 overlaps #715. Candidate 2 changes geometry from the Gaussian #738/#770 and Hurwitz #703/#785 certificates and answers an explicitly unresolved #620 copy-cost question. It does not repeat the predecessor CP-SAT search.

GitHub reported no pinned issues, and the only open issue was #650 (Discussions). No separate reservation issue was opened. The local claim is used instead. Open PR metadata was checked through #796 (615 open PRs), including #620, #634, #703, #738, #761, #765 and #770. #620's reported Eisenstein lower bound is 9 and its feasible symmetric cost is 40; the search was not certified optimal. The ledger marks #620 partially reviewed and #446 unreviewed.

At the exact starting base, the selected accepted conditional result was #626 with #543, kappa = 51110230636731/31250000000000000. Larger pending titles are not treated as accepted.

## Evidence-driven pivot

At the first experiment refresh, new PR #798 (Jonathan Lam, head `0aea3382e49abd9a59d3cb6676cdb26fd15b04e5`) already supplied the scalar Eisenstein bound and clique-method optimum. Our independent exact geometry replay had found all 772 flats, 2,880 maximum cliques and the uniform maximum-clique floor 280/13. That scalar investigation will not be submitted as new.

The revised scope is fixed-support, deterministic, zero-error nonlinear messages and arbitrary finite bit widths on the same 40 Eisenstein lines. We will check an exact weighted demand bound by combining the #798 geometric inequality with the conditional-transcript argument of #785 (Hurwitz). The deliverable must explicitly price each message by its bit width times source/reader pairing rank, distinguish this model premise from a physical-circuit theorem, and test nonlinear and side-information boundary examples. No second pivot is planned.

## Result update

Completed 2026-10-13 06:16 UTC: submitted one research-note PR, [#814](https://github.com/CrocSwap/integer-mult-bounds/pull/814). Construction/proof commit: `f916c8b20060706bcc50a931a8138bab998aa0de`.

- Result: fixed-support, deterministic, zero-error nonlinear messages on the 40 Eisenstein E8 lines obey C >= 22b for equal b-bit demands, with additive width-times-pairing-rank pricing. Unequal demands obey the weighted 11/20 sum bound and the maximum clique-demand bound. The physical pricing premise is explicit. No new kappa or supplier is claimed.
- Complete geometric coverage: all 772 flats, 298,378 unordered flat pairs, 30,880 line extensions and 2,970 maximal cliques. Stopping rule: exhaust that finite domain and the declared message controls, then package one result. No incompleteness or timeout is presented as an impossibility theorem.
- New evidence beyond #798/#785: the Eisenstein nonlinear and unequal-demand composition; 4,096 nonlinear inputs and 303,104 conditional transcripts; unequal-width and side-information boundary examples; exact reconstruction and a separate modular/Fraction arithmetic checker. The geometric scalar result and transcript method retain predecessor credit.
- Validation: both implementations pass on CPython 3.14.4 and 3.12.13; 12 rejection controls, relocation, source/certificate tampering, output preservation, committed-byte equality and selected-record integrity pass. Structured autoreview reports no actionable findings. See VALIDATION.md for exact scope and commands.
- Final pre-submission refresh: 625 open PRs through #812; #798 and #785 remain at their pinned heads. New #801 is a distinct format-ceiling/coordinate-total note. No pinned coordination issue exists; no reservation issue was opened. This is the single result update to the local claim.
- Upstream advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261` and selected #741 at kappa 1661202643272239/1000000000000000000. Its review was read. All pinned base geometry files remain byte-identical. The contribution retains its exact starting base and changes no selected or upstream file.

Reproduce (Python 3.10+): `python3 -B research/eisenstein-message-copy-bound/verify.py`. Expected prefix: `PASS_EISENSTEIN_MESSAGE_BOUND`. Prepared by Michael Fischler (@shiftybitshiftr) with substantial OpenAI Codex assistance; Apache-2.0.
