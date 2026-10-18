# One extra total cannot improve the orthogonal-frame decoder

**Research note / scoped negative result.** For the fixed rank-ten Eisenstein
orthogonal-frame decoder, every binary decomposition into at most eleven totals
has abstract pairing charge at least **40**. Both ten and eleven totals attain
40. Non-clean supports and cancellation are allowed.

The result follows from a general theorem for any partition into orthogonal
frames. It closes a complete one-extra-total mechanism, rather than a sampled
neighborhood. The inherited necessary supplier screen requires charge at most
31, so this mechanism cannot improve the selected complex supplier.

The result fixes the binary decoder matrix. Other fitting matrices and twelve
or more totals remain open. It gives no supplier, new kappa, unrestricted
copy optimum, or complete multiplication theorem.

## Argument and evidence

Read [PROOF.md](PROOF.md) for the claim, quantifiers and complete argument.
With one extra factor, at least one factor space remains the frame code.
The other factor space extends that code by at most one dimension.
Distinct supports in one coset have pairwise orthogonal geometric complements.
Their total rank deficit cannot exceed the ambient dimension.
This gives the sharp lower bound.

The standard-library verifier supplies three forms of finite corroboration:

- The primary exact census covers 164110 nonempty proper-span E8 supports in
  159270 cosets. The maximum aggregate deficit is four.
- An independent traversal checks all 10700 sets of at most three port
  generators over the prime 65537. A determinant bound makes its ranks exact
  over the rationals. Combination-based subset enumeration recovers the same
  complete support-to-rank dictionary. Separate rational elimination then
  checks 9200 complements and 5470 pairs in all 4360 nontrivial cosets.
- A direct four-port model enumerates all 225 nonzero rectangles and 50625
  ordered pairs. Matrix XOR finds every possible third term. All six ordered
  two-term and 618 ordered three-term decompositions have charge at least four.
  This check uses neither the factor-space reduction nor the coset argument.

Both E8 sharp witnesses replay exactly. Controls reject a duplicated frame and
an altered geometric rank. Repeating a low-rank support violates the deficit
bound and shows why the proof needs distinctness. A direct full-span Gram check
catches the one-unit underpricing error.

[EXPECTED.json](EXPECTED.json) records regression outputs, not independent
expected answers. Source pins protect the inherited input files. No proof
assistant or independent human reviewer has checked the universal theorem.
The written proof and the finite checks have different roles.

## Reproduce

From the repository root, with standard-library CPython:

```sh
python3 -B research/eisenstein-eleven-total-seed22/verify.py
```

Expected final line: `PASS_EISENSTEIN_ELEVEN_TOTAL`.
The JSON output records the interpreter and exact finite coverage.
The primary research run uses stable CPython 3.15.0.
The generic manifest retains the repository's explicit Python 3.12 environment;
validation records its separate compatibility replay.

## Open next questions

The charge of 40 is already larger than the necessary limit of 31 in PR1794.
Helpers, source access, frames, copies, restoration, recursive children and
assembly still require payment. No physical synthesis follows from this note.
The next question is whether a changed fitting matrix or at least two extra
totals can lower the complete invoice. Start with an optimistic paid budget.
No obstruction for that larger scope is established here.

## Provenance and credit

[SOURCES.json](SOURCES.json) pins the base commit and inherited files.
[TASK.json](TASK.json) records the scope refinement and open question.
The actual run identifier, seed22 and timing appear in [VALIDATION.md](VALIDATION.md).

Jonathan Lam / PR798 provides the E8 geometry and pairing-rank charge model.
GamingPuzzled / Joel Pulikkan / PR620 provides the order-three construction.
Maximooch / PR1794 provides the frame witness and necessary cost screen.
Josie Elliston / PR1977 studies stronger general minrank bounds; its search is not repeated here.
This note contributes the general one-extra-total theorem and its specialization.

Charles Bethin, with substantial OpenAI Codex assistance in derivation,
implementation, verification and writing. New work is Apache-2.0.
Preserve all predecessor notices. The selected frontier and upstream files are unchanged.
