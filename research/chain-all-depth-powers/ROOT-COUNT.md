# A numerical consequence at depth five and modulus fifteen

Among the correct balanced words of length 75, exactly 4,697,520 have a
nontrivial repetition. They all have target 3, least period 15 and form
313,168 cyclic classes. The other fourteen target residues have no shorter
classes. The total number of primitive length-75 words is a separate count.

Here orders dividing 15 are 1, 3, 5 and 15. Orders 3 and 15 fail at a proper
interval of length three. For order 5 the shorter block has three copies of
each letter. The shift is 3^5=3 modulo 15. Only c=3,8,13 admit a root,
with respective residues 0,1,2 modulo 3. The two exact methods below give

```text
W_5(3,0), W_5(3,1), W_5(3,2) = 4,697,520, 0, 0.
```

Every repeated word therefore has maximal repetition 5, giving the claimed
number of classes after division by 15. In particular W_5(15,3)=45 modulo
75, while W_5(15,c)=0 modulo 75 at every other c. [General law](PROOF.md)

## Count by a prefix and an inverse suffix

Split a balanced length-15 word after its seventh letter. Enumerate the
65,100 prefixes of length 7 and the 281,400 reversed suffixes of length 8
having at most three copies of each label. Keep their exact five letter
counts. Complementary counts enforce balance.

Let P denote the unitriangular prefix action and S the suffix action, with
chronological composition S P. The target condition S P=I+cE is equivalent
to P=S^(-1)+cE, since E is the bottom-left matrix unit. To compute S^(-1),
process the reversed suffix with a negative shear at each call. Equivalently,
the interval of length h in its unsigned action acquires the sign (-1)^h.

For a prefix, key a histogram by its five counts and nine proper nonsingleton
interval residues (four pairs, three triples, two intervals of length four).
Store the three top residues with their multiplicities. For each inverse
suffix look up the complementary counts and the same proper residues.
Singleton residues already match because the counts add to three. The
prefix top minus the inverse suffix top gives c. Each complete word has
one split, including its order within the two halves.

There are 3,084 prefix keys in this run. Summing the compatible prefix/suffix
multiplicities before the endpoint restriction gives 168,168,000, the full
multinomial number. The sign and multiplication order are also checked at
519 cuts in the 173 credited positive-target witnesses at other moduli.

## Count by the middle three letters

Delete labels 1 and 5. The remaining balanced middle word has three each
of 2,3,4. Of the 1,680 such words, 270 have the required vanishing 23,34,234
counts. For each one place the three 1s and three 5s in the ten gaps around
the nine middle positions. There are 220 placements on each side.

For a given placement, let b_i count 1s before middle position i and a_k
count 5s after middle position k. The three remaining proper intervals
starting at 1 are obtained by summing b_i over the 2 positions, the 23
pairs and the 234 triples, respectively. Apply the analogous sums of a_k
over the 4 positions, the 34 pairs and the 234 triples for intervals ending
at 5. All six sums must vanish modulo three. Then the top residue is

```text
Σ b_i a_k  modulo 3, over all middle triples i<j<k labeled 2,3,4.
```

If gap g contains u_g ones and v_g fives, its interleavings have multiplicity
C(u_g+v_g,u_g). Multiply over gaps. Within-gap order cannot change a term
above, since a middle occurrence always separates the 1 and 5 of such a term.
The resulting 2,278,152 eligible placement pairs give the same W row with
their exact weights. Independently summing all gap weights gives 100,100
per middle word, again 168,168,000 words before endpoint restrictions.

At n=2, both methods give (25,520,0), also reproduced by literal enumeration
of all 113,400 ten-letter words. These engines are separate implementations
with the same assisted author and Python integer runtime. The small root
census is a finite exact computation. The general theorem supplies its use
at the larger modulus.
