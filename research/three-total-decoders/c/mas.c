// max induced acyclic subgraph size: argv: n then n lines of out-bitmasks (decimal). DP over subsets (n<=26).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(){int n; if(scanf("%d",&n)!=1)return 1; uint32_t o[32]; for(int i=0;i<n;i++){unsigned long x;scanf("%lu",&x);o[i]=x;}
 uint32_t N=1u<<n; uint8_t*ac=calloc(N,1); ac[0]=1; int best=0;
 for(uint32_t S=1;S<N;S++){uint32_t x=S; while(x){uint32_t b=x&-x;int i=__builtin_ctz(b); if(!(o[i]&S)&&ac[S^b]){ac[S]=1;break;} x^=b;}
  if(ac[S]){int c=__builtin_popcount(S); if(c>best)best=c;}}
 printf("%d\n",best); return 0;}
