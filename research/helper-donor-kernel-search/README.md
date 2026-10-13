# Exact helper-donor cold-kernel search

**No new κ.** This is a reusable search tool for the helper-donor cold-kernel mechanism, plus an exhaustive
census of that mechanism on the current frontier words.

The mechanism was introduced in #1274 for pivot 531 and extended in #1286/#1297 to pivots 543, 555 and 567.
It is the largest local gain of the X54 line: H1 −3, H3 +1 per call per kernel, about +2.6·10⁻⁷ in κ each.
#1297 describes an "exact backward output-sensitivity relation search", but no search tool has been published.
`search.py` is such a tool. It is standard-library code on top of #1186's exact pricer.

## What it does

`search.py` takes every register p and every write gate `p += k·Y` that has earlier reads of p. For each one:
1. It deletes a nonempty subset of those early reads.
2. It cancels p inside the write: it inserts `Y −= p/k` at a cut, and restores it with an early-cleanup tail
   gate. Every tail position next to a tail gate touching Y or p is tried.
3. It computes the exact change D of the whole program map, mod 2³¹−19.
4. It looks up one donor hook whose unit injection vector satisfies `q·v = −D` for a dyadic q. A donor hook is
   `X += p` before a gate reading X, and `X −= p` right after.
5. It prices each surviving candidate exactly with #1186's frame solver.

## Results

- **Positive control:** on #1218's base word, which has no kernel yet, the search **rediscovers #1297's pivot-555
  kernel exactly**:
  - delete reads 466, 502 and 734;
  - donor 620 with coefficient 2 at hook 112;
  - cost delta −11,676, profile `{1:2355, 2:504, 3:411, 4:130, 5:82}`.

  It also finds the equivalent alternative donors 585, 616, 617 and 618, matching the five alternative hooks
  #1297 reports.
- **Census on #1305's final words** (base and extra, the four kernels already applied). The same words are used
  unchanged by #1324, the current best claim, κ = 0.001677380107853623:
  - every register and every write was searched, 1,048 write instances per word;
  - **no further single-donor kernel exists** in this family;
  - the four pivots 531/543/555/567 were the only ones available.
- **Negative control:** pivot 555 on the already-kernelled word yields no gain.

This tells others where not to look: further local gains on these words need relations with two or more donors,
a different cancel form, or changed interfaces.

## Reproduce

```sh
# Needs research/exact-frame-toolkit from PR #1186 (head 9254a3cc) and NumPy.
python3 -B research/helper-donor-kernel-search/verify.py --toolkit PR1186/research/exact-frame-toolkit   # ~1 min
SHARD=0 NSH=1 python3 -B research/helper-donor-kernel-search/search.py WORD.json.gz TOOLKIT all            # new word
```

`verify.py` does the following:
- checks the input pins;
- reruns the positive and negative controls;
- checks that the recorded sweep logs (`evidence/`) cover every write and contain no gain.

The inputs are vendored byte-for-byte:

| Input | Source |
|---|---|
| `K4-BASE-WORD`, `K4-EXTRA-WORD` | #1305 at `a96a5d95` (`gauge44-word`, `extra-word`), identical to #1297/#1324 |
| `PR1218-BASE-WORD` | #1218 at `0aa14797` |

## Scope

- This is a finite search over the stated family. A failed search is not an impossibility theorem.
- A candidate found by the tool is nomination data only. It still needs native replay, the leaver premise and
  strict owner admission.
- All inherited conditions of the incumbent remain conditions here: all-size compiler, common-label and
  mutable-source realization, whole-call hosting, precision and tape, exact recovery, analytic transfer, and
  bit H1–H5.

## Open next questions

1. **Are there two-donor relations?** *Why:* they are the natural next family once single-donor kernels are
   exhausted. *First step:* hash the pairwise sums of the normalized injection vectors restricted to the support
   of D. *Blocked by:* the quadratic number of hook pairs, about 7·10⁵ per write, so a sparse-support filter is
   needed.
2. **Do other cancel forms work?** Examples are cancel through a helper other than the write source, or a
   restore placed in B. *First step:* add these to the cut and restore options of `search.py`. *Blocked by:*
   none.

## Credit

The mechanism is Jeremy Kothe's #1274 and Rohan Arun's #1286/#1297. The pricer and frame solver are #1186, by
Marius-Paul Dumitrean, with the lineage it credits. The words come from #1305/#1324 (jeremykothe2), #1218/#1193
and their ancestry. Prepared by Wronskode with substantial AI assistance (Anthropic Claude, via Claude Code).
Apache-2.0.
