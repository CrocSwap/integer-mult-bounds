# A further U* end at raw helper249

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

This extends the pinned PR637 JP8 supplier. Let P be its exact scalar state after A, cut, B and all inherited early-tail gates. Let I=P^-1. Coordinates below refer to raw registers. U*=[256,128,64,32,16,8,6,1]. The new end is249, originally cold with terminal width9. Its current frame at this point has rank7 and lies in U*. Registers25 and255 already have frame U*.

The key is to add a cold row with zero pairing to the candidate's initial dirt column. Define

    r0 = e254 + e245
    r1 = e256 - e249 - e246 - e242 - 2 e240.

Exact arithmetic in the inherited state gives

    r0 I = e28 - e26 - e25/2 + e24/2,
    r1 I = -e249/2 + e255 - 2e31 + e29 - e24/2
           + e28 + e25 - 2e26.

Thus r=-2r1+4r0 eliminates the rank7 carrier26:

    r I = e249 - 2e255 + 4e31 - 2e29 + 3e24 + 2e28 - 4e25.

All four ports24,28,29,31 have the same rank4 frame B=[296,168,120,6], contained in U*. They can be combined before any of them climbs. The earlier candidate with an unavoidable-looking carrier26 was only one choice of inverse row, not a lower bound.

Take c=e249/2. Then r*c=1. The cold premix M is identity except

    row249(M) = e249/2 + e256 - e246 - e242
                - 2e240 - 2e254 - 2e245.

It uses one scale and six rankzero additions. It realizes column249(M)=c and row249(M^-1)=r. Every involved helper is cold and previously unended, so inherited ended rows and columns are unchanged.

Target rows need separate cancellation. The constructor calculates the ten rankzero target writes from the actual signed target block, using

    x_t = -1/2 * sum_{z target} I[t,z] * P[z,249].

It must not assume that the target block is identity: some target signs/mixings differ. These writes precede M and remove the target part of the new dirt column without changing the non-target state. They use the existing allowed primitive of a frame-zero target write from cold helper249. The complete constructor and native auditor verify the resulting target cancellation rather than trusting this formula.

The appended eight-gate tail is:

    at B: 31 *=4; 31 -=2*29; 31 +=3*24; 31 +=2*28
    at U*: 249 +=31; 249 -=2*255; 249 -=4*25; 255 +=249/4.

The first three U* additions implement r I, making row249 exactly e249. Before the tail, the non-target dirt column is e249/2-e255/4; after those additions and the final column-clear gate it is exactly e249. All69 ended rows and columns are now unit vectors. A fresh dyadic FULL Gauss–Jordan cleanup on the remaining non-target/non-ended coordinates restores every other non-target register. The native auditor separately checks scalar endpoint, arbitrary-dirt compensation, both orientations, frame chains, row/column cones and paid profile.

Only accumulator31 climbs from rank4 to8, and only249 gains a rank7-to8 climb instead of rank7-to9. Per-call paid-profile delta is {1:+2,2:-1,4:+1,5:-1}; helper249's width is9->8. New JP8 profile is {1:2528,2:397,3:448,4:169,5:63,6:4,8:8}. A global gain still requires a new literal owner map and exact assembly; no global claim follows from local admission alone.

Reproduction: `build_end249.py --base-hpe HPE_WORD --source-recipe PR637_JP8_RECIPE --code PINNED_CORE_CODE --out NEW_DIRECTORY`. The exact word/recipe payloads reproduced across two invocations. `check_end249.py --word WORD --provider jp8 --out RECEIPT --negative-controls` is independent sparse Fraction/GF2 code with no constructor/auditor imports and works under `-I -O`; it checks all69 ended rows and columns, the remaining non-target cleanup, monotone frames, the climb profile, and eight focused mutations. Native gate guards remain unchanged.
