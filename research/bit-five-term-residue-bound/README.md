# Five address-twist contributions still have residue rank at most two

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.** For
every m >= 4, five rank-at-most-one frames satisfying the dirty degree-one
conditions of JoyboyBrian's [#5490](https://github.com/CrocSwap/integer-mult-bounds/pull/5490)
have role-s residue of matrix rank at most two. The bound is attained with
five nonzero frames at every such m.

Let V=M_m(F2), U_j(z)=L_j z R_j with invertible L_j,R_j, and require

```text
sum a_j = 0,
sum a_j * (U_j z) = 0 in Sym^2(V), for every z,
beta = sum U_j^-1(a_j).
```

Polynomial squares are retained. [PROOF.md](PROOF.md) classifies the
five-frame span and multiplicities. At span dimension four or three,
transport rank distance forces residue zero. At dimension two, the frame
multiplicities are 3,1,1 and the problem reduces to the credited four-term
theorem of [#5978](https://github.com/CrocSwap/integer-mult-bounds/pull/5978).
Its rank-two witness becomes a five-frame witness by splitting one frame.

This answers the m >= 4 rank-one part of that older package's Open next
question 2. It does not settle five contributions at m=2 or m=3, arbitrary
frame ranks, complete words, supplier admission or a new kappa. In this
necessary-condition model, adding a fifth contribution does not raise the
maximum residue rank above two at m >= 4.

## Evidence and reproduction

From the repository root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-five-term-residue-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/bit-five-term-residue-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-five-term-residue-bound
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-five-term-residue-bound --check-source-history
```

The scientific marker is `PASS_FIVE_TERM_RESIDUE_BOUND`. The verifier
enumerates all five-nonzero-vector multisets spanning F2^d and summing to
zero for d=1,2,3,4. Their counts are 0,3,28,168. It checks the claimed
types and every kernel-basis syzygy for each of the 199 multisets in a
six-dimensional ambient space. This finite calculation corroborates the
written dimension-independent argument; it does not replace that proof.

It then checks new five-frame rank-two witnesses at m=4,...,8 by direct
polynomial arithmetic on every input basis matrix. Omitted-term,
changed-frame and changed-transport controls must fail at the named
conditions; a square-retention control is also required. No predecessor
executable is imported or replayed. The two cited proof files are
authenticated by their pinned hashes.

Default replay writes nothing. Its JSON output includes the complete
finite result and SHA256 of all six package files and the two proof inputs.
`--receipt /absolute/path/outside/repository.json` writes the same generated
receipt and refuses to overwrite an existing file. No receipt is hand-written.

## Limits and credit

The universal result is a written proof using cited premises. Independent
human and formal proof-kernel review are unclaimed. No rounded native
implementation, complete caller, other off-diagonal blocks, constant-input
second-order cross terms, physical twist costs, recursive moment or selected
supplier replay is supplied. The selected frontier is unchanged.

JoyboyBrian's #5490 supplies the model, the necessary conditions, transport
rank distance and three-term rigidity. Nick Petalas's older #5978 supplies
the four-term theorem, its field witnesses and the explicit five-term
question. Krzysztof Wójt's #5003 supplies the inherited second-order
quotient and source compatibility, with the Cinna Davis/#2110, Ali Romman,
eumemic and huxint lineage retained by citation. Linear syzygies and finite
fields are standard ingredients. The new contribution is the five-term
reduction, its sharpness by splitting, and the new finite corroboration.

The scoped side result changes card `bit-new-register-model` from a native
alphabet search to this local obstruction. The card's working source-binding
baseline passed against selected #7000. This is not a new register census
or a completed native alphabet. The CLAIM describes the local refinement;
TASK.json marks the change from the broader catalogue premise explicitly.

## Open next questions

1. Can five rank-one frames at m=3 have residue rank three? The span-four
   branch is the sole new branch left by this proof. Start with a five-circuit
   of rank-one matrices and impose the full quadratic equations on two-sided
   transports. A transport pair can differ by rank three there, so the present
   distance argument does not settle it.
2. What is the first contribution count admitting full-rank residue for a
   named m>=4? Start with six contributions and classify frame multiplicities
   before any word synthesis. A local residue still needs every remaining
   block, constant-input cross term and physical cost in a complete caller.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Implementation bounds

The verifier has no recursion, network, subprocesses, dynamic code generation
or predecessor imports. Census loops cover at most C(19,5)=11,628 multisets
per dimension; syzygy systems have 30 variables and 21 equations. Witnesses
have m<=8, at most 64 input basis matrices, five terms and 4,096 polynomial
bit positions. Functions are shorter than 60 physical lines. Explicit
exceptions remain active under optimization. Each registered command has a
120-second timeout. Python exact arithmetic allocates during this bounded
offline computation, a Power of Ten rule 3 deviation. Package and proof
files are individually capped at 256 KiB. Warning-strict normal and
optimized execution provide the interpreted-code diagnostics.
