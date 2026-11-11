# Nonzero addresses where the F9 operators have matrix element 1

**Exhaustive finite census, no new κ.** On the pinned F9 word, the only
computational basis address at which every canonical `K_G` has matrix element
`+1` is `|0>`. At address `1`, operators 30 and 66 send the state to `|2>`
with phase `+1`; the other 70 classes fix it with phase `+1`.

The selected conditional exponent stays `363005817/100000000000`.

## Scope and evidence

Task `joint-query-controller`, scope **refined**. The card's first experiment
says to audit the PR5745 active-mode claim before another free-injection
search. The merged F9 audit separated `K_G|0>` from the full-frame transport
and left the nonzero-address matrix element open. This package evaluates that
element at every address. It does not change the query demand or construct a
caller.

[PROOF.md](PROOF.md) gives the phase formula, the character property on each
fixed space, and the operator-26 / operator-30 witness. [RESULT.json](RESULT.json)
records a basis of every phase-+1 set. The domain is the 72 canonical classes,
their four signed variants, and all 512 width-9 basis states. Every triple is
evaluated. A failed or partial search is not this claim.

Operator 6 at address 328 is a checked phase `-1` incidence: the address is
fixed and the coefficient is multiplied by `-1`. There are 114 such
incidences. The scalar observer does not match `K_G` there.

## Reproduce

From the repository root, CPython 3.12, standard library:

```sh
python3 -I -B research/f9-nonzero-address-matrix-element/verify.py
python3 -I -O -B research/f9-nonzero-address-matrix-element/verify.py
python3 -B scripts/research_package.py --package research/f9-nonzero-address-matrix-element
```

The direct verifier prints

```text
PASS_F9_NONZERO_ADDRESS_MATRIX_ELEMENT classes=72 addresses=512 variants=4 common_phase_one_addresses=1 address_one_exceptions=30,66 minus_incidences=114 no_new_kappa=true
```

`--record` rewrites `RESULT.json` and is not part of the check. Normal replay
only reads it.

## Limits

The census is exactly the 72 classes of this word. It does not extend to an
arbitrary invertible matrix or to `F† K_G F`. Phase `-1` incidences are
counted and one is exhibited; they are not priced. No compiler, caller,
precision, or outer admission is claimed.

## Open next questions

* Can one of the eight full-frame transports that fix `|0>` be used without a
  new `H8`? First price one of operators 2, 16, 17, 41, 44, 61, 62 or 64,
  including its frame change, restoration and target debit. The matrix element
  of `K_G` does not supply that invoice.
* What ordinary correction does one phase `-1` element force? Start with
  operator 6 at address 328. One sign is not a new κ.

## Credit

The F9 word and the scalar observer are Ali Romman's PR5720 and PR5745,
following flyingviper's active-mode restoration and the filtered-native packet
of Cao Yifan, Cinna Davis and Dugongue. The quadratic engine is the copy
pinned by PR5745. The `|0>` separation of `K_G` from the full-frame transport
is the merged audit of that word; this package starts from the nonzero-address
question left there.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
