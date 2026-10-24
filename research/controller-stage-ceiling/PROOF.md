# Complete stage-family ceiling and a native repair target

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## Family and scope

Fix one of the three source-bound local invoices: selected PR4470, PR4610,
or PR4626. There are v=112 ports and transverse rank b=8. For each
1 <= p <= 64, take any split a in {0,...,p-1} of the minimal-cut paired
path controller, and **any** subset S of its 2p+1 native stage positions.
Stages outside S become fully paid query shears, lose all helper credit,
and lose their stage multiplier in both main targets and idle jobs.
This is the specialization operation of PR4440, not deletion of a bill.

The family is deliberately an invoice relaxation: all these substitutions
are priced even if a particular new physical contact has not been admitted.
Rejecting this stronger relaxation is safe; positive scores alone would not
admit a word. No other idle masks, words, native suppliers, typed outputs,
or p>64 are excluded. The selected record is unchanged.

## Complete surplus

Let n=|S|, t=1-C, and let H_t and P_t be the local helper and paid moments.
Write V=112 and B=8. The complete surplus is

    F(C) = n(H_t-P_t+V) - V(2p+1) + 2V(1+Bn)^t
           + sum_arm 2V[(1+B(k+e))^t - (Bk)^t - e B^t].

There are a left arm of length a and a right arm of length p-1-a. At
an arm step j, k is the number of selected bits in the first 2j positions
of that arm and e is the next, even-position bit. The right arm is read
in reverse stage order. Rank-zero idle terms mean zero cost, including
in the limit t -> 0. The central odd-position bit contributes only to n.

The first term includes all n independent helper inventories and all n
native paid inventories. The V correction replaces the otherwise paid
query at each native stage. The second term charges every query position.
The third term is the two copies of the long main target. Each arm term
includes its shorter main target, initial/terminal idle, and the separate
middle idle of rank B when e=1. Thus no middle idle is silently erased
when its stage remains native. `literal_control` independently counts every
LOCAL, QUERY_SHEAR, IDLE and diagonal target of the retained p16 word.

## Dynamic program, with outward rounding

An arm's score depends on a prefix only through its selected-bit count.
For a nonempty arm its first two bits have no separate charge and therefore
only their count 0,1,2 matters. An empty arm has one bit. At each subsequent
step choose e, add its displayed complete arm contribution, then choose the
following odd bit unless this is the last step. Keep the largest score
for each count. This is exhaustive induction on the bit prefix, not a
local hill climb. It is the recurrence of the credited historical floating
DP, now evaluated with exact, outward integer bounds.

The retained rational interval engine encloses each r^t. Scale by 2^64,
round positive occurrences up and negative occurrences down. Every DP
score is consequently an upper bound on its real surplus. Maxima preserve
upper bounds. Combine both arms, every split and the middle bit, then
maximize over every p=1,...,64. The three native profiles share that
combinatorial envelope. Their local replacement terms are added separately.

At C=0.003022, every final upper bound is strictly negative. `RESULT.json`
records the exact rational upper bounds, integer scale and witness parameters.
The covered count is sum(p*2^(2p+1), p=1,...,64) per native invoice. It
counts split/support pairs; it is not a claim that all invoices are distinct.

Acceptance also exhausts every arm bit pattern through length four and
all complete stage supports/splits through p=3; checks the actual p16
invoice for each local substitution; and recomputes a witness moment with
the independent full-invoice path of the rational engine. Omitting the
real middle-idle charge or duplicating independent helper credit changes
the rejection into an apparent positive result. These are rejected models.

## Why one test excludes every larger saving in this family

For each fixed support, divide the surplus by 8^t. Its normalized local
replacement is

    L(C) = (H_t - P_t + V)/8^t.

All paid ranks are at most 8. For t in (0,1], its derivative with respect
to C has upper bound

    L'(C) <= -((P_1-V)/8)*log(8)
              + sum_(r<8) H_r log(8/r) < 0.

Indeed, retain only the negative rank-one paid contribution; its magnitude
is at least (P_1-V)log(8)/8. Bound each possible positive helper contribution
by H_r log(8/r), and drop the other negative contributions. The final strict
inequality is enclosed rationally for each frozen invoice.

For an arm step with k>=1, the derivative of

    (k+e+1/8)^t - k^t - e

is negative, since x^t log(x) is increasing for x>=1. If k=0,e=1,
its derivative is again negative. The only positive case k=e=0 contributes
at most (1/8)^t log(8) before the multiplicity 2V. There are at most p-1
such arm steps. The normalized negative query term contributes
-V(2p+1)(1/8)^t log(8), more than cancelling all of them. If n>=1,
the normalized long main target has negative derivative. If n=0, its
positive derivative leaves the total derivative exactly
-V(1/8)^t log(8). Thus F(C)/8^(1-C) is strictly decreasing throughout
0<=C<1 for every support in the family.

The negative bound at .003022 therefore excludes **all C>=.003022,
C<1**, not merely that one numerical point. This is a conditional invoice
ceiling, not a universal limit on integer multiplication.

## Changed model: the H repair budget

The old H112 reconstruction changes a local rank-eight correction bill
8 H8 to 8 H1, saving 56 units of rank per full call. Applying that
56-unit change to PR4610's stronger native invoice is an **optimistic
unrealized combination**. It is not a source-compatible H word: changed
warp contacts, cross-port response, head/hole normalizers, absolute phases
and arbitrary-input helper restoration all still need proof.

For that explicitly hypothetical invoice, the same complete DP gives
exact upper repair budgets at .004, .006 and .01. A full-invoice lower
bound at each saved witness confirms the scale of the positive budgets.
A rank-one repair request costs exactly one unit at every C; a rank-r
request costs r^(1-C). Storage, scalar work and all other requests also
need their actual ledger. These numbers are spending limits, not free
allowances or proposed K values. In particular the .01 screen fails even
before a repair in this bounded family. No conclusion for p>64 follows.
