// impl B: Off(omega_i) = positive roots with nonzero alpha_i coefficient (Bourbaki), min_{La,Lb} |Off\(La u Lb)|; masks rebuilt independently.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u;
static inline int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int A[8][8]={{2,0,-1,0,0,0,0,0},{0,2,0,-1,0,0,0,0},{-1,0,2,-1,0,0,0,0},{0,-1,-1,2,-1,0,0,0},{0,0,0,-1,2,-1,0,0},{0,0,0,0,-1,2,-1,0},{0,0,0,0,0,-1,2,-1},{0,0,0,0,0,0,-1,2}};
int rt[120][8],nr=0,lab[120];
int find(int*v){for(int i=0;i<nr;i++)if(!memcmp(rt[i],v,32))return i;return -1;}
int cmpu(const void*a,const void*b){u x=*(u*)a,y=*(u*)b;return x<y?-1:x>y;}
int main(){for(int i=0;i<8;i++){memset(rt[nr],0,32);rt[nr][i]=1;nr++;}
 for(int q=0;q<nr;q++)for(int i=0;i<8;i++){int k=0;for(int j=0;j<8;j++)k+=rt[q][j]*A[j][i];int v[8];memcpy(v,rt[q],32);v[i]-=k;
  int pos=1;for(int j=0;j<8;j++)if(v[j]<0)pos=0;int nz=0;for(int j=0;j<8;j++)nz|=v[j];if(pos&&nz&&find(v)<0)memcpy(rt[nr++],v,32);}
 for(int t=0;t<120;t++){lab[t]=256;for(int j=0;j<8;j++)lab[t]|=(rt[t][j]&1)<<j;}
 u*ms=malloc(130816*sizeof(u));int nm=0;
 for(int f=1;f<512;f++)for(int g=f+1;g<512;g++){u x=0;for(int t=0;t<120;t++)if(!(__builtin_popcount(f&lab[t])&1)&&!(__builtin_popcount(g&lab[t])&1))x|=(u)1<<t;ms[nm++]=x;}
 qsort(ms,nm,sizeof(u),cmpu);int w=0;for(int i=0;i<nm;i++)if(!w||ms[w-1]!=ms[i])ms[w++]=ms[i];nm=w;
 u*M=malloc(nm*sizeof(u));int NM=0;for(int i=0;i<nm;i++){int sub=0;for(int j=0;j<nm&&!sub;j++)if(j!=i&&(ms[i]&ms[j])==ms[i])sub=1;if(!sub)M[NM++]=ms[i];}
 printf("roots %d masks %d\n",nr,NM);
 for(int i=0;i<8;i++){u off=0;for(int t=0;t<120;t++)if(rt[t][i])off|=(u)1<<t;int best=999;
  for(int a=0;a<NM;a++){u R=off&~M[a];if(pc(R)-36>=best)continue;for(int b=0;b<NM;b++){int c=pc(R&~M[b]);if(c<best)best=c;}}
  printf("node %d |Off| %d min leftover %d\n",i+1,pc(off),best);fflush(stdout);}}
