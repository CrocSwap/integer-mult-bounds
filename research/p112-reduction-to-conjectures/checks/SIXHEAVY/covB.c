// SIXHEAVY impl B: cover of a line set O (E8 lines) by flats of given dims.
// Flats generated as PRIMAL spans (RREF bases, all 2^w elements), unlike impl A (dual kernels).
// stdin: 120 labels (9-bit ints); k, then k line indices (O); m, then m dims.  stdout: COVER <dims+line lists> | NONE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef unsigned __int128 u128;
static int lab2line[512];
static u128 O; static int nO;
static int pc(u128 x){ return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64)); }
typedef struct { u128 *m; int n, cap; int **per; int *pn; int G; } FL;
static FL F[10];
static int cmpm(const void*a,const void*b){ u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:x>y?1:0; }
static void gen(int w, int mn){
  FL *f=&F[w]; f->n=0; f->cap=1<<16; f->m=malloc(sizeof(u128)*f->cap);
  int piv[9];
  // iterate pivot sets
  for(int ps=0; ps<512; ps++){ if(__builtin_popcount(ps)!=w) continue;
    int k=0; for(int c=0;c<9;c++) if(ps>>c&1) piv[k++]=c;
    // free positions: (r,c) with c>piv[r], c not a pivot
    int fr[64],fc[64],nf=0;
    for(int r=0;r<w;r++) for(int c=piv[r]+1;c<9;c++) if(!(ps>>c&1)){fr[nf]=r;fc[nf]=c;nf++;}
    for(long b=0;b<(1L<<nf);b++){
      int rows[9]; for(int r=0;r<w;r++) rows[r]=1<<piv[r];
      for(int t=0;t<nf;t++) if(b>>t&1) rows[fr[t]]|=1<<fc[t];
      u128 m=0; for(int s=0;s<(1<<w);s++){ int v=0; for(int r=0;r<w;r++) if(s>>r&1) v^=rows[r]; if(lab2line[v]>=0) m|=(u128)1<<lab2line[v]; }
      m&=O; if(pc(m)<mn||m==0) continue;
      if(f->n==f->cap){ f->cap*=2; f->m=realloc(f->m,sizeof(u128)*f->cap); }
      f->m[f->n++]=m;
    }
  }
  qsort(f->m,f->n,sizeof(u128),cmpm); int u=0; for(int i=0;i<f->n;i++) if(u==0||f->m[i]!=f->m[u-1]) f->m[u++]=f->m[i]; f->n=u;
  f->G=0; for(int i=0;i<f->n;i++) if(pc(f->m[i])>f->G) f->G=pc(f->m[i]);
  f->per=malloc(sizeof(int*)*128); f->pn=calloc(128,sizeof(int));
  for(int i=0;i<f->n;i++) for(int l=0;l<128;l++) if(f->m[i]>>l&1) f->pn[l]++;
  for(int l=0;l<128;l++){ f->per[l]=malloc(sizeof(int)*(f->pn[l]+1)); f->pn[l]=0; }
  for(int i=0;i<f->n;i++) for(int l=0;l<128;l++) if(f->m[i]>>l&1) f->per[l][f->pn[l]++]=i;
}
static int rem[10]; static long nodes=0;
static int chw[16]; static u128 chm[16]; static int depth=0;
#define HS (1<<22)
static u128 *hU; static int *hR;
static int rcode(){ int c=0; for(int w=1;w<=8;w++) c=c*13+rem[w]; return c+1; }
static int seenf(u128 U){ int rc=rcode(); uint64_t h=((uint64_t)U*0x9E3779B97F4A7C15ULL ^ (uint64_t)(U>>64)*0xC2B2AE3D27D4EB4FULL ^ rc*0x165667B1ULL)&(HS-1);
  for(int t=0;t<64;t++){ int i=(h+t)&(HS-1); if(hR[i]==0) return 0; if(hR[i]==rc&&hU[i]==U) return 1; } return 0; }
static void addf(u128 U){ int rc=rcode(); uint64_t h=((uint64_t)U*0x9E3779B97F4A7C15ULL ^ (uint64_t)(U>>64)*0xC2B2AE3D27D4EB4FULL ^ rc*0x165667B1ULL)&(HS-1);
  for(int t=0;t<64;t++){ int i=(h+t)&(HS-1); if(hR[i]==0){hR[i]=rc;hU[i]=U;return;} } }
static int rec(u128 U){
  if(U==0) return 1;
  int tot=0, any=0; for(int w=1;w<=8;w++) if(rem[w]){ any=1; tot+=rem[w]*F[w].G; }
  if(!any) return 0; int u=pc(U); if(tot<u) return 0;
  if(seenf(U)) return 0; nodes++;
  int bl=-1, bc=1<<30;
  for(int l=0;l<128;l++) if(U>>l&1){ int c=0; for(int w=1;w<=8;w++) if(rem[w]) c+=F[w].pn[l]; if(c<bc){bc=c;bl=l;} }
  for(int w=8;w>=1;w--) if(rem[w]){
    int need=u-(tot-F[w].G); rem[w]--;
    for(int t=0;t<F[w].pn[bl];t++){ u128 m=F[w].m[F[w].per[bl][t]];
      if(pc(m&U)<need) continue;
      chw[depth]=w; chm[depth]=m; depth++;
      if(rec(U&~m)) return 1;
      depth--; }
    rem[w]++;
  }
  addf(U); return 0;
}
int main(){
  int labs[120]; for(int i=0;i<120;i++) if(scanf("%d",&labs[i])!=1) return 2;
  memset(lab2line,-1,sizeof lab2line); for(int i=0;i<120;i++) lab2line[labs[i]]=i;
  int k; scanf("%d",&k); O=0; for(int i=0;i<k;i++){int x; scanf("%d",&x); O|=(u128)1<<x;} nO=pc(O);
  int m; scanf("%d",&m); int dims[16]; memset(rem,0,sizeof rem); for(int i=0;i<m;i++){ scanf("%d",&dims[i]); rem[dims[i]]++; }
  // static need per dim: G_w computed from an unfiltered pass would cost time; use g-table upper bounds for the filter
  int g[9]={0,1,2,4,8,12,20,36,64}; int tot=0; for(int i=0;i<m;i++) tot+=g[dims[i]];
  for(int w=1;w<=8;w++) if(rem[w]){ int mn=nO-(tot-g[w]); gen(w, mn<1?1:mn); }
  hU=calloc(HS,sizeof(u128)); hR=calloc(HS,sizeof(int));
  for(int w=1;w<=8;w++) if(rem[w]) fprintf(stderr,"w=%d n=%d G=%d\n",w,F[w].n,F[w].G);
  int r=rec(O);
  if(r){ printf("COVER"); for(int i=0;i<depth;i++){ printf(" %d:",chw[i]); for(int l=0;l<128;l++) if(chm[i]>>l&1) printf("%d,",l);} printf("\n"); }
  else printf("NONE nodes=%ld\n",nodes);
  return 0;
}
