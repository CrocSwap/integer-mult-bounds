# R439 compensation with coupled helper triples

**Finite bit-circuit construction; no new kappa.** Replacing 40 disjoint
PR926 helper pairs and 40 unused helpers by coupled three-helper bases saves
**140 further ADDs**, including every preparation and restoration operation.
The complete local word has **11,840 ADDs**, versus 11,980 in PR926,
13,208 in PR915 and 24,305 in selected bit source PR589.

The selected conditional bound at this contribution's base remains
`1661957774647029/10^18 = 0.001661957774647029`, from PR890 with PR589.
This package does not replace that selection or claim a multiplication
runtime improvement.

| Exact quantity | PR926 | Helper triples |
|---|---:|---:|
| Helper preparation / restoration, each | 192 | 234 |
| Target preparation / restoration, each | 306 | 306 |
| Middle injections | 4,764 | 4,540 |
| Complete D ADDs | 5,760 | 5,620 |
| Complete local ADDs | 11,980 | 11,840 |
| Forward positive maximum F | 71,907 | 72,399 |
| Reverse positive maximum B | 10,562,318 | 10,464,656 |
| Local expression bit length | 102 | 102 |
| Nine-stage expression bit length | 192 | 192 |

Thus the complete prefix bill is **234 + 306 + 4,540 + 306 + 234 = 5,620**.
The unchanged suffix costs 6,220 ADDs. The 40 replacements consist of 38
two-ADD preparations and two three-ADD preparations. The other 152 helper
pairs remain in place. No scratch helper, source access, MOVE path,
COPY/ERASE, frame, copied total or recursive child is added. All non-D
fields of the word remain identical to PR589; native replay checks the
exported resource equality separately.

## Reproduce

From the repository root, with Python 3.12+, a C++17 compiler and Boost:

```sh
python3 -I -B research/r439-helper-triples/verify.py
```

For a nonstandard Boost installation, set `BOOST_INCLUDE` to its include
root. Set `CXX` if needed. The final line is:

```text
PASS_R439_HELPER_TRIPLES_FINITE: 11,980 -> 11,840 ADDs; 40 helper triples; no new kappa
```

The command regenerates the complete search certificate and canonical word,
checks them independently, runs the owning E8/frame/interface checks,
compiles unchanged native checkers and tests the original, PR915 and new
words at 5, 9 and 11 stages. The complete report must equal `EXPECTED.json`.
Use `--output NEW_DIRECTORY` to retain logs and all generated evidence.
`--python-only` explicitly produces partial evidence with a different status.
`--record` creates a previously absent expected receipt and never overwrites
one; it is for initial artifact generation, not ordinary verification.

The isolated standard-library discovery command is:

```sh
python3 -I -B research/r439-helper-triples/search.py --output /tmp/new-r439-triple-search
```

It reproduces `CERTIFICATE.json` and `candidate.json.gz`; gzip payloads are
compared canonically, not by regenerated compression bytes.

## Bounded experiment and independent evidence

Assignment seed **12** came from operating-system randomness. The claim and
three considered tasks are in `CLAIM.json`. With the PR915 target basis
fixed, the domain is every one of PR926's **192 pairs**, each of its **55
unused helpers**, and all **168 elements of GL(3,2)**: **1,774,080 scores**.
Breadth-first search nominates one shortest chronological CNOT word for
each matrix; seed 12 orders generators and ties. Both copies of that word
are charged. This is a new overlapping-helper search class, beyond the
disjoint-pair restriction; merely changing the matching seed is not its
mechanism.

One sorted greedy pass considers all **935 strict-gain nominees**: **40**
are accepted, **115** fail an exact prefix guard, and **780** conflict with
an already used pair or singleton. It stops after that pass, without a
restart. Each successful replacement consumes a distinct original pair and
singleton. Search coverage is complete for this declared domain and these
representatives; it is not a global circuit optimum or an optimum over all
shortest words, longer words, alternate target bases or overlapping triples.

The independent verifier enumerates invertible matrices directly and uses
Boolean Gaussian elimination, set-valued supports and literal scalar
instructions. It checks **1,008 neighbor inequalities** plus realizing
paths to certify all 168 shortest lengths, all search scores/ties, every
guard decision and the final word. Each of the 661 source, target and dirty
helper columns is replayed separately in both D directions for four words.
Controls remove preparation, restoration and middle coefficients, reverse
the required undo order, transpose helper directions and corrupt a group
certificate. A cancelling helper pair is accepted at the boundary but
charged two ADDs. Every over-budget nominee remains rejected.

The owning checker is imported unchanged. It confirms the full endpoint,
geometry and H1/H3/H4/H5 predicates. As in PR915/926, **original syntactic
H2 and literal `K_equals_D` are false**; the complete semantic boundary is
checked independently instead. No predicate is rewritten to hide this.

The exact numerical checks are:

```text
64 F^3 B^2 = 2659668991063825342552531255296 < 2^104
2^18 F^5 B^4 = 6253203843833393632383133699318586751438846446425369214976 < 2^192
```

The second uses about **99.6193%** of its ceiling. Exact integers, not rounded
bit counts, decide admission. The expression and 192-bit charge are checked
against the unchanged supplier source. These are finite local/staged bounds,
not a complete hosted precision invoice.

## Predecessors, pins and remaining obligations

Exact research base: `007664306fff84fbb1c9a1b4053b69f439764034`.
`SOURCES.json` pins executable/data dependencies and records the selected
context at that base separately from runtime dependencies. The full consumed
predecessor closure is also checked through PR926's existing manifest.

Credit Gareth Davidson's **PR915** target basis and **PR926** disjoint helper
construction, and Scott Woolsey Biggart's **PR733** two-sided mechanism.
The new contribution is the bounded coupled-triple replacement and its
independent evidence. Concurrent **PR941** reports a disjoint-pair floor of
11,948 ADDs with this target basis; the present 11,840-ADD word is outside
that class. This package does not import or independently certify PR941's
matching proof. PR952's six-wire phase-A synthesis concerns another section;
its savings are not composed here. The earlier factored-retiming negative
searches and unevidenced campaign triple proposal concern different objects
and do not establish an obstruction to this search class.

Before using this word as the bit supplier, accept the semantic D interface,
emit and audit the complete hosted supplier, recompute the entire finite and
precision invoice and rebuild the outer assembly. Inherited all-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape
and analytic obligations remain. This is neither a formal proof of the full
multiplication theorem nor independent human peer review. It does not compose
other circuit savings or alter `upstream/`.

Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance** in research, implementation, proof checking and
packaging. Apache-2.0; cumulative attribution is in `NOTICE.md`.
