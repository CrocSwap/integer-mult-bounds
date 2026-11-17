# Verification boundaries

`model.py` authenticates eight fixed inputs, reuses the predecessor's frame
construction definitions, and builds the new pair-consistent equality model.
`powers.py` provides directed integer bounds. `verify.py` checks the supplied
primal and symbolic dual, the actual integral frame assignment, and rejection
controls. No scientific predecessor replay or solver executes.

The certificate is a generated proof witness, not a handwritten receipt.
Its mathematical model hash is regenerated from the complete rows, right-hand
sides, costs, fixed constant, source profile, domains, node variable inventory
and mapped-edge count. Gzip container bytes are not a mathematical invariant;
the decoded certificate and freshly checked equations define acceptance.

## Power of Ten inspection

New functions stay within 60 physical lines. All loops range over explicit
finite collections or fixed Taylor truncations. Guards enforce at most 100,000
source events, 5,000 source frames, dimension nine, 16,000 graph nodes, 30,000
mapped edges, quotient gap five, 5,000 marginal choices, 25,000 columns and
16,000 equality rows. This is a fixed authenticated input, not a general input
service. Checks raise explicit exceptions and remain enabled under `-O`.
All new data is local to one run. Input files and certificate bytes are read
only; file operations use `Path` methods with normal error propagation.

Rule 3, managed allocation deviation. CPython, arbitrary-precision arithmetic,
standard containers and the retained frame caches allocate during verification.
These cannot meet a fixed-memory native execution rule. The scope is one bounded
read-only certificate replay, with the enforced inventories above and a 120-second
registered timeout. The largest LP table has 59,077 nonzero coefficients; dual
vectors have five integer entries. No fixed-memory physical caller is claimed.
A native port would need fixed-capacity arithmetic and storage before such use.

Rule 8, authenticated source-loading deviation. Preserving the pinned source
requires compiling its frame definitions and the single unchanged `construct`
function selected by AST name. The whole native verifier must not run, since
that would spend the assignment on predecessor verification. Eight hashes are
checked before loading. No source text is modified, and no arbitrary module or
callback path is accepted. The retained constructor's globals are explicitly
bound to its original canonical data, Fraction, copy and an exception guard.
The verifier exercises the actual graph produced by those definitions. A future
upstream definition-only module would remove the need for AST extraction.

Rule 9, managed dispatch deviation. Standard-library operations and the
predecessor's `NativeSchedule` methods dispatch through a fixed, authenticated
module. The eight test-only rejection callables have explicit local targets.
No callback registry, network or subprocess exists in the scientific checker.
Changing the loader to a native static interface would be needed for a literal
no-indirect-call execution model.

Rule 10. Registered normal and optimized replays enable warnings as errors.
The available interpreter supplies syntax and runtime diagnostics. No separate
static analyzer is installed in the declared standard-library environment.
Frozen predecessor code is preserved; no repository-wide analyzer configuration
or historical suite is changed.

## Meaningful controls

Eight controls reject a missing integral pair variable, an invalid index,
a duplicated selected variable, a changed dual coefficient, an omitted dual
row, an omitted model row, a false optimum histogram and an invalid power rank.
They exercise the same acceptance functions as the certificate. The proof's
Taylor remainders and reduced-cost signs are executable acceptance obligations.
The direct stdout receipt records source hashes, exact counts, interpreter,
all rejection reasons and the minimum certified positive sign bound.
