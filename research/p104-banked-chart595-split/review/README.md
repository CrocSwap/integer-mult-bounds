# Independent chart-595 review

From the package directory, run the standalone standard-library check against the packaged signed caller and outer receipts.

```sh
python3.12 -I -B review/check_cut_and_price.py \
  --caller-receipt evidence/CALLER.json --outer-receipt evidence/PRICE.json \
  --out /tmp/chart595-independent-review.json
```

The checker authenticates both graph hashes, the literal caller, caller layout and edit. It checks the two arbitrary split-owner columns, replays the frozen graph with a complete early typed write to owner 281, and rejects a forced alias and a same-price missing old-value subtraction. An independent numerical caller replay evaluates every one of the 68 rows in each of four Gaussian phase sectors at fixed distinct body values. Complete invoice bins and the directed claim and bracket are independently recounted. A new rank-one payment or a lost rank-one target credit fails the initial threshold.
