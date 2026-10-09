PR69 balanced coarse sums + PR71 anchored split: completed finite checkpoint

Both axes are complete and independently checked. This compatible composition
improves PR73's finite conditional bound, but does not surpass public PR76.
No PR76 graph/scheduler composition was run in this experiment.

Selected results

                         PR71/73              balanced + split
h23 roles                 27,455                 27,338
h25 roles                 36,015                 35,942
h23 scalar additions      68,771                 67,460
h25 scalar additions      96,718                 94,993
h23 literal L XORs       162,103                161,763
h25 literal L XORs       225,757                227,097
complete width W     135,075,665            134,677,282

m = 575; total recursive rank = 77,437,590,250 = 575 W - 1,846,900.
The width still needs 28 role bits. Fewer additions or roles alone was not
used to accept the construction; actual child profiles decide the comparison.

The exact accepted bit saving is
    a = 51547482808051 / 10^18.
The adjacent larger point at denominator 10^18 is rejected. Using backoff
h=10^-18, all 47 strict assembly inequalities and seven margins yield
    kappa = 51544825802029 / 10^18 = 0.000051544825802029.
The adjacent larger kappa grid point is rejected by the assembly checker.
The gain over PR73 is 26035939567 / 200000000000000000, about 0.2531957481%.
The difference from PR76's reported/reproduced kappa is
    -1.93850243112e-7.
Thus this package is a verified composition result, not a new public frontier.

Verification

Each complete serialized word was independently replayed over every input,
output and arbitrary-dirty auxiliary basis coordinate in both algebraic
orientations (30,880 coordinates at h23; 40,542 at h25). Every local incidence
and output contract passes. A separate strict check binds the literal scatter
sequence to the complete output records, closing the inherited replay's
scatter-binding gap. Actual transition multisets are independently rederived
from the saved XOR word and compared with the compiler events.

Fresh fixed-basis CRT profiling checks 5,513 special matrices at h23 and
7,422 at h25, with zero modular disagreements; inherited bounded-minor
inequalities are checked too. Complete profiles include both exterior
classes, both data-growth classes, all fixed data-corner charges, retained
center copies and the final paid endpoint copy. Each individual-axis hybrid
already has a strictly lower characteristic at the exact PR73 saving:
approximately -4.0400921542e-8 for h23 and -1.9763587274e-8 for h25.
The both-axis certificate reconstructs the full paid profile and compares
against both PR73 and PR76 using directed rational enclosures and a separate
inherited arithmetic evaluator. arithmetic-review.txt is an additional narrow
read-only source review, not another word/CRT rerun.

Schema for offline arithmetic review: combined-comparison.json.
Its profile contains m, W, total_rank, child_multiplicities and all parts;
bit_saving, accepted_moment, rejected_moment and independent_enclosures record
the characteristic check. finite_bridge, backoff, preferred and kappa contain
the conditional balanced assembly. inputs binds both fresh profiles, local
comparison receipts and raw word hashes. frontier_comparison is explicitly a
comparison-only public PR76 reference, whose exact source pin/path/hash is
recorded in pr76-frontier-source.json.

Source and proof scope

The unchanged upstream checkout is PR73 commit
253ecc88faeed55a950c76026d1fe67a7f690123, preserving PR71's anchored [1,1,2]
producer. The single guarded in-memory source replacement is literally the
PR69 balanced coarse-sum transformation at commit
91aa1f17e6e3fc063241686a41a34ddd0dc24c50. Source closures, exact fragment hashes,
generator receipts and compressed/raw word hashes are recorded. Original
upstream files and earlier proof bundles were not changed.

See compatibility.txt for the source-level proof: balanced columns sum exactly
the same disjoint cross-group supports under any permitted split partition;
all new intermediate envelopes keep the common point. The compiled finite
word checks, rather than this argument alone, certify selected carrier reuse.

This is a finite conditional witness. There is no new real-power Lean
certificate for these literal profiles, and no new complete ambient physical
frame-trace replay for these words. The independently checked scalar words
and local transition profiles are combined with the inherited fixed
data/exterior/copy profile facts and unchanged framing equations. All-size
residual compilation, physical stream/tape costs, routing, prime selection,
recovery and analytic transfer remain the explicitly inherited contracts.
It is not a full machine proof, global optimum or practical speed claim.
The compiler's paid_clones=0 means no extra optimizer-added clones; mandatory
h retained-center copies remain included in all profile charges.

Reproduction

Use assert-enabled Python >=3.10 and a C++17 compiler. UPSTREAM must be a clean
checkout of the exact PR73 commit above from
https://github.com/CrocSwap/integer-mult-bounds. From this package directory:

python3 balanced_split.py --upstream "$UPSTREAM" --h 23 --output build/candidate --compile
python3 balanced_split.py --upstream "$UPSTREAM" --h 25 --output build/candidate --compile
python3 verify_balanced_split.py --upstream "$UPSTREAM" --h 23 --candidate build/candidate --output build/verification
python3 verify_balanced_split.py --upstream "$UPSTREAM" --h 25 --candidate build/candidate --output build/verification
python3 compare_completed.py --upstream "$UPSTREAM" --verification build/verification --frontier pr76-frontier-reference.json --output build/combined-comparison.json

To validate the supplied words without rerunning discovery, replace
--candidate build/candidate by --candidate candidate in the two verifier
commands. To independently recompute only the exact combined arithmetic:

python3 compare_completed.py --upstream "$UPSTREAM" --verification verification --frontier pr76-frontier-reference.json --output build/combined-comparison.json

Create build/ before the arithmetic-only command. Compilation took about
223 seconds at h23 and 343 seconds at h25 on the discovery machine. These are
reproduction observations, not an integer-multiplication speed measurement.
The output bundle includes logs; the PR publication omits logs, executables
and caches. Integrity manifests bind the respective included files.
