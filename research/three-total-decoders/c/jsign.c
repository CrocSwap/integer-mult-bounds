// joint Camion system (extended for research/three-total-decoders: with argument 's' it also prints the solution as a line 'SIGN <bits>' after the flags line,
// bit i = 1 means the i-th one of B (row-major order) gets sign -1).  input v; v rows of B as bitmasks; then 3 blocks: nR R.., nA A..
// mode argv[1]: "j" joint (all blocks one system) -> prints "J b0 b1 b2" (J joint ok, bk block k ok)
#include <stdio.h>
#include <stdint.h>
#include <string.h>
typedef unsigned __int128 u128;
int v; uint32_t row[32]; int vid[32][32]; int nv;
int nR[3],nA[3],R[3][32],A[3][32];
u128 bs[128]; int br[128]; int havep[128];
static int addeq(u128 e,int rhs){for(int b=127;b>=0;b--){if(!((e>>b)&1))continue;if(havep[b]){e^=bs[b];rhs^=br[b];}else{havep[b]=1;bs[b]=e;br[b]=rhs;return 1;}}return rhs==0;}
static int block(int j){ // add all Camion eqs of block j; return 0 if inconsistent
  int nr=nR[j],nc=nA[j]; uint32_t rw[32];
  for(int a=0;a<nr;a++){uint32_t x=0;for(int b=0;b<nc;b++)if(row[R[j][a]]>>A[j][b]&1)x|=1u<<b;rw[a]=x;}
  for(uint32_t S=1;S<(1u<<nr);S++){uint32_t x=0;int k=__builtin_popcount(S);
    for(int i=0;i<nr;i++)if(S>>i&1)x^=rw[i];
    uint32_t Z=((nc==32)?0xffffffffu:((1u<<nc)-1))&~x;
    if(__builtin_popcount(Z)<k)continue;
    for(uint32_t T=Z;;T=(T-1)&Z){ if(__builtin_popcount(T)==k){int ok=1;
        for(int i=0;i<nr&&ok;i++)if(S>>i&1)if(__builtin_popcount(rw[i]&T)&1)ok=0;
        if(ok){u128 e=0;int cnt=0;for(int i=0;i<nr;i++)if(S>>i&1)for(int b=0;b<nc;b++)if(T>>b&1&&(rw[i]>>b&1)){e|=(u128)1<<vid[R[j][i]][A[j][b]];cnt++;}
          if(cnt && !addeq(e,(cnt/2)&1))return 0;}}
      if(T==0)break;}}
  return 1;}
static int popc128(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int main(int argc,char**argv){
 int sflag=argc>1&&argv[1][0]=='s';
 while(scanf("%d",&v)==1){
  for(int i=0;i<v;i++){unsigned x;scanf("%u",&x);row[i]=x;}
  for(int j=0;j<3;j++){scanf("%d",&nR[j]);for(int i=0;i<nR[j];i++)scanf("%d",&R[j][i]);scanf("%d",&nA[j]);for(int i=0;i<nA[j];i++)scanf("%d",&A[j][i]);}
  nv=0;for(int i=0;i<v;i++)for(int k=0;k<v;k++)if(row[i]>>k&1)vid[i][k]=nv++;
  if(nv>128){printf("-1\n");fflush(stdout);continue;}
  int bo[3];
  for(int j=0;j<3;j++){memset(havep,0,sizeof havep);bo[j]=block(j);}
  memset(havep,0,sizeof havep);int J=1;for(int j=0;j<3&&J;j++)J=block(j);
  printf("%d %d %d %d\n",J,bo[0],bo[1],bo[2]);
  if(sflag&&J){u128 x=0;for(int b=0;b<nv;b++)if(havep[b]){int val=br[b]^(popc128(bs[b]&x&~((u128)1<<b))&1);if(val)x|=(u128)1<<b;}
   printf("SIGN ");for(int b=0;b<nv;b++)putchar((x>>b&1)?'1':'0');putchar('\n');}
  fflush(stdout);}
 return 0;}
