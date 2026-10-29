// usage: srch ntarget capsmall nbig  w1 file1  w2 file2 ... (big weights descending, one entry per piece; file = text lines "lo hi")
// prints leaf residual masks (distinct) "lo hi" with popcount<=capsmall, and "FULL" if unc==0 reached
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
typedef struct {u64 lo,hi;} M;
int nb,capsmall; int *FIRST=0; int NF=0; int W[16]; M* C[16]; int NC[16]; int G[8]={0,1,2,4,8,12,20,36};
int capb[17];
#define HS (1u<<22)
M *HT; char *HU; long nleaf=0; long nodes=0;
static inline int pc(M a){return __builtin_popcountll(a.lo)+__builtin_popcountll(a.hi);}
void leaf(M u){
  u64 x=u.lo*0x9E3779B97F4A7C15ULL ^ (u.hi+7)*0xC2B2AE3D27D4EB4FULL; unsigned i=(x>>20)&(HS-1);
  while(HU[i]){ if(HT[i].lo==u.lo&&HT[i].hi==u.hi) return; i=(i+1)&(HS-1);} HU[i]=1;HT[i]=u; printf("%llu %llu\n",u.lo,u.hi); nleaf++;
}
void rec(int idx,M unc,int start){
  nodes++;
  int left=pc(unc);
  if(left==0){printf("FULL\n");return;}
  if(idx==nb){ if(left<=capsmall) leaf(unc); return;}
  int need=left-capb[idx+1]-capsmall; // capb[i]=sum of G[W[k]] for k>=i
  if(left>capb[idx]+capsmall) return;
  M*c=C[idx]; int n=NC[idx];
  int st=(idx>1&&W[idx-1]==W[idx])?start:0;
  int lim=(idx==0&&FIRST)?NF:n;
  for(int kk=st;kk<lim;kk++){
    int k=(idx==0&&FIRST)?FIRST[kk]:kk;
    M m=c[k];
    M u={unc.lo&~m.lo,unc.hi&~m.hi};
    if(left-pc(u)<need) continue;
    rec(idx+1,u,k);
  }
}
int main(int argc,char**argv){
  int nt=atoi(argv[1]); capsmall=atoi(argv[2]); nb=atoi(argv[3]);
  HT=malloc(sizeof(M)*HS); HU=calloc(HS,1);
  for(int i=0;i<nb;i++){ W[i]=atoi(argv[4+2*i]); FILE*f=fopen(argv[5+2*i],"r"); int cap=1<<20,n=0; M*a=malloc(sizeof(M)*cap);
    unsigned long long l,h; while(fscanf(f,"%llu %llu",&l,&h)==2){ if(n==cap){cap*=2;a=realloc(a,sizeof(M)*cap);} a[n].lo=l;a[n].hi=h;n++;} fclose(f); C[i]=a;NC[i]=n;}
  if(argc>4+2*nb){FILE*f=fopen(argv[4+2*nb],"r");FIRST=malloc(4*(1<<20));int x;while(fscanf(f,"%d",&x)==1)FIRST[NF++]=x;fclose(f);}
  capb[nb]=0; for(int i=nb-1;i>=0;i--) capb[i]=capb[i+1]+G[W[i]];
  M full; full.lo=nt>=64?~0ULL:((1ULL<<nt)-1); full.hi=nt>64?(nt>=128?~0ULL:((1ULL<<(nt-64))-1)):0;
  rec(0,full,0);
  fprintf(stderr,"nodes %ld leaves %ld\n",nodes,nleaf);
  return 0;
}
