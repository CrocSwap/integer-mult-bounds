# Attribution and provenance

New implementation and finite uniform certificate: Mason Hale, with substantial
OpenAI Codex assistance. Apache-2.0. No independent human or formal-kernel
verification is claimed.

David Harvey and Joris van der Hoeven, *Integer Multiplication in Time
O(n log n)*, Annals of Mathematics 193 (2021), 563–617,
DOI 10.4007/annals.2021.193.2.4, supply the periodic Gaussian resampling
and inverse-correction lineage. The retained source uses the
[45-page author manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf).
The Gaussian maps, Neumann method, FFT, CRT and carry algorithm are existing
methods, not inventions of this contribution.

OpenAI's frozen source sections 07-resampling.tex and 08-assembly.tex supply
the map definitions, retained permutations, disk-grid and two-normalization
conventions. Their source files remain unchanged and are pinned as live
inputs in SOURCES.json.

Jose Manuel (jmbarrancoml), PR2298 at
8507498d363735ced0b0a3f02d5ecf80ed3e3805, identifies the immediate open
Gaussian execution handoff and supplies the conservative outer composition.
His proposed selected BIT/complex callees are PR2234 at
d047ef86fbc5b1614d3d8e2b8d3441413beab73f and PR2287 at
8c60765b5dea9d862b3b190d55da102a576031bf. Their proof files are separately
pinned for context; no predecessor executable is imported, and their
selected suppliers are not executed or independently validated here.

Related audits retain their own scope: Artus Krohn-Grimberghe's PR371
identifies final-grid rounding; Effy Elden's PR684 checks generated Gaussian
domains/windows; Alan Grillo's PR902 distinguishes correction-power and
inverse-tail bounds; Hanson Sun's PR1430 analyzes rounded Neumann evaluation.
The present implementation explicitly includes these error categories but
does not repackage those audit results as new work. The underlying fast
Gaussian construction credits eumemic and icekylinx in those predecessors.

The selected native Clifford/gauge44/T16, bit-supplier and other contributor
lineages retain their repository credit. This artifact changes none of their
frozen sources, selected certificates or review dispositions.
