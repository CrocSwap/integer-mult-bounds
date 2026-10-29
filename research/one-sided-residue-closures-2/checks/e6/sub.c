// usage: sub m L < Zfile   ; Zfile: 511 lines "lo hi" (u64 decimal) for functional a=1..511 ; prints deduped masks "lo hi" with popcount>=L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef unsigned long long u64;
u64 Zl[512],Zh[512];
#define HS (1u<<24)
u64 *HL,*HH; char *HU;
static inline int pc(u64 a,u64 b){return __builtin_popcountll(a)+__builtin_popcountll(b);}
void ins(u64 l,u64 h){
  u64 x=l*0x9E3779B97F4A7C15ULL ^ (h+0x7F4A7C15ULL)*0xC2B2AE3D27D4EB4FULL; unsigned i=(x>>20)&(HS-1);
  while(HU[i]){ if(HL[i]==l&&HH[i]==h) return; i=(i+1)&(HS-1);} HU[i]=1;HL[i]=l;HH[i]=h; printf("%llu %llu\n",l,h);
}
int main(int argc,char**argv){
  int m=atoi(argv[1]); int L=atoi(argv[2]);
  for(int a=1;a<512;a++) scanf("%llu %llu",&Zl[a],&Zh[a]);
  HL=malloc(HS*8);HH=malloc(HS*8);HU=calloc(HS,1);
  int n=9;
  // pivot combos via bitmask over 9 columns with popcount m
  for(int pm=0;pm<512;pm++){ if(__builtin_popcount(pm)!=m) continue;
    int piv[9],k=0; for(int c=0;c<n;c++) if(pm>>c&1) piv[k++]=c;
    int sc[100],sr[100],ns=0;
    for(int i=0;i<m;i++) for(int c=piv[i]+1;c<n;c++) if(!(pm>>c&1)){sr[ns]=i;sc[ns]=c;ns++;}
    for(u64 bits=0;bits<(1ULL<<ns);bits++){
      int rows[9]; for(int i=0;i<m;i++) rows[i]=1<<piv[i];
      for(int s=0;s<ns;s++) if(bits>>s&1) rows[sr[s]]|=1<<sc[s];
      u64 l=~0ULL,h=~0ULL; for(int i=0;i<m;i++){l&=Zl[rows[i]];h&=Zh[rows[i]];}
      if(pc(l,h)>=L) ins(l,h);
    }
  }
  return 0;
}
