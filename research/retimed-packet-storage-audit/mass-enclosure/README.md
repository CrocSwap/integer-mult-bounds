# Reviewed dyadic mass enclosure and owner consequence

The unchanged author [PROOF.md](PROOF.md) establishes the uniform error of
the actual `Measure.inverse_power` and `Measure.mass` loops in Ali Romman's
#8042 source at `dfd25d553a843a946ca0b94130a5ff8943e98fdd`. Its exact hash is
`b92516aaa39192c6713654fa6f41b4c4f8367b1f71c7e374b95fd31687464c1b`.
The accepting [independent review](review/CROSS-REVIEW.md) supersedes the
historical author footer saying review is pending. The proof and all five
frozen review artifacts remain byte-identical to the accepted versions.

For reduced dyadic `t=k/2^d`, grid `g=2^p`, rational `1<=x<=X` and `p>=0`,
each inverse-power endpoint has error at most
`E_d(X)/g`, where `E_d(X)=(d+1)(d+2)X/2+d+1`.
For nonnegative rational volume `V`, each directed mass endpoint has error
at most `2V E_d(X)/(t g)`. The proof permits a zero rounded lower endpoint
and handles empty intervals separately.

The authentic Gaussian and binary callers have `d<=60`, `t>=1/2`, volume
`N^6`, grid `g>N^64`, and every nonempty endpoint at most `2064N`. Hence
their mass error is `<2^24 N^-57<=2^-33<1/4` for `N>=2`. The explicit
[owner corollary](OWNER-COROLLARY.md) combines this with the unchanged
Gaussian census: its `<2B` production bound no longer needs the local
unproved numerical-enclosure premise. Full funding, correctness, physical
storage, movement and analytic recovery remain separate contracts.

The author checker uses exact integer-power inequalities. The independent
reviewer uses rational log/exp series with proven remainders and integer
bisection, without importing the author's checker or repeating its root
recurrence. Its 600 inverse-power cases, 1,080 mass cases and 1,320 directed
allocation checks are finite corroboration; the induction gives the
universal theorem. Neither checker executes a production-size calendar.

The portable adapter preserves all frozen reviewer bytes, authenticates
them through `review/FROZEN.json`, and compiles them with `optimize=0` so
their assertions remain active. It changes only the runtime, authenticated
stock and output paths, then requires both generated receipts to equal the
accepted receipts exactly:

```sh
python3 -IB mass-enclosure/restore_stock.py --runtime /path/to/runtime \
  --output /tmp/mass-review-stock
python3 -IB mass-enclosure/review/replay.py --runtime /path/to/runtime \
  --stock /tmp/mass-review-stock --output /tmp/mass-review
```

`restore_stock.py` invokes the original authenticated graph/journal loader
and reproduces the exact graph/layout JSON bytes named by
`STOCK-BINDINGS.json`; these large generated files are temporary replay
inputs. The unchanged reviewer additionally checks their original logical
graph/layout digests.
The parent `verify_followups.py` supplies the fresh offline runtime. Original
priority for the source and transfer argument remains with Ali Romman and
the retained contributors. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance; the independent review is model-assisted,
not human peer review or a proof-assistant certificate.
