# Canonical rotation rows have a sharp three-rectangle description

Every canonical padded-rotation row is the union of at most three rectangles
in quotient/remainder wire coordinates. First and center rows need at most
one. A 64-wire example needs three, even for overlapping rectangle covers.
The descriptor uses O(h) bits and O(h) arithmetic bit work. It gives a stream
of the complete row in Theta(2^h) bit work and O(h) temporary bits.

This is an enabling proof and arithmetic algorithm. No new kappa, literal
tape row producer, complete CRT caller or discharged framework assumption
is claimed. All five selected assumptions remain. The canonical routing
rule and current-wire table are unchanged.

Read [PROOF.md](PROOF.md), [row.py](row.py), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json), and [CREDITS.md](CREDITS.md).
The exact finite census covers 2,793 networks, 28,797 rows and 1,633,182
entries at heights one through six. Every entry matches the unchanged
canonical compiler, the retained point query and the stream. The checks
include rectangle counts, switch pairs, areas, work bounds, 280 wide
descriptors with 4,937 point checks, 131,328 counter decrements, fourteen
domain rejections and four semantic controls. The descriptor cap is 65,536;
large rows are not materialized. The written theorem covers every height.

## Reproduce

Use Python 3.12 and its standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/rotation-row-rectangles
```

Both registered normal and optimized commands must print:

```text
PASS_ROTATION_ROW_RECTANGLES sharp three-rectangle row and output-linear stream
```

The runner validates provenance through Git. The six retained source files
are authenticated directly by the verifier. An exported package can run
`python3.12 -W error -B research/rotation-row-rectangles/verify.py` without
Git or network access. No historical full suite, selected cold replay,
Lean, Docker, physical row execution or complete ROM workload ran.
Counters measure the stated bit algorithm, not Python runtime or literal
tape transitions. Finite tests and source retention are not formal proof
checking or independent human acceptance.

## Selection and scope

The base is e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8.
The selected bindings pass; the catalogue assessment is older. TASK.json
records the changed compiler-interface scope under uniform-transfer-audit.
The parent handoff asks about whole-row generation and ROM reuse. This
result resolves the row-description and arithmetic-output part only.
Exact-source intake, live handoffs, open/closed bodies, a rotation/rectangle
search and relevant omitted main notes found no matching claim in their
coverage. The sparse local inventory and unpublished work remain limits.

## Open next questions

- Can a fixed tape program emit this row with a complete linear transition
  bill and full private restoration? Start with one descriptor on the
  existing point-query ABI. Output layout and ownership need explicit costs.
- When does a row descriptor beat a stored ROM for an actual CRT caller?
  Bind the current offset producer and the caller's reuse order first.
  Transport, payload use and retirement are still unpriced here.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0. The closed
formula, endpoint rules and canonical compiler retain their predecessor
credit in CREDITS.md and the unchanged source notices.
