// impl A common: E8 positive roots (Bourbaki simple-root coords, K579T typB convention), 9-bit labels, maximal 7-flat masks, simple reflections on lines
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u;
static inline int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int A[8][8]={{2,0,-1,0,0,0,0,0},{0,2,0,-1,0,0,0,0},{-1,0,2,-1,0,0,0,0},{0,-1,-1,2,-1,0,0,0},{0,0,0,-1,2,-1,0,0},{0,0,0,0,-1,2,-1,0},{0,0,0,0,0,-1,2,-1},{0,0,0,0,0,0,-1,2}};
int rt[120][8],nr=0,lab[120],refl[8][120];u*M;int NM;
int find(int*v){for(int i=0;i<nr;i++)if(!memcmp(rt[i],v,32))return i;int w[8];for(int j=0;j<8;j++)w[j]=-v[j];for(int i=0;i<nr;i++)if(!memcmp(rt[i],w,32))return i;return -1;}
int cmpu(const void*a,const void*b){u x=*(u*)a,y=*(u*)b;return x<y?-1:x>y;}
int ip(int*x,int*y){int s=0;for(int i=0;i<8;i++)for(int j=0;j<8;j++)s+=x[i]*A[i][j]*y[j];return s;}
u act(int i,u m){u r=0;for(int t=0;t<120;t++)if((m>>t)&1)r|=(u)1<<refl[i][t];return r;}
void build(){for(int i=0;i<8;i++){memset(rt[nr],0,32);rt[nr][i]=1;nr++;}
 for(int q=0;q<nr;q++)for(int i=0;i<8;i++){int k=0;for(int j=0;j<8;j++)k+=rt[q][j]*A[j][i];int v[8];memcpy(v,rt[q],32);v[i]-=k;
  int pos=1;for(int j=0;j<8;j++)if(v[j]<0)pos=0;int nz=0;for(int j=0;j<8;j++)nz|=v[j];if(pos&&nz&&find(v)<0)memcpy(rt[nr++],v,32);}
 for(int t=0;t<120;t++){lab[t]=256;for(int j=0;j<8;j++)lab[t]|=(rt[t][j]&1)<<j;}
 for(int i=0;i<8;i++)for(int t=0;t<120;t++){int k=0;for(int j=0;j<8;j++)k+=rt[t][j]*A[j][i];int v[8];memcpy(v,rt[t],32);v[i]-=k;refl[i][t]=find(v);}
 u*ms=malloc(130816*sizeof(u));int nm=0;
 for(int f=1;f<512;f++)for(int g=f+1;g<512;g++){u x=0;for(int t=0;t<120;t++)if(!(__builtin_popcount(f&lab[t])&1)&&!(__builtin_popcount(g&lab[t])&1))x|=(u)1<<t;ms[nm++]=x;}
 qsort(ms,nm,sizeof(u),cmpu);int w=0;for(int i=0;i<nm;i++)if(!w||ms[w-1]!=ms[i])ms[w++]=ms[i];nm=w;
 M=malloc(nm*sizeof(u));NM=0;for(int i=0;i<nm;i++){int sub=0;for(int j=0;j<nm&&!sub;j++)if(j!=i&&(ms[i]&ms[j])==ms[i])sub=1;if(!sub)M[NM++]=ms[i];}
 qsort(M,NM,sizeof(u),cmpu);free(ms);}
int mfind(u x){int lo=0,hi=NM-1;while(lo<=hi){int m=(lo+hi)/2;if(M[m]==x)return m;if(M[m]<x)lo=m+1;else hi=m-1;}return -1;}
u offS(int S){u o=0;for(int t=0;t<120;t++)for(int i=0;i<8;i++)if(((S>>i)&1)&&rt[t][i])o|=(u)1<<t;return o;} // Off of dominant h with support S
// W-orbit of a line-mask under simple reflections
int orbit(u m,u**out){int cap=1<<16,n=1;u*o=malloc(cap*sizeof(u));o[0]=m;
 for(int q=0;q<n;q++)for(int i=0;i<8;i++){u y=act(i,o[q]);int f=0;for(int k=n-1;k>=0&&!f;k--)if(o[k]==y)f=1;if(!f){if(n==cap){cap*=2;o=realloc(o,cap*sizeof(u));}o[n++]=y;}}
 *out=o;return n;}
