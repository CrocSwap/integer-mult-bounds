# Bit side, plane-port upgrade step 1: fails (scoped theorem)

**Question** (from `../README.md` and the partial-upgrade law): upgrade a set S of |S| = 5 bit
ports that share a common r (pairwise odd, S ⊂ r^⊥, rank M = 4; 11,950 such sets) from lines to
planes span(ℓ_s, ℓ_r). The upgrade raises κ iff ΔC < (8/9)|S| = 4.44.

**Answer: no.** In the class below, every decoder for every one of the 11,950 sets costs at least
68 = 63 + 5. So ΔC ≥ 5 > 4.44, and the net is at most 5 − (9/8)·5 = −0.625 ports per invocation.

## Conventions

- **Term cost.** Rational pairing rank between the span of the readers' port spaces and the span of
  the sources' port spaces (bit-side Theorem C, as in #1084, PR757 and PR761). The incumbent P111
  decoder costs 63 under this convention. F2 label-pairing rank would give 69, so it is not the bit
  convention.
- **Target.** Over F2: N_aa = 1, N_ab = 0 when the two port spaces are not orthogonal, and N_ab is free
  otherwise.

## Theorem (classes 𝒫 and 𝒰)

- **𝒫:** line-port supports are label reader sets, plane-port memberships are free, and there can be
  any number of terms.
- **𝒰:** 𝒫 plus arbitrary terms whose reader set or source set lies inside S. This class contains the
  step-0 repairs.

For pairwise-odd S ⊂ r^⊥ with s = |S|, every decoder in 𝒫 costs **C ≥ 63 + s**. The proof has five
steps, with n1 the number of terms whose functionals are nonzero on both sides:

1. The X matrix is forced to QF, so n1 ≥ 9.
2. The plane ports' row and column functionals vanish. In 𝒰 they are fixed linear functions of the
   anchored corrections.
3. N[S,S] = I_s, because planes sharing r are never orthogonal.
4. **Rank lemma:** s ≤ (n1 − 9) + #(other terms with a reader-side S part), and the same holds on
   the source side.
5. Every other term costs at least its number of nonempty S-sides. The n1 terms cost
   ≥ max(63 − s, 54) when n1 = 9 (#1084 Thm b, puncture P ∪ S), and ≥ 6·n1 otherwise.

The residual cases with n1 = 10 and s ≤ 4 are closed by exact F2 enumeration.

**Coverage**
- **𝒫:** all 226,903 maximal pairwise-odd common-r sets and all of their subsets.
- **𝒰, r live:** the same bound holds (premise F3).
- **𝒰, r punctured** (all 11,950 target sets have r punctured; λ_r makes the odd-to-r labels
  rank 8):
  - One extra rank per side is possible here. This was re-checked with exact savings maxima and an
    exhaustive 10-term search.
  - **Closed** for every s ≥ 5 set and its subsets, for s = 1 and 2 (a gadget argument for 227 sets),
    and for s = 3 with n1 = 10.
  - **Not closed:** 15 three-sets sit exactly at break-even (C ≥ 65). s = 4 with n1 = 10 was checked
    on a 10% sample only (4,965 of 49,648 sets, all closed).

**General supports are open.** For decoders with arbitrary supports on the line ports there is a rank
certificate. Each of the 11,950 sets has an explicit 12-clique, S plus 7 lines, whose port spaces are
pairwise non-orthogonal (`clique_certs.json`; the line case has 8). So any decoder needs ≥ 12 terms,
and one whose terms all have span ≥ 7 costs ≥ 72. Nothing settles the general case, because 63 is not
proven optimal for the line target once supports are arbitrary. The best constructions found cost
72 (ΔC = 9). A SAT probe on the incumbent's readers plus ≤ 4 single-port fixes timed out after 1 h.

## Run

```sh
python3 -I -B verify_step1.py          # ~2.5 min, stdlib only -> PASS_BIT_PLANE_STEP1_CLASSP
python3 -I -B verify_step1.py --full   # F1/F2 on all 226,903 sets, census on all 11,950, all small-S sets
```

The word is read from `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` (sha256 pinned
in `core.py`). `sets.py` regenerates `sets_all.json` (7 MB, not committed). `logs/` has the
authoritative runs of the class-𝒰 and small-s scripts: `classU_*.py`, `small_s.py`, `small12.py`,
`gadget2.py`, `tenneed.py`, `control19.py`, `costlemma.py`. Positive control: `control19.py` / `ten19.py`
find an exact 10-term decoder of cost 61 on a 19-line puncture, so the exclusion search can find
solutions when they exist.

**Checks done in the main session.** I re-ran `verify_step1.py` from this directory. Separately, I
checked all 11,950 clique certificates for pairwise non-orthogonality, importing only the root
vectors from `core.py`.

Prepared with substantial Claude Code assistance; a sub-agent did the search and the proofs.
