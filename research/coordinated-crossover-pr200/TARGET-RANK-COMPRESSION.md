# Integer target-response compression

Eight disjoint groups cover targets216–223 and864–919. Their complete prefix response rows have exact integer dependencies, recorded in `rank/selection.json`. A response row is a target's coefficient vector against the independent signed compensation symbols in its specified prefix. The relations concern these response rows, not the arbitrary initial target values.

For retained targets R and a dependent row t with response r_t=Σ_j a_tj r_j, perform Y_t←Y_t−Σ_j a_tj Y_j at the common post-center D0. Execute the retained prefix reads and omit the dependent reads. Immediately before the group's first nonprefix read, restore Y_t←Y_t+Σ_j a_tj Y_j at the recorded common rank-20 frame. The output equals the old Y_t plus its required response. The transformation is block triangular with identity diagonal blocks and determinant one; arbitrary dirty coordinates restore exactly over the integers and F₂. Dependencies use only retained rows, so the order of dependent-coordinate updates does not change the transfer.

For example, for targets872–879 retain872,873,874,876 and use response relations:

- r875=r873−r874+r872
- r877=r873−r876+r872
- r878=r874+r876−r872
- r879=r873−r874+2r872−r876

The eight groups have29 dependent rows and eliminate122 prefix reads. The local target histogram delta relative to the same 492-source/equal-response word is C1+32,C2+2,C3−4,C6−2,C8−23,C9−4,C12−5,C13−24,C20+29. Stock and rank mass are unchanged. Setup and inverse use186 scaled additions, conservatively expanded to198 unit additions in the fixed-call bill.

`targetagg/word.py` executes this transformation literally. `targetagg/boundary.py` independently reconstructs the response matrices, tests arbitrary-variable local transfers for both integer signs, checks the common closing frame and its primal/dual prime witnesses, and rejects missing-setup, missing-inverse and repeated-read controls. The full scalar word and complete paid profile include every source, ordinary recipient, copied-center scatter, terminal action and restored target path.

Prepared by eumemic with substantial OpenAI Codex assistance. Apache-2.0; inherited contributor and assistance notices remain.
