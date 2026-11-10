# Execute the first-success slice constructor over F4

This supplies the fixed-F4 executable backend left open by PR6543. The
primary uses Ali Romman's exact existing Field implementation to construct
the least-degree extension field, a literal invertible projective slice of a
raw regular pencil, and its two-sided inverse. Every scalar operation uses
F4 tables; encoded elements are not integers modulo4. The reference admits
square matrices of dimensions0..17 over F4=F2[z]/(z^2+z+1), with2=z and3=z+1.

The new result is an executable interface and independently checked witness
evidence. PR6543 already supplies the first-success algorithm and its
all-prime-power arithmetic proof; Nick Petalas6451 supplies the threshold
theorem and attainers. Ali Romman5664 supplies the field backend, and
5692/5712 already handle raw nonprime pencils and transport. This is not a
new threshold theorem, a new field framework or the first F4 pencil program.
[PROOF.md](PROOF.md) binds the fixed field to the inherited contract;
[NOTICE](NOTICE) retains exact credit and source boundaries.

Both independently implemented engines pass all65,536 raw2x2 F4 pencils:
63,360 regular and2,176 identically singular. Their complete4,476,800-byte
first streams agree byte for byte, including every determinant polynomial,
status, selected projective point, literal slice and inverse. Ten named raw
inputs additionally test empty/singular/infinity/constant/row-pivot boundaries,
dimension5 F16 witnesses, dimension17 F64 witnesses, nonprime strict-equivalence
transforms and a repeated-root dimension9 case. After blind first seals, the
oracle checks all ten actual primary outputs, including every returned
modulus, embedding, point, slice and both inverse products for the nine
regular cases. Different valid field presentations are allowed.

With CPython3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/f4-first-slice-constructor
```

VERIFY.json registers both normal and optimized modes of both engines.
For a Git-free export run those declared commands with their package path.
The defaults require the retained RESULT.json and ORACLE.json; they never
silently regenerate missing receipts. `--emit` prints a newly computed
receipt. An optional `--stream-file` may write the full raw stream to a fresh
external path during `--emit`; default registered runs do not write files.
Exact commands, controls and coverage limits are in [VALIDATION.md](VALIDATION.md).

Six source objects remain byte-exact under SOURCE-PINS.json. Only the
authenticated definitions of `inputs/5664-field.py` and Field construction
are executed; its tensor recognizer and every predecessor scientific checker
are unrun. The oracle imports no source or primary arithmetic code. All raw
named matrices and prospective calibration degrees were frozen before
execution in PENCILS.json; the degrees are checked against actual searches.
`input_recipe.py` emits that exact JSON without modifying the frozen file;
its regeneration is byte-identical. The generator retains the inherited
attainer and literal strict-transform recipes alongside the input artifact.

## Scope and remaining obligations

Independent executable coverage is the complete2x2 domain and ten named cases,
not all matrices of dimensions3..17. The all-size arithmetic theorem remains
the credited source result; this port is not proof-kernel verification of its
implementation. Human acceptance remains open. No general nonprime backend,
new bit/tape/storage complexity, original-field SL descent or native consumer
is supplied. An extension-field invertible slice is not physical coefficient
delivery, arbitrary dirty restoration, a precision/stock/control/compiler
invoice or a complete recursive/outer multiplication supplier. All five
selected framework assumptions and the frontier remain unchanged. No new
kappa, selected full replay, Lean or Docker is claimed.

## Open next questions

* Bind one returned extension-field slice to an actual original-field descent
  or native consumer. Pin the raw pencil and source consumer, then charge
  coefficient/map delivery and restoration. A literal extension witness alone
  does not supply this interface or its full invoice.
* If another supplied nonprime backend is needed, select one concrete missing
  consumer after refreshing overlap, then independently verify its returned
  witnesses. Existing F4/F9 decomposition and transport work retains credit;
  changing a field cardinality alone is not a new construction or theorem.

Prepared by ToikY with substantial OpenAI Codex assistance and separate AI
primary/oracle/static review. Apache-2.0; human/kernel acceptance unclaimed.
