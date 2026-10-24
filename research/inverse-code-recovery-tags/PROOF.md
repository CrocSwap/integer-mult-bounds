# Exact recovery tags with a sharp state bound for the rounded inverse code

FINDING — the rounded inverse-code kernel has a sharp recovery-state bound: 13^8 states, or 30 packed bits, per real scalar coordinate of its 112 owners. Eight separate four-bit quotient tags give a simple 32-bit implementation of the injective output interface. This answers part of the ownership question left by [PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035); it is not a reversible circuit, a free cleanup rule, or a new kappa.

Let M be the actual 112-by-8 signed mode matrix, with M^T M=56I. Let round mean nearest integer with exact ties away from zero. The [source kernel](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/coded-inverse-fixed-grid/kernel.py) computes, in integer grid units,

```text
t=M^T x,  q=round(t/52),  y=x-Mq.
```

Retain the eight tags a_j=q_j mod 13. Given y and the tags, compute s=M^T y. For each mode, recover the unique integer q in

```text
ceil((-26-s)/4) <= q <= floor((26-s)/4)
q mod 13 = a
round((s+56q)/52) = q.
```

There are at most fourteen integers in that interval, independently of the input word length. Then return x=y+Mq. This is an exact constructive inverse for the tagged map on every integer input. A caller can pack the tags as sum_j a_j 13^j, or keep eight four-bit fields.

**Why recovery is unique.** Write r=t-52q. The rounding rule gives -26<=r<=26, and s=r-4q. Two distinct candidates with the same residue mod13 must differ by at least13, so their r values differ by at least52. Equality forces the endpoints -26 and +26, with the larger q at +26. For nearest rounding away from zero, r=-26 requires q>=1, while r=+26 requires q<=-1. Those conditions cannot hold for an increasing pair. Thus at most one candidate is valid; the original q supplies existence. Reconstruction also verifies the defining forward relation, since M^T(y+Mq)=s+56q.

**Sharp lower bound.** For every v in {-6,...,6}^8, take x=Mv. Then t=56v and round(56v/52)=v, so y=0. The 13^8 vectors are distinct because M has column rank 8. They all obey ||x||_infinity<=24. Therefore any injective extension of this rounded map needs at least 13^8 distinguishable retained states when the input bound admits H>=24. The tags above attain that state count. Since

```text
2^29 < 13^8 = 815730721 < 2^30,
```

30 packed bits are necessary and sufficient for one coordinate. For N independent real scalar coordinates, the exact maximum fiber size is 13^(8N), so the information lower bound is ceil(log2(13^(8N))) bits. A direct separate-tag layout uses 32N bits. Signed monomial physical wrappers are bijections and do not change these fiber counts.

**Why this matters for a caller.** The source kernel's noninjectivity is quantified, rather than treated as an unspecified loss of the entire input word. A caller that must recover the original inputs can retain a fixed amount of information per coordinate. Those tags are output state that must have an owner. This theorem does not permit them to be erased while preserving only y, and does not price a reversible gate implementation, tag movement, whole-field storage or later uncomputation. The original paid classical overwrite contract remains valid on its own terms. The complete physical boundary invoice and global precision remain separate obligations.

**Evidence.** Normal and optimized CPython 3.12.13 checks agree. The checker authenticates the actual [mode source](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/coded-native-caller/NORMALIZERS.json) and kernel, verifies the Gram identity, checks all valid residual cases for q=-200,...,200, and round-trips forty mixed 112-owner vectors through the actual source kernel. The written proof covers all integers. Zero-fiber fixtures and the twelve-residue collision are controls. No whole native, compiler, selected replay or reversible machine run was made.

Run the registered checks with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/inverse-code-recovery-tags
```

Expected verifier marker: PASS_SHARP_INVERSE_KERNEL_TAGS. The checker proves the large zero-fiber count by the exact Gram/scalar identities; it does not enumerate 815 million vectors.

Credit: JoyboyBrian's PR5035 supplies the finite kernel, rounding rule and original collision; Dillon's [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) supplies the mode factorization and physical wrappers; Dugongue and the retained native, ownership, precision and compiler authors keep their source credit. Some retained package prose uses the wrong number PR5037 for this kernel; the verified PR is 5035. New exact recovery formula and sharp fiber count: Ali Romman with OpenAI Codex assistance, Apache-2.0. Author-checked, not independent human or proof-kernel acceptance.
