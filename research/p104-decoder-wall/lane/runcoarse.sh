#!/bin/sh
# Cover of all codim-5 closures (F,B), dim F=f, dim B=f+5 (D,S only grow under the covers => monotone):
#  f0b5, f4b9 exact; f1b6 inside f0b6 (F -> 0); f3b8 inside f3b9 (B -> F2^9, refined to b=8 on failure);
#  f2b7 inside f2b8 (B -> hyperplane, refined to b=7 on failure).
cd "$(dirname "$0")"
for R in R0123 R0135; do
  ./prop2 data_$R.txt 0 5 ${R}_f0b5.out
  ./prop2 data_$R.txt 4 9 ${R}_f4b9.out
  ./prop2 data_$R.txt 0 6 ${R}_f0b6.out
  ./prop2 data_$R.txt 3 9 ${R}_f3b9.out 8
  ./prop2 data_$R.txt 2 8 ${R}_f2b8.out 7
done
echo DONE
