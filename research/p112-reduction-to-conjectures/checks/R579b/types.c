// step 1: min over (La,Lb) of |Off(h)\(La u Lb)| for every dominant support S with |S|<=2 (all non-root perp types reduce to these via Off(S) = U Off(i))
#include "e8.h"
int main(int c,char**v){build();printf("roots %d masks %d\n",nr,NM);int mx=0;for(int a=0;a<NM;a++)if(pc(M[a])>mx)mx=pc(M[a]);
 for(int S=1;S<256;S++){if(__builtin_popcount(S)>2)continue;u off=offS(S);int best=999;
  for(int a=0;a<NM;a++){u R=off&~M[a];if(pc(R)-mx>=best)continue;for(int b=0;b<NM;b++){int k=pc(R&~M[b]);if(k<best)best=k;}}
  printf("S=%02x |Off| %d minleft %d\n",S,pc(off),best);fflush(stdout);}}
