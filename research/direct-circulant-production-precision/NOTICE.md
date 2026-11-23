# Attribution and retained source notice

The six files in `retained/` are byte-identical source excerpts at file level,
with original paths and exact hashes listed in `ORIGINS.json`. They are retained
to authenticate the physical gate layout, phase/grid selector, full allocator
and cached coefficient schedule used by this audit. The sources are provided
under the repository's Apache-2.0 license.

Ali Romman, with substantial OpenAI Codex assistance, supplied the original
direct circulant Fourier word and coefficient generator in PR #7849.
Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance, supplied
the retained rational full compiler and phase interface. Chafik Boukhalfa's
certified phase work and Vlado Vojdanovski's compiler and routing work retain
their predecessor credit. Cinna Davis and the native/mixed-rank contributors
remain credited for the separate supplier and recovery interfaces.

The new precision proof, selector and exact audit were prepared for
Jerry Chen / @CubeJerry with substantial OpenAI assistance. They do not
reassign predecessor credit or assert independent human acceptance.
