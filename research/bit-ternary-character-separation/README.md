# A ternary cut beyond bounded dyadic counting screens

An exact eight-call candidate for three invertible 3-by-3 targets passes every
rational projection/rank cut, determinant equality, all 64 binary characters
of its generated lattice and all 4,096 order-four counting cuts. A ternary
character retains only one paid call against three target roles. This rejects every call order
and any finite number of restored dirty scalar roles in the stated formal
abelian model.

A scaling family passes every dyadic nonzero-label counting cut through any
prescribed finite order, while retaining the ternary rejection. One fixed
diagonal eight-factor word also realizes the full endpoint in each covered
quotient H/(4^s H). The contribution is this separating family, its written
[proof](PROOF.md), and an independent replay. The projection/rank
method is inherited. This is a pre-search rejection, not a new register model,
successful circuit, supplier or kappa improvement. The selected result remains
unchanged.

## Evidence and reproduction

[EXAMPLE.json](EXAMPLE.json) contains the eight paid frames and three targets.
[LATTICE.json](LATTICE.json) certifies their actual generated lattice in both
directions with integer coefficients. [RESULT.json](RESULT.json) records the
exact determinants, all character margins and the rejection witness.

From the repository root, Python 3.12 or later, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/bit-ternary-character-separation
python3.12 -I -O -B research/bit-ternary-character-separation/verify.py
python3.12 -B -m unittest discover -s research/bit-ternary-character-separation -p 'test_*.py' -v
```

Expected direct replay:

```text
PASS_TERNARY_CHARACTER_SEPARATION rational_subsets=28 binary=64 order4=4096 ternary=729 cut=1<3 projectors=120 no_new_kappa
```

The replay takes under a second locally. It checks all 28 independent
six-frame subsets, target determinants 5184, 576 and 25524, exact lattice
membership, determinant equality, 64 binary, 4,096 order-four and 729 ternary
characters. The witness is X_11 modulo three, with paid residues
`(1,0,0,0,0,0,0,0)` and target residues `(1,1,2)`. Exactly two ternary
characters violate, each with margin -2; no binary character violates.

Seven test groups include independent Leibniz minors, image-code character
enumeration, polynomial verification of F4 arithmetic, false saturated-lattice
and malformed-input controls, relocated normal/optimized CLI execution,
read-only checks and corrupted receipts. Four actual implementation mutants
must fail before receipt comparison: reducing ternary values modulo two,
counting only residue one, omitting a call from the positive word, and assigning
a projected factor to the wrong scalar role. The replay also checks the
family's determinant formulas and exact quotient word for s=1,...,16.
The field check covers all 120 four-role binary rank-one idempotents and a
direct nine-call positive word in both forward and reverse orders, with a
fourth dirty role restored. These controls support the universal written proof;
they do not exhaust arbitrary-role words.

Normal replay writes nothing. `verify.py --write` regenerates only RESULT.json.
The registered replay also runs the behavioral tests and checks the pinned
source documents. Direct replay uses only this package, importing no predecessor
implementation. This fixed witness checker is not a general candidate-search CLI.

Build the Lever led to the retained replay and exact lattice certificate.
Prove It Works led to separate determinant/code oracles and actual implementation
mutants. Power of Ten kept the checker bounded and its contracts active under
Python optimization.

## Scope and current handoff

Base main is `95ff4e2dd396c505932a43ff7c1cdfdd94b8c867`, priority revision 5.
The chooser suggested `bit-new-register-model`; this task changes scope from
constructing a new alphabet to the explicit unequal-class screening handoff in
pending [PR2938](https://github.com/CrocSwap/integer-mult-bounds/pull/2938), pinned
at `050aa9f623d180a08b36a375c30004d060d480d5`. Its code is not a dependency.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2898#discussioncomment-18974717)
records this bounded task. Metadata searches cover PR bodies and Discussions,
not every diff or external result; no claim of general novelty follows from them.

The written proof rejects the displayed scaling family. It does not classify all
unequal-class targets or establish independence from every other cyclic or
algebraic obstruction. General rank-one increment arguments and cyclic quotient
methods already exist in the retained sources. The advance is the exact
separation from rational cuts, determinant equality and any prescribed finite
range of dyadic nonzero-label counting cuts. The initial unscaled probe also
failed an order-four cut; the revised family addresses that covered case.

No full predecessor or selected cold replay, proof-assistant check, physical
word, native realization, all-size compiler, hosting, precision/tape or completed
supplier moment was run. The covered quotient identity does not give a full-H
word or a native-address program. The result has an independent internal mathematical
check; independent human and formal-kernel review remain separate.

## Open next questions

Can a concrete unequal-class eight-call candidate pass these ternary cuts as
well as rational, determinant and parity screens? Retain its exact generated
lattice and targets first, then evaluate the complete character families before
searching the scalar-role domain from mixed-target compression. Such a candidate
and its completed native consumer bill are missing. Passing these necessary
screens would still not justify supplier admission or a larger construction
campaign. [TASK.json](TASK.json) records this same question and stopping rule.

## Credit and implementation limits

Nick Petalas. Apache-2.0. The projection/register and rational rank-cut lineage
includes Ali Romman, eumemic/PR288 and huxint/PR203. Tuafo's augmentation argument
and the retained mixed-target compression motivate the dirty-role contract.
PR2938 supplies the generated-lattice binary-cut comparison and immediate
handoff. The retained dyadic-ternary catalyst, cyclic-root barrier and faithful
finite-address work supply related character and cyclic-quotient context.
Predecessor files and notices remain unchanged. Exact source pins and pending
context are in SOURCES.json and TASK.json. Substantial AI assistance was used for
analysis, implementation and checks; no independent human review is claimed.

The Power of Ten inspection covers verify.py and test_verify.py. Input files
are limited to 65,536 bytes. The witness has exactly eight paid frames, three
targets and six lattice basis rows, with 64-bit integer entries. All loops
have fixed bounds or bounds from these shapes: 28 subsets, 64/4,096/729 characters,
225 projector pairs, two nine-call words, 16 family formula/quotient cases,
and 720 permutations per independent minor. Rank elimination uses at most eight
rows and nine columns. The tests
use only bounded local fixtures and sequential subprocesses with 30-second
timeouts. Every function is shorter than 60 physical lines. Explicit contracts
remain enabled under optimization; there is no recursion or generated code.

Rule 3 deviation: Python and Fraction allocate at runtime. Fixed shapes and
entry capacities bound live collections and integer arithmetic in this short
research command; the registered commands have 120-second timeouts. A fixed
memory implementation would be needed for a steady service. Rule 9 deviation:
unittest uses fixed method dispatch, the tests import one local module, and
temporary copies run only that module with the current interpreter. The
subprocess results are checked and temporary directories are closed on every
exit. Rule 10 uses Ruff diagnostics and warning-as-error compilation in addition
to registered replay. No shared runtime or predecessor refactor is needed.
