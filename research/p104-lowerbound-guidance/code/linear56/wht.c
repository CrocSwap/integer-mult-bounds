/* LINEAR56 wht.c: for a family of subspaces span_t of F2^28 (given by generators), compute for every omega in F2^28
   good(omega) = #{t : omega . chi = 0 for all chi in span_t}, via Walsh-Hadamard. Prints max over omega != 0 and argmax.
   input (stdin): T, then for each t: r and r generator ints (independent). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(){
  const int N=28; const size_t S=(size_t)1<<N;
  int32_t *A=calloc(S,sizeof(int32_t)); if(!A){fprintf(stderr,"oom\n");return 1;}
  int T; if(scanf("%d",&T)!=1) return 1;
  for(int t=0;t<T;t++){ int r; scanf("%d",&r); unsigned g[32]; for(int i=0;i<r;i++) scanf("%u",&g[i]);
    int w=1<<(7-r>=0?7-r:0); if(r>7){fprintf(stderr,"r>7\n");return 1;}
    for(unsigned m=0;m<(1u<<r);m++){ unsigned x=0; for(int i=0;i<r;i++) if(m>>i&1) x^=g[i]; A[x]+=w; } }
  for(size_t h=1;h<S;h<<=1) for(size_t i=0;i<S;i+=h<<1) for(size_t j=i;j<i+h;j++){ int32_t a=A[j],b=A[j+h]; A[j]=a+b; A[j+h]=a-b; }
  int32_t best=-1; size_t arg=0; long hist[110]={0};
  for(size_t o=1;o<S;o++){ int32_t v=A[o]/128; if(v>best){best=v;arg=o;} if(v>=0&&v<110) hist[v]++; }
  printf("max_good %d argmax %zu\n",best,arg);
  for(int v=60;v<110;v++) if(hist[v]) printf("good=%d count=%ld\n",v,hist[v]);
  free(A); return 0; }
