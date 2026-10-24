# Attribution

The original two-image block3 prefix, hook representation, eight-cut family and Gaussian rank engine are from CrocSwap/integer-mult-bounds PR4688, by lee-phys, exact head264c4b3cb13c82d171de352ecf60486dfb8d2bd4:
https://github.com/CrocSwap/integer-mult-bounds/pull/4688

The unchanged source files in vendor/pr4688 are authenticated by SHA256. The underlying small-m goal and hook framework are also discussed in PR4628 by jacobalansussman:
https://github.com/CrocSwap/integer-mult-bounds/pull/4628

The phase-aligned two-call repair and its exact residual identity are PR4710, scientific commit e7988a43f523690c279232845ab2bfeabb5df10b, current head b0d5192390af493d626054b060921895df3c94d2:
https://github.com/CrocSwap/integer-mult-bounds/pull/4710 The arithmetic.py file is an unchanged copy of that contribution's standalone Gaussian-rational residual verifier. This handoff uses those identities and contributes two concrete continuation preparations, exact replay, and scoped graph obstructions. It does not claim that the predecessor authors proposed these two preparations or made the disproved continuation claim.
