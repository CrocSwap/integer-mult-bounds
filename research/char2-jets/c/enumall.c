// exhaustive: input v f; f lines "t s"; for j: nR R.., nA A..; optional slack k: output all B with cost<=min+k (we output cost too)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int v,f,ft[64],fs[64],nR[3],nA[3],R[3][32],A[3][32];
uint32_t row[32];
static inline int rk(int j){uint32_t rows[32];int n=0;
 for(int a=0;a<nR[j];a++){uint32_t x=0;int t=R[j][a];for(int b=0;b<nA[j];b++){int s=A[j][b];if(row[t]>>s&1)x|=1u<<b;}rows[n++]=x;}
 int r=0;for(int i=0;i<n;i++){uint32_t x=rows[i];for(int k=0;k<r;k++){uint32_t y=rows[k];uint32_t hb=1u<<(31-__builtin_clz(y)); if(x&hb)x^=y;}
   if(x){ // insert keeping distinct leading bits: reduce others not needed for rank since we use highest-bit pivots sorted?
     rows[r++]=x; // ensure pivot uniqueness: sort by highest bit descending
     for(int k=r-1;k>0 && (31-__builtin_clz(rows[k]))>(31-__builtin_clz(rows[k-1]));k--){uint32_t tmp=rows[k];rows[k]=rows[k-1];rows[k-1]=tmp;}
   }}
 return r;}
int main(int argc,char**argv){int slack=argc>1?atoi(argv[1]):0;
 if(scanf("%d %d",&v,&f)!=2)return 1;for(int i=0;i<f;i++)scanf("%d %d",&ft[i],&fs[i]);
 for(int j=0;j<3;j++){scanf("%d",&nR[j]);for(int i=0;i<nR[j];i++)scanf("%d",&R[j][i]);scanf("%d",&nA[j]);for(int i=0;i<nA[j];i++)scanf("%d",&A[j][i]);}
 for(int t=0;t<v;t++)row[t]=1u<<t;
 uint64_t N=1ull<<f,g=0;int best=1000;
 size_t cap=1<<22, nm=0; uint64_t*ms=malloc(8*cap); int*cs=malloc(4*cap);
 for(uint64_t i=0;i<N;i++){
  if(i){int b=__builtin_ctzll(i);g^=1ull<<b;row[ft[b]]^=1u<<fs[b];}
  int c=rk(0)+rk(1)+rk(2);
  if(c<best){ // drop entries above new best+slack
    best=c; size_t m=0; for(size_t k=0;k<nm;k++) if(cs[k]<=best+slack){ms[m]=ms[k];cs[m]=cs[k];m++;} nm=m;}
  if(c<=best+slack && nm<cap){ms[nm]=g;cs[nm]=c;nm++;}
 }
 printf("%d %zu\n",best,nm);for(size_t k=0;k<nm;k++)printf("%d %llu\n",cs[k],(unsigned long long)ms[k]);}
