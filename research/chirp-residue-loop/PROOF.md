# Equivalence of the bounded one-axis loop

This is an implementation-equivalence argument for PR3806's primary command.
It establishes no new chirp identity or multiplication theorem. James Reed's
mathematical result remains the credited predecessor.

## Domain and state induction

The ordinary interface has integer radius r=2^ell for 2<=ell<=12,
length t in {r/2,r}, and odd slope s with 0<s<t. The specialization's
test-only initial-state argument is outside that ordinary interface.

Both implementations set M=2r, c=(-s*(r//t)) mod M and start at

```text
index=0, value=0, difference=c, total=0, steps=0.
```

Before each transition they evaluate, in this order,

```text
value == (c*index*index) mod M
difference == (c*(2*index+1)) mod M
total == value.
```

The retained `require` calls have no successful-path state effect. On a
false predicate they call `fail`, which raises SystemExit with a fixed prefix
and the predicate's label. The new branches evaluate the same expressions
and raise the same exception text in the same order. They retain the separately
updated total and evaluate the third predicate at every state.

After all three predicates pass, both increment steps. If index+1<t,
both execute the same assignments in the same order,

```text
total = (total+difference) mod M
value = (value+difference) mod M
difference = (difference+2*c) mod M
index = index+1.
```

Otherwise both subtract value from total modulo M, restore index and value
to zero and difference to c, and break. Induction proves equality of every
visited state and transition. Neither closed-form check becomes a recurrence.

Before the final transition index is t-1. There are exactly t visits, so
replacing the source's open-ended loop by `for _ in range(t)` cannot truncate
an ordinary execution. The final rollover and steps==t predicates are
unchanged. Their logical rewrites are equivalent for the admitted integers
and have the same first failure text. Computing c directly uses exactly
the authenticated source helper's expression.

## Complete command and counted work

The adapter authenticates all four declared source files before loading the
retained module. It changes only `one_axis`. Every square identity, two-axis
state, recursive visit tuple, historical selected-value check and stored-receipt
comparison executes as before. No scientific result is cached.

The differential run records all 6,141 ordered
(radius,length,slope,returned_steps) tuples on both sides. Their arrays and
stdout agree exactly. The sum of enumerated returned step counts is
13,981,010. Each state loses three successful `require` call boundaries;
each rollout loses two final `require` boundaries. Thus exactly

```text
3*13,981,010 + 2*6,141 = 41,955,312
```

such calls disappear while their predicates remain. Separate profiles
corroborate this count. Timing covers the source primary command, including
authentication, import, all enumerations and receipt comparisons. It excludes
the separate retained test command and the new conformance harness, which
are checked separately.

## Rejection evidence and limits

For three smallest admitted length/slope pairs, the checker enumerates all
512 triples of value, difference and total modulo eight at initial index zero.
The 1,533 bad states must raise the original first predicate label; the three
valid states complete. Fifteen malformed domain/control cases reject. A
changed source program rejects at its hash before its appended exception can
execute. The original independent test script runs unchanged in a separate
nonoptimized interpreter, also when the conformance harness runs with -O.

The written argument covers the stated interface. Finite controls do not
provide independent human or proof-kernel review. No physical consumer,
supplier invoice, selected-frontier change or multiplication theorem is supplied.
