# Produce CRT offsets from actual current child coordinates

The balanced CRT caller reconstructs its left integer from coordinates that
have **already been transformed**. They differ from original mixed-radix
digits. This package replaces that numeric producer with encoded tape
arithmetic and completes the right-node offset/padded-coordinate consumer.

For left moduli (5,7), original digits (1,2) become current coordinates
(1,5). The [producer](producer.py) reconstructs **11** and returns offset
**7** for right modulus 13. Treating the current coordinates as original
digits instead gives 26 and offset zero. Both current coordinates are
individually valid. This is a real source-convention distinction, not a new
CRT identity or another fixed key/ROM wrapper.

[PROOF.md](PROOF.md) proves the result for arbitrary finite nonempty left
and right groups with pairwise coprime moduli, complete product below
2^(P-1), and common encoded precision P>=4. It includes current-coordinate
reconstruction, modular inverses, every successive right prefix, padded
right values, invalid-left disabling, all owned arithmetic erasure and
borrowed head/byte restoration. The output is an owned sequential stream
of (offset,new right-coordinate), plus owned k_A and S_A words.

## Arithmetic domain and implementation

The existing physical `Word.Ring` rejects small moduli padded into a wider
arena: it requires exactly one leading zero margin bit. Its guard remains
unchanged and is tested. The new separately proved `Arithmetic` uses only
retained unsigned bit-tape primitives. It explicitly admits M>1 with a zero
highest bit; it implements modular add/subtract, scanned multiplication and
Euclid directly. It neither skips a Ring initializer nor relaxes a frozen
guard. Arbitrary additional leading zeros are legal in this new interface.

The producer receives two encoded streams of (modulus,current coordinate)
records, a pre-initialized 64-slot numerical arena and source tape classes.
All word data are read through bit operations. It never receives a Python
list of numerical moduli, decoded coordinate, group length or computed
offset. Runtime Word.inspect is disabled, and an AST check excludes direct
word backing reads, bit_length and times_small. The only runtime literal
constructor uses the compiled constant one.

Input descriptor framing, initialized arena/template and their transport
are explicit entry premises. Stream LEFT/END markers must be unique;
record/key grammar failures inside that frame reject. Up to eight unrelated
borrowed numerical words may retain arbitrary contents and entry heads.
The producer returns input heads to one and preserves unrelated heads.

The constructive bound is **32 live numerical slots**, with fixed capacity
64, and at most `2^20*(P+2)^4` source-tape/control operations per admitted
invocation. Numerical and descriptor/output traffic are recorded separately.
This finite-alphabet bound is not a claim that a complete binary control
compiler, arena constructor or the full E(p,ell) implementation has run.
The exact operation model and all remaining costs are in the proof.

## Evidence

[RESULT.json](RESULT.json) records:

- All **1239** canonical operand pairs for moduli 2..15, checking encoded
  modular addition, subtraction and multiplication, plus **119** unit/nonunit
  inverse cases. The original Ring rejects wide modulus 5 while the new
  explicitly admitted interface accepts it.
- All **64** eight-valued left coordinate pairs for (5,7), including invalid
  padding, with mixed valid/padded right fields; the (1,5) discriminator is
  additionally recorded separately.
- Varying 1+1, 1+2, 2+2 and 3+3 group sizes at P=4,8,12,20,32. Runtime
  moduli 257/263/269 exercise values outside any finite `times_small` label.
- Four complete original balanced-root fixtures after both children have
  transformed, and four complete original **mixed-width Callers**. Their
  declared widths (4,4,4,5), literal idle/active rows and unchanged Beneš
  consumer provide an independent endpoint/offset check at each level.
  Observer decoding in the verifier does not feed the encoded producer.
  Each module receives a source-derived encoded fixture; these checks are
  not an uninterrupted physical whole-tree run.
- Eight unrelated dirty borrowed numerical words at different noninitial
  heads, unchanged input/template bytes, and erasure of all visited private
  backing; the observed peak is at most 26 slots.
- Actual producer mutations misinterpret current coordinates, omit the
  preceding right modulus or reduce padding. Eleven rejecting controls
  include noncoprime prefixes, high-bit/product capacity, empty groups,
  insufficient entry inventory, short words and a malformed second right
  record after output has already been produced. Cleanup is checked before
  fixture teardown.

Finite observations corroborate the uniform written argument. Host integer
CRT, direct values and source logical network construction occur only in
independent reference/inspection code. No speedup or new kappa is claimed.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-current-crt --check-only
python3.12 -B scripts/research_package.py --package research/encoded-current-crt
```

The hook runs ordinary and optimized checks, authenticates all declared
source bytes and compares a type-sensitive frozen receipt. Only explicit
`verify.py --write-result` regenerates it. Standard export supports direct
Git-free replay. Source-history/committed-byte and export integrity checks
are transport evidence, not mathematical acceptance.

## Scope, predecessors and family decision

Base is canonical `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority7.
[SOURCES.json](SOURCES.json) pins the original CRT algebra, mixed-width
caller, physical words/records and the existing original-coordinate offset
producer. Tekalign's `crt-address-streams/crt_offsets.py` already computes
encoded **original-lower-coordinate** triangular offsets with its paid-router
premises. That work is retained, not claimed again. PR4192 already supplies
a shared-arena Beneš compiler; PR4982/PR5015 concern supplied-ROM/key and
radix consumption. This task fills a different numeric current-child input.

Initial overlap covered all 6710 tracked notes, 320 open PR bodies at
2026-10-23 06:50:51 UTC and 4130 Discussion records at 06:51:43 UTC, with
complete inventory/pagination. Targeted CRT/encoded/offset searches and
source reads distinguished these predecessors. Arbitrary diffs and
unpublished work remain limits. Canonical coordination is [Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19140230).
[TASK.json](TASK.json) retains the exact scoped card and stop rule.

**Narrow, then stop:** this is a complete numerical module and logical
consumer boundary. Pre-entry parameter/arena/descriptor construction,
physical transport, binary control compilation, complete ROM/table
construction, raw compact macro, sparse repair, ordinary interchanges,
full E and native/outer transfer remain external. The original mixed-width
Caller is a logical verifier reference, not a physical runtime oracle or
full payload caller. No selected frontier, supplier or theorem is changed.

## Open next questions

1. Bind one actual caller's encoded parameter/coordinate stream production,
   transport and restoration, with a complete entry invoice.
2. Join these offsets to an encoded permutation/Beneš/ROM producer and query,
   preserving current-state epochs and all output/scratch lifecycle costs.

Both questions and blockers are structured in TASK.json. This contribution
does not implicitly start either implementation campaign.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retain Cinna Davis/#4100's balanced CRT algebra, Hiroki KUMAZAKI/#4169/#4174
and the mixed-width caller, Tekalign's original-coordinate encoded offsets,
ToikY/#4192, unpaidmoon/#4377, Jose Manuel and the retained physical Word,
caller, Douglas Colkitt/John-Michael Smith and source NOTICE lineage.
Frozen sources are unchanged. No independent human or formal proof-kernel
acceptance is claimed.
