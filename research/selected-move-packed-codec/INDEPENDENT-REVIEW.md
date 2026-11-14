# Separate orchestrator review

The lead orchestrator independently reviewed the frozen graph generator
at SHA256
`119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba`.
The regenerated literal graph has 6,003 instructions, 43 tapes and digest
`ac852be823d484cdb0d10e8fb8cd063c7f0c4351789ea0516bf5fd23a475ce1b`.
The graph was not changed after that review.

The reviewer wrote `independent_check.py` separately from the author's
CPU and numerical/address fixtures. It uses sparse dictionary tapes,
independent head movement and instruction execution, and tuple sorting
to calculate the address permutation. Only its import path and exact-byte
module loader were adapted for this portable package; its scientific
checks are retained.

The full independent packet has f=1, r=2, b=3, 512 addresses, 24,576 old
physical bits and a 405-bit descriptor containing a 138-bit cutoff value.
It executes 9,611,543 transitions, changes the packed data by a supplied
same-width function, and checks the complete returned old image, descriptor,
relative origins, opaque left exteriors and all private historical cells.
This is a codec service fixture, not native C arithmetic.

Three additional subprogram cases use uniquely labeled records and K=2/3,
rho>0, external rows and fixed prefixes. Their exact forward result agrees
with tuple sorting, and their reverse result recovers the original word.
They execute 1,588,986, 1,902,986 and 1,409,890 transitions respectively.
A mutation swapping a decoded input-bit branch is detected by the full
packet's independent image check.

The reviewer separately checked the increasing-position rotation argument,
guide update/halving conditions, inverse ordering, complete copied-field
cost and retained backing. No defect was found. One prose correction was
made: nine old shape values are unary-expanded; the tenth kept field,
cutoff, remains binary and may exceed the payload's numerical size.

The resulting portable normal and optimized receipts are
INDEPENDENT-RESULT.txt and INDEPENDENT-RESULT-OPTIMIZED.txt. The final
VALIDATION.json records their executed commands and exact output hashes.
No full f>1 or K>1 nine-slot packet, source native operator, whole selected
caller or global foundation was verified by these checks. This is a
separately conducted model-assisted review, not human or proof-kernel
acceptance.
