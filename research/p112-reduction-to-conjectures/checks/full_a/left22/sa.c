// unstructured max of served(E) over |E|<=c ; served = |E| + #roots not in E with leftover subset E + #D7 with leftover subset E
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef unsigned long long u64;
typedef struct{u64 lo,hi;}M;
static M *RM,*DM; static long nr,nd; int NB_R=9387,NB_D=6021;
static int szOK(M m,int c){return __builtin_popcountll(m.lo)+__builtin_popcountll(m.hi)<=c;}
int rootidx[120];
static M* load(const char*fn,long*n,int c,int per,int ntar){ FILE*f=fopen(fn,"rb");long tot=(long)per*ntar;M*a=malloc(tot*sizeof(M)*1);long k=0;static M tmp[1]; 
  // also record target id? roots: need target to avoid double counting: store target id in separate array
  M*all=malloc(tot*sizeof(M)); fread(all,sizeof(M),tot,f); fclose(f); for(long i=0;i<tot;i++) if(szOK(all[i],c)) a[k++]=all[i]; *n=k; free(all); return a;}
// targets: leftover masks grouped; to count distinct targets we keep tid arrays
static int *RT,*DT;
static long lc(const char*fn,M**out,int**tid,int c,int per,int ntar){FILE*f=fopen(fn,"rb");long tot=(long)per*ntar;M*all=malloc(tot*sizeof(M));fread(all,sizeof(M),tot,f);fclose(f);M*a=malloc(tot*sizeof(M));int*t=malloc(tot*4);long k=0;for(long i=0;i<tot;i++)if(szOK(all[i],c)){a[k]=all[i];t[k]=i/per;k++;}free(all);*out=a;*tid=t;return k;}
static char hitR[120],hitD[1080];
static int eval(M E,int c){
  memset(hitR,0,sizeof hitR);memset(hitD,0,sizeof hitD);int n=0;
  for(int r=0;r<120;r++){int t=rootidx[r];int in=t<64?(E.lo>>t)&1:(E.hi>>(t-64))&1;if(in){hitR[r]=1;n++;}}
  for(long i=0;i<nr;i++){int t=RT[i];if(hitR[t])continue;if((RM[i].lo&~E.lo)==0&&(RM[i].hi&~E.hi)==0){hitR[t]=1;n++;}}
  for(long i=0;i<nd;i++){int t=DT[i];if(hitD[t])continue;if((DM[i].lo&~E.lo)==0&&(DM[i].hi&~E.hi)==0){hitD[t]=1;n++;}}
  return n;}
static inline M tog(M E,int t){if(t<64)E.lo^=1ULL<<t;else E.hi^=1ULL<<(t-64);return E;}
static inline int has(M E,int t){return t<64?(E.lo>>t)&1:(E.hi>>(t-64))&1;}
int main(int argc,char**argv){int c=atoi(argv[1]);int iters=atoi(argv[2]);int seed=atoi(argv[3]);srand(seed);
  FILE*g=fopen("rootidx.txt","r");for(int i=0;i<120;i++)fscanf(g,"%d",&rootidx[i]);
  nr=lc("roots.bin",&RM,&RT,c,9387,120);nd=lc("d7.bin",&DM,&DT,c,6021,1080);fprintf(stderr,"masks %ld %ld\n",nr,nd);
  int best=0;M bestE;
  for(int rs=0;rs<iters;rs++){
    M E={0,0};int sz=0;int cur=0;
    while(1){ int bestv=-1;M bestU={0,0};int nb=0;
      for(int tr=0;tr<3000;tr++){ int pick=rand()%(nr+nd); M m=pick<nr?RM[pick]:DM[pick-nr]; M U={E.lo|m.lo,E.hi|m.hi};
        int s2=__builtin_popcountll(U.lo)+__builtin_popcountll(U.hi); if(s2>c||s2==sz)continue;
        // pad with arbitrary lines to c is irrelevant (monotone); evaluate U
        int v=eval(U,c); if(v>bestv||(v==bestv&&rand()%2)){bestv=v;bestU=U;} }
      if(bestv<0)break; E=bestU;sz=__builtin_popcountll(E.lo)+__builtin_popcountll(E.hi);cur=bestv; if(sz>=c)break; }
    // fill with arbitrary lines (monotone) then final
    cur=eval(E,c);
    if(cur>best){best=cur;bestE=E;fprintf(stderr,"restart %d best %d\n",rs,best);}
  }
  printf("c=%d max served found %d (|E| contributes %d)\n",c,best,c);
}
