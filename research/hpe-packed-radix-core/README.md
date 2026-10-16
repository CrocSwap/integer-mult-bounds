# Kernel-checked packed comparison from the HPE energy grammar

This completes the standalone smaller-radix comparison implication left open
by [PR2499](https://github.com/CrocSwap/integer-mult-bounds/pull/2499), using its
unchanged Gaussian-integer energy grammar. For C counts k1,k2<=K and
**B=2^(K+2)**, equality of both scaled Gaussian packed row sums implies equality
of every corresponding scaled entry. Ten theorem roots compile in Lean4.34.1;
their live transitive axiom reports contain only `propext`, `Classical.choice`
and `Quot.sound`.

## Scope and evidence

PR1859 already supplies the written stronger-premise radix argument and its
Python comparator. PR2499 kernel-checks its energy ingredient but explicitly
leaves the final comparator open. The new work composes that actual imported
theorem with signed-digit uniqueness, unequal-C-count scaling and finite
packed-row linearity. It does not claim a new mathematical radix bound.

Arham Tahir's PR1906 and Ross's independent PR1934 audit already give a
sharper **K+1-bit** written result using whole-row energy. This package does
not formalize that sharp energy-ball argument. It formalizes the K+2-bit
component-bound contract from the available PR2499 column-energy grammar.

[PackedRadix.lean](PackedRadix.lean) proves:

- Energy-one column entries obey component bounds `|a|<=2^k`.
- Scaling each side by `2^(K-k)` bounds difference digits by `2^(K+1)<B`.
- A zero signed packed sum with strict digit bounds has every digit zero.
- Both Gaussian components satisfy that implication.
- Actual scaled packed equality gives entrywise scaled equality, by the
  `packed_compare_sound` theorem, with explicit common finite arity.

[BOUNDARY.md](BOUNDARY.md) states the exact quantified contract. `ColumnEntry`
may witness different runs/dimensions per entry; the bound needs only energy.
A common source matrix and its parser/compiler correspondence are not assumed
kernel-certified. The old Lean4.21/Mathlib/Python semantic bridge remains open.

The finite observer executes the unchanged source comparator and its twelve
existing controls. It collects all **3,072 basis columns** from the six literal
circuits, reconstructs packed rows from them, and checks all **6,144 real and
imaginary packed components**. Each retained pair has k1=9,k2=7,K=9, scales1,4
and B=2048. The already established largest packed-input sizes remain 5,622
bits versus 10,221; these are predecessor results, not a timing claim.

The observer uses the retained compiler/executor. It supplies finite source
correspondence, not an independent gate implementation or formal Python
semantics. Four false Lean statements are rejected: a nonstrict digit bound,
an omitted imaginary component, an omitted relative scale and a dropped final
column. Separate source/formal/typed-receipt corruptions fail closed.

Canonical base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority4;
picker seed `1a55dafafc1eb36d2c2be11cbc6e518c`. The binding baseline passed.
The exact original card and scoped refinement are recorded in TASK.json.
SOURCES.json pins base inputs; VENDOR.json pins unchanged PR2499 Energy.lean
and its explanation; FORMAL.json records this proof's source hash and roots.

## Reproduce

From the repository root, with Python3.12 and Lean4.34.1:

```sh
python3.12 scripts/research_package.py --package research/hpe-packed-radix-core --check-only
python3.12 scripts/research_package.py --package research/hpe-packed-radix-core
python3.12 research/hpe-packed-radix-core/check_lean.py --lean /path/to/lean
```

The registered Python replay checks finite correspondence and artifact integrity.
The explicit Lean command freshly compiles both modules in a temporary directory,
audits actual compiler axiom reports and rejects four false statements. It does
not reuse an existing `.olean`. Both commands were run locally; the recorded
kernel result is in KERNEL-VALIDATION.json. Generic package CI does not install
or invoke Lean. No hosted CI or independent human review is claimed.

Normal checks do not rewrite artifacts. `verify.py --write` explicitly regenerates
the finite receipt for review. All sources are authenticated before import.

## Open next questions

Connect the retained Mathlib gate interpreter to `Energy.Step` and its finite
vector enumeration to `packGaussian`. That formal translation is required
before replacing the old checker; more finite examples do not discharge it.
No selected checker, frozen source, supplier or exponent is changed here.
Hosting, compiler uniformity, precision/tape and multiplication remain outside
this finite-checker proof boundary.

## Credit

PR2499's source and notices are retained byte-for-byte. Credit woklerx/PR1859
for the stronger-premise bound and packed executor, Jeremy Kothe/PR593 for
the Clifford formalization, original digit argument and literal pairs,
commdata2338 for the literal parser, and the retained Lemma A/G lineage.
Credit PR1906/PR1934 for the sharper written row-energy result and its audit.
New formal composition, source observer and controls: ywz65 with substantial
OpenAI Codex assistance, Apache-2.0. Separate AI review is identified as such.
