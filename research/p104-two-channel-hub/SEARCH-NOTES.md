# Bounded retiming screen: search failure only

After the frozen-chronology obstruction, one extension was tried: retime a
register's MOVEs inside a gap containing no scalar read, write, INIT or CLEAR
of that register. Boundary states and the 1,095-frame catalogue were fixed.
The screen formed 9,520 frame/gap possibilities and tested 16,897 cuts.

Discovery used prime 1,000,003, exact modular propagation and intersection
bases. It found 1,576 cut records of pairing rank at least two, with maximum
modular rank 20. These are algebraic possibilities, not dyadic physical words
or earned productive targets. They show that retiming materially changes
the frozen theorem's hypotheses.

For each cut the screen formed pairs from the computed collection and
delivery bases, retained at most the 100 cheapest individual channel pairs,
then tested pairs of those for a nonzero two-by-two Gram determinant. It
charged the union of frame/gap query edits once per physical edit. Both
chronological and access-cost-ordered basis insertion were tried. Arbitrary
linear combinations of these bases were not exhaustively searched.

The cost-ordered pass evaluated 386,644 basis-channel pairs with nonzero
determinant. None had positive optimistic signed local gain at κ=.00337180,
before additional pivot access, boundary bases, ordinary work, buffer
lifetimes, completion or stock costs. The best floating screen value was
approximately −0.00111363528845. This pair used dimension-one frame106 with
prospective target change `2H1+2H8−2H9` and query change `6H1−2H3`.

Its four unshared query replacements were:

| Role | Source MOVE event | Original frames | Intermediate frame | Paid grades |
|---|---:|---|---:|---|
|157|9482|3→356|106|2→1+1|
|195|9950|3→404|106|2→1+1|
|521|10069|3→740|106|3→1+2|
|635|9382|3→1093|106|3→1+2|

No favorable pair was promoted to rational C,D, an emitted word or native
replay. Power values here were floating-point discovery values. The exact
proof and RESULT.json do not depend on this search or its sign.

The screen is not an exclusion of arbitrary retimings, basis combinations or
larger blocks. Further exploratory block tests are outside this frozen proof
package. The next meaningful construction must provide a complete physical
word and invoice. No expensive native replay is justified by the candidates
listed here.

Prepared for @CubeJerry with substantial OpenAI Codex assistance; seed46.
Credit the contact-free retiming implementation of PR #6805 and Ali Romman's
helper basis methods. Apache-2.0.
