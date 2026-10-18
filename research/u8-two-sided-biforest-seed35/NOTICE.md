# Attribution and license

New contribution by **Stephan Arrington (@steph4n-gh)**, with substantial
**Google DeepMind Antigravity AI assistance** for task selection, algebraic
formulation of the arbitrary-depth leaf-before-parent helper-forest identity,
alternating MST fixed-point construction, independent integer-dyadic and
cycle-property verification, negative controls, and documentation. This is not
independent human peer review. All new files in this directory are released under
the repository's **Apache-2.0** license; see `../../LICENSE`.

## Predecessor credit

This work builds on and credits:

- **Ross Richardson (@RossRichardson)**:
  - [PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932)
    (`c5b5b30279bdda513e97017587806a0b9f0ca850`, `research/complex-x4-target-forest`),
    establishing the `10,883` component-primitive (`47,690` real primitives saved)
    target-only signed-forest floor on the X4/U8 compensation panel.
  - [PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917)
    (`2f1584f482a022b83e98e6ab166bf60e55d5ee8c`, `research/complex-ck-two-sided`),
    combining a target forest with register-disjoint helper pairs on the
    historical PR626 CK provider and package structure conventions.
- **woklerx**:
  - [PR961](https://github.com/CrocSwap/integer-mult-bounds/pull/961)
    (`f953844028d18a5b58d7a6fc28ee7e9b2f7688d0`, `research/complex-x4-dyadic-forest-seed31`),
    proving that arbitrary nonzero dyadic parent coefficients cannot improve the
    `10,883` target-only forest floor on X4/U8 while noting helper-basis changes
    as out of scope.
  - Concurrent bit-supplier R439 counterparts [PR1040](https://github.com/CrocSwap/integer-mult-bounds/pull/1040)
    (`a01bd602969e4086e55f0d1f392855b91cfe0507`, `research/r439-post-helper-shear-seed03`,
    single post-star helper shear on R439) and [PR1047](https://github.com/CrocSwap/integer-mult-bounds/pull/1047)
    (`9d885867f28c1f391ab395af2d0b1f2a63681bfd`, `research/r439-target-retune-seed14`,
    single target-step retune on R439 after helper mixing).
- **ToikY**:
  - [PR901](https://github.com/CrocSwap/integer-mult-bounds/pull/901) and
    [PR909](https://github.com/CrocSwap/integer-mult-bounds/pull/909),
    disjoint target pairs on X4 and two-sided pairs on historical CK.
- **David Awad** ([PR807](https://github.com/CrocSwap/integer-mult-bounds/pull/807),
  CK helper pairs), **@dd-hemant** ([PR816](https://github.com/CrocSwap/integer-mult-bounds/pull/816),
  CK signed target forests), **Sricharan Vagvala** ([PR749](https://github.com/CrocSwap/integer-mult-bounds/pull/749),
  rational target pairs; [PR967](https://github.com/CrocSwap/integer-mult-bounds/pull/967),
  depth-1 bit helper stars), and **Oscar Fennell** ([PR759](https://github.com/CrocSwap/integer-mult-bounds/pull/759),
  binary target forests and superroot MST reduction).
- **Selected frontier and U8 local word lineage**:
  **Jonathan Capalbo** (PR942, `1960cfa919a0945d0ca4cb14ea96237000037903`),
  **Chafik Boukhalfa** (PR890, `4b3bd8cbe8e3e81c44161017c9b72c905a8040a8`;
  PR741, `e516b1463606840a15f80aac1995d64ce0092e89`),
  **Jeremy Kothe** (PR869, `73e86f69bf9a391e3c334999f7bbe3825dc42759`;
  PR870, `b734850dc348800942f0ffd1f0723fdec7539b2b`;
  PR799, `80e6463157cfc80b85af09e7e2f14748fe2dac60`),
  **Hao Yan** (PR858, `ae2e25fee91540c83ceee5a60e3b07422ce21c7d`),
  **DreamingOfClouds** (PR589), **eumemic** (PR555), **icekylinx** (PR425/433),
  and all contributors recorded in `CONTRIBUTORS.md`.
