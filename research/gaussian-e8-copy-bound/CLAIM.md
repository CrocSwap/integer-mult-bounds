# Sprint claim

- Track: bit supplier; OS-random assignment seed **6** (one-byte rejection sampling).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13 04:46:52 UTC; planned handoff by 06:16 UTC.
- Object: #620's 60 Gaussian E8 lines, scalar binary fitting decoders with
  arbitrary reader/source supports and any number of totals.
- Hypothesis: averaging maximum nonorthogonality-clique rank inequalities
  yields a stronger exact pairing-rank COPY lower bound. Close supports to
  their rational Gaussian spans and exhaust all flat pairs; check independently.
- Deliverable: scoped proof or counterexample, offline exact verifier,
  deterministic certificate, meaningful negative controls and source pins.
  No new kappa or physical supplier is promised.

Three candidates considered: (1) the fixed P111 nine-total decoder basis,
(2) Gaussian/Eisenstein extension-unit pairing-rank bounds, and (3) the
fixed-plan P111 mini-node helper floor. #620 already computes candidate (1).
Candidate (2) directly addresses an open report question, using #703's rank
averaging approach on a different geometry. Seed parity chooses Gaussian
(6 is even); its maximum nonorthogonal clique has 12 ports, compared with
7 for Eisenstein, making its optimistic bound more promising.

Before computation, two orthogonal-root hyperplanes show that averaging
maximum 12-cliques can prove at most 40 Gaussian COPY units. Thus even a
successful certificate will not prove the reported approximately 42.6-unit
threshold needed to exclude this unit as a possible improvement. A stronger
partial lower bound and a precise limitation of the method remain useful.

No pinned sprint coordination issue was available: the open issue search
returned only #650 (requesting Discussions). This claim is therefore local.
Initial overlap review includes current selected #626/#543, #620, #631, #703, #715,
and recent bit circuit/frame work through #720. #703 treats ten quaternionic
lines, while #631/#715 treat real E8 star decoders/punctures. No matching
Gaussian asymmetric COPY-cost contribution was located at that initial check. Claims in unreviewed
PRs are treated as source context, not accepted mathematical conclusions.

Prepared for @chinmayarvind23 with substantial OpenAI Codex assistance.

## Completed result and final overlap update

The completed [proof and review package](README.md) establishes a ceiling of
40 for all nonnegative weighted inclusion-maximal-clique certificates on
the 60 Gaussian E8 lines, attained by the uniform maximum-clique certificate.
Two separate exact implementations reproduce the corresponding copy floor
on all 2,582,128 unordered flat pairs. The actual decoder optimum remains
in [40,60], with no new supplier or kappa claim.

The final overlap refresh found Sagar Thakrar / @thakrarsagar's
[#738](https://github.com/CrocSwap/integer-mult-bounds/pull/738), inspected at
`9671c5d72f3119ba26f3774f40aa7130c67bcf77`. It already reports the same floor,
closure reduction and uniform-weight sharpness. The scope was therefore
reframed as independent verification plus the stronger ceiling for arbitrary
nonnegative weights on inclusion-maximal cliques. Its inspected proof gives
48 for general clique weights; our theorem gives 40 in this specified class.
Non-maximal cliques are outside the extension. Including empty supports
explains the pair-count difference from #738 and is not a new mathematical
domain. No #738 code was imported.

The refresh inspected Gaussian search results and new PR metadata through
#763, including the distinct P111 factorization work in #757/#761. A last
Gaussian search before submission also inspected #767: its planar and
incidence decoder subclass obstructions differ from this maximal-clique
certificate ceiling, and no code or theorem from it is used here. Main and
the inspected #703/#738 heads remained unchanged. The only open issue was
still #650; no separate reservation issue or claim comment was posted.

The 21-case reproducibility and rejection run completed on 2026-10-13 at
05:14:34 UTC; [VALIDATION.md](VALIDATION.md) also records the subsequent
replay of exact staged bytes after manifest line-ending normalization. The experiment
stopped after exhaustive flat-pair and maximal-clique coverage. The remaining
sprint time was used for verification, overlap review and handoff, rather
than further speculative search. The original seed and selected object
were retained.
