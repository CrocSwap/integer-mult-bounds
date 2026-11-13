# Packaging correction to the root review

The root replay receipt records shape `[1,1,2,1,10,3]` in the established order `[f,c,P,S,w,cutoff]`. At root's request, the packaged `ROOT-REVIEW.md` corrects one parameter label from `r=1` to `c=1` and states the selected central rank is `3`. The original review is preserved byte-for-byte at `original/ROOT-REVIEW.md` (SHA-256 `08137daaf65d0bccefcf6474d3807cea13accaf95a317219491d51e84d1ebe24`). The root checker and receipt remain byte-for-byte unchanged.
