# Attribution and license

New contribution: Ross Richardson (@RossRichardson), with substantial
OpenAI Codex assistance in research selection, proof development,
implementation, separate checker development, validation and writing.
The second implementation is an independent method written by the same
AI-assisted contributor, not an independent human review. Apache-2.0,
under the repository's root LICENSE.

Predecessors retain their attribution:

- **martinxxx9, PR1046**, head
  `7cadcb0a2fc71fdedc0066704dec3fec58c2ca2c`: full affine-code factorization
  model, arbitrary-length affine floor, two- and four-total witnesses,
  rank-two decoder distinction, and scoped three-term affine minimum 35.
  Its README, proof and independent receipt are retained verbatim. The
  present proof follows its Sylvester reduction but replaces the affine
  census bound with an orthogonal-basis argument for arbitrary masks.
- **Ross Richardson, PR958**, head
  `28d68c88f0184835d8c8a7266ab8d0dad3f18a8a`: five-port quadratic Gram,
  parity clique, separate-star obstruction and optimistic stage budget.
  Its proof is retained verbatim. This does not reopen its separate-star
  search or claim an improvement to its larger-p ceiling.
- **Joel Pulikkan / GamingPuzzled, PR231**: paired-port star parity and
  the five-port decoder context. The integrated note is retained verbatim.
- **icekylinx and eumemic**: paired-cube decoder and supplier lineage.
- **DreamingOfClouds, PR446/595**, **Jacob Sussman**, **Zhihao Chen** and
  retained contributors: pairing/frame, common-label and stage-accounting
  premises, as credited in PR958 and PR1046. Those premises are inherited,
  not proved or relaxed by this contribution.
- **Rohan Arun, Jeremy Kothe, Hao Yan** and the cumulative k8/T16 and
  PR589/PR555 lineage: the frozen selected context only. No selected
  supplier is modified or freshly cold-replayed here.

Seven inspected source/context files are retained byte-for-byte in sources/,
with source paths, exact base, SHA256 and Git blob identities in SOURCES.json.
PR1046's three retained files and PR958's proof were additionally checked
against their exact predecessor heads. Existing notices in the retained
files remain intact. No predecessor executable implementation is imported.
No literature-wide priority claim is made for rank inequalities or
orthogonal-basis facts.

Nearby work inspected: PR1070 concerns address-map affine agreement, not
these support masks; PR669's odd-diagonal copy theorem uses another Gram;
PR912/888 concern nonlinear data messages under other geometric pricing;
PR1077 concerns eight-term E8 field extensions. None supplies the exact
three-total arbitrary-mask result here.
