# Paid-job merges in the native word: exact invoice delta

## 1. Source and what changes

The comparison is PR6551: the PR6545 Gaussian retirement, the PR6398 mixed
root with child trees `(7,2,5,4)`, and the exact PR6529 native word. The
caller, the trees, the dual pairs and the retirement proof of PR6551 are
unchanged and retained in `source.tar`. In particular the unchanged prefix
through event 328 and the equal-target argument of PR6551 section 2 apply
without modification, because the caller sees the native word only through
its public boundary.

Only the native word changes. It is the PR6529 word with three edits, each
an exact rewrite with its own compensation (README.md lists them with event
numbers).

- A merges the paid hops of the owned register 770 (frames 549, 553, 1047,
  593) into one hop from frame 549 to frame 593. The six rows that consumed
  the intermediate values receive the same combination in frame 3 at the
  start of the program, and two rows take compensating ADDs in frame 127.
- B re-bases the addition made to register 471, with its compensation in
  frame 676.
- C moves the input of helper 435 from frame 127 to frame 246. The only
  change at the public boundary is `final[435]` from 127 to 246, which the
  verifier checks and allows explicitly. Its preparation is done in frame 3 and compensated
  in frame 516, with a shadow register 783 created and cleared in frame 127.

The verifier regenerates the PR6529 word from its retained construction and
compares it with `BASEWORD.json.gz` before it substitutes `WORD.json.gz`. The
new word is then replayed against all 799 columns, the owned lifetimes
(46 lifetimes, peak 13), the helper maps, the absolute phases and the 7,488
caller contacts. The base-word positional controls run on the
base word.

## 2. Exact profile delta

Let H_r denote one Gaussian target or paid job of rank r. The native word is
called 18 times. From the replay in RESULT.json the candidate local profile
differs from the base word's as follows, per call.

```text
paid    {1:-3, 3:-1, 4:+1, 5:-1, 6:+1}
targets {8:+1, 9:-1}
```

The edits A and B account for `paid {1:-3, 3:-1, 6:+1}`: three rank-1 jobs
and one rank-3 job become one rank-6 job, with the rank mass 3+3 = 6
preserved. Edit C accounts for `targets {8:+1, 9:-1}` and
`paid {4:+1, 5:-1}`: one rank-9 target becomes rank 8 and one rank-5 job
rank 4. The complete invoice therefore changes by 18 times these counts:

```text
Delta T = 18 H8 - 18 H9,
Delta P = -54 H1 - 18 H3 + 18 H4 - 18 H5 + 18 H6.
```

The caller side of the invoice is identical to PR6551, so these are the only
changes against it. The checks in `pricing.py` confirm that the complete
profile is exactly PR6551's plus this delta: productive fields 13,756 are
unchanged, paid jobs fall from 67,096 to 67,042, and the target minus paid
rank mass stays 760 (each of the two masses falls by 18).

## 3. Why the gain is positive

The signed gain is `Delta(T-P) = Delta T - Delta P`:

```text
Delta(T-P) = 18 * [ (3 H1 + H3 - H6) + (H5 - H4) - (H9 - H8) ].
```

Take `H_r = r^t` with `0 < t < 1`.

1. The function is strictly concave with `H_0 = 0`, so it is strictly
   subadditive. Since 1+1+1+3 = 6, `H1 + H1 + H1 + H3 > H6`: the merge of
   edits A and B is positive.
2. The derivative `t r^(t-1)` strictly decreases. Hence
   `H5 - H4 = integral over [4,5] > integral over [8,9] = H9 - H8`, and
   edit C is positive.

Each bracket is positive, so `Delta(T-P) > 0` for every exponent in the
stated domain. This is an exact all-exponent comparison. It does not
depend on the tested saving.

Equivalently, the six ranks `{1,1,1,3,5,8}` on the gaining side have the
same sum 19 as `{4,6,9}` and are majorized by it, so every strictly concave
sum is larger on the first multiset.

## 4. Costs that are charged

The new word has 18,561 events (68 more than before). The owned inventory
has 29 labels and 46 lifetimes with peak 13, and the local scalar allowance
is 137,866 (was 137,218). The rank mass of local paid and target jobs is
5,924, as before. The full ordinary-work upper bound stays 254,932,208, below
the retained 10^9 allowance. The edits add no unpaid channel, helper, copy
or restoration. One shadow register (783) is nonzero when it is erased in
frame 127, like register 781 in PR6529, and is covered by the same
`owned_erasure` assumption.

## 5. Conditional numerical result

The new claimed saving is 0.00329700. The tested saving is 0.003297005. Two
rational engines certify a positive complete moment at the tested saving and
both signs of the raw root enclosure in RESULT.json. The raw crossing is
0.0032970138574524603, above PR6551's 0.003294926110571363 by
0.0000020877468811. A negative derivative bound gives a unique crossing
below the retained BIT cap. Both engines reject the full PR6551 invoice at
the new claim.

The retained completion tails, the integer compiler threshold and all 54
strict plus four functional outer predicates are evaluated with the new
profiles. As in PR6551, the source tail decay 31/32 is below the completion
ratio, and the check uses decay 97/100 and reserve 10^(-27) at power 1920.
The conditional bound has the same form `O(n (log n)^(1-kappa))` with
`kappa = 0.00329700` under the five source framework assumptions.

No global optimum over words or callers, unconditional multiplication
theorem, independent review or selected-frontier change is claimed.
