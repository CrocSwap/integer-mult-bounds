// TU-signability of binary matrix via Camion: all square Eulerian submatrices sum = 0 mod 4 (linear system over F2).
// input: nr nc, then nr rows as bitmasks (decimal over nc bits). output 1 signable /0
#include <stdio.h>
#include <stdint.h>
#include <string.h>
typedef unsigned __int128 u128;
int nr,nc; uint32_t row[20]; int vid[20][20]; int nv=0;
uint64_t basis[128]; int brhs[128]; // pivot by highest bit; vars <=64 -> use u128? use u128
u128 bs[128]; int br[128]; int havep[128];
int addeq(u128 e,int rhs){ // returns 0 if inconsistent
  for(int b=127;b>=0;b--){ if(!((e>>b)&1))continue; if(havep[b]){e^=bs[b];rhs^=br[b];} else {havep[b]=1;bs[b]=e;br[b]=rhs;return 1;} }
  return rhs==0; }
int main(){scanf("%d %d",&nr,&nc);for(int i=0;i<nr;i++){unsigned x;scanf("%u",&x);row[i]=x;}
 for(int i=0;i<nr;i++)for(int j=0;j<nc;j++)if(row[i]>>j&1)vid[i][j]=nv++; 
 if(nv>127){printf("-1\n");return 0;}
 for(uint32_t S=1;S<(1u<<nr);S++){ uint32_t x=0;int k=__builtin_popcount(S);
   for(int i=0;i<nr;i++)if(S>>i&1)x^=row[i];
   uint32_t Z=((1u<<nc)-1)&~x; // columns with even degree inside S
   // T submask of Z with popcount k
   for(uint32_t T=Z;;T=(T-1)&Z){ if(__builtin_popcount(T)==k){ int ok=1;
        for(int i=0;i<nr&&ok;i++)if(S>>i&1)if(__builtin_popcount(row[i]&T)&1)ok=0;
        if(ok){u128 e=0;int cnt=0;for(int i=0;i<nr;i++)if(S>>i&1)for(int j=0;j<nc;j++)if(T>>j&1&&(row[i]>>j&1)){e|=(u128)1<<vid[i][j];cnt++;}
          if(!addeq(e,(cnt/2)&1)){printf("0\n");return 0;} } }
      if(T==0)break; } }
 printf("1\n");return 0;}
