# A sharp native plane bound for three complete roles

Assume the all-size native group-algebra contract from PR521. Each query
has one binary rank-one idempotent DATA projector and a nonidentity
rational plane ADDRESS map g with rank(g-I2)=1. The target is -I2 on
each of three arbitrary productive DATA roles. There are no other roles
in this statement. At least six queries are necessary. Six coordinate
reflection queries attain the bound.

The following statements give the proof.

1. The determinant-sign quotient forces an even number of negative
   queries. Every query is a rank-one idempotent, so its determinant in
   the commutative sign group algebra is the ADDRESS sign group element.
   The plane endpoint has positive determinant.
2. A complete word has full image and covector spans and no coloop.
   See PROOF.md. A coloop forces its ADDRESS map to equal -I2, which has
   rank two difference from identity and is not an allowed query.
3. Five positive queries are impossible. See POSITIVE-FIVE-PROOF.md.
   Two ADDRESS normal forms suffice. Nonunit determinants give a
   four-projector sum-zero obstruction. Unit determinants give direct
   target coefficient rank contradictions.
4. Four negative and one positive query are impossible. The sign
   quotient makes the four negative projectors sum to zero. Their image
   and covector ranks sum to at most four. Full span then makes the sole
   positive query a coloop. See PROOF.md.
5. Two negative and three positive queries are impossible. The negative
   maps must be opposite reflections, and the positive maps must be
   three distinct unipotents whose ordered product is -I2. At most one
   four-query subset can add a third target branch. The target subset
   extrema then contradict each other. See TWO-NEGATIVE-PROOF.md. The
   complete finite DATA replay in search.py and independent-audit/check.py
   gives a separate verification check.

The same elementary conditions exclude fewer queries. With at most
three queries, a full three-dimensional image span has a coloop. For
four positive queries, a target branch needs at least three maps; only
two distinct last selected indices are available, so target rank is at
most two. For two negative queries among four, the two negative DATA
projectors are equal; a full three-dimensional span then makes both
remaining images coloops. For four negative queries, the sum-zero
factorization has image and covector ranks at least three, contrary to
their rank sum bound of four. Odd negative counts fail the sign quotient.

The six-query construction uses R1=diag(-1,1), R2=diag(1,-1). For each
productive DATA coordinate projector E_j, use H_(E_j)(R1) followed by
H_(E_j)(R2). All three roles reach the full endpoint. The independent
checker verifies the construction and every single-call omission.

The theorem is about a finite native word model. It gives no lower bound
for integer multiplication and no kappa gain. It excludes the specific
plan of five plane queries plus three independent axis flips. It does
not exclude a general eight-query three-coordinate nonmonomial word,
higher-rank queries, initialized or discarded helper endpoints, or a
different endpoint or compiler model. No global novelty claim is made.
AI assistance was used in the proof and verification.

The same six-query bound holds with any number of arbitrary dirty helpers
that return identity on every input. More generally, let D be a constant
binary rank-three idempotent and require the exact endpoint
I+(z-1)D. The independently audited proof is in
independent-audit/HELPER-AUDIT.md. It proves that query images and
covectors have no coloop, including helper directions. The two-negative
and four-active cases reduce exactly to the productive three-dimensional
block. The positive branch contradictions only need target coefficient
rank three. No clean-zero, discarded, or other partial helper contract
is included in this extension.
