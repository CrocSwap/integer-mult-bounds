/* AUD-2 independent cover checker. Lines = 120 E8 root lines; label = class mod 2E8 as GF(2)^8 via
   inner products with the Conway-Sloane E8 basis (2e1, e2-e1,...,e7-e6, (1/2)^8) mod 2. A w-flat = affine (w-1)-subspace
   of GF(2)^8 (labels (1,rbar)). Off(h) = root lines with <h,r> != 0 over Q.
   usage: cov TARGET w1 w2 ...  TARGET in {root, d7}. prints COVER (with witness check) or NONE. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 M;
static int R[120][8]; /* doubled coords */
static int nl=0; static unsigned char lab[120]; static M ptmask[256];
static M OFF; static int noff;
static int pc(M x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static int gtab[9]={0,1,2,4,8,12,20,36,64};
typedef struct {M m; int c;} Fl;
static Fl *L[9]; static int nL[9], capL[9];
static int want[16], nw, slack;
static void addroot(int*v){ /* keep one of +-r: first nonzero coord positive */
  int i=0; while(!v[i]) i++; if(v[i]<0) return; memcpy(R[nl],v,sizeof(int)*8); nl++; }
static int ip2(int*a,int*b){int s=0;for(int i=0;i<8;i++)s+=a[i]*b[i];return s;} /* 4*<a,b> */
static int dimk; static unsigned char basis[8]; static int cnt;
static void addfl(int w,M m){ int c=pc(m&OFF); if(c<1) return; if(c<gtab[w]-slack) return;
  if(nL[w]==capL[w]){capL[w]=capL[w]?2*capL[w]:1024; L[w]=realloc(L[w],sizeof(Fl)*capL[w]);} L[w][nL[w]].m=m&OFF; L[w][nL[w]].c=c; nL[w]++; }
/* enumerate linear k-subspaces in RREF; pivots chosen increasing */
static void cosets(int w,int k){ unsigned char span[256]; int ns=1; span[0]=0;
  for(int i=0;i<k;i++){ for(int j=0;j<ns;j++) span[ns+j]=span[j]^basis[i]; ns*=2; }
  int piv=0; for(int i=0;i<k;i++){ int b=7; while(!((basis[i]>>b)&1)) b--; piv|=1<<b; }
  for(int t=0;t<256;t++){ if(t&piv) continue; M m=0; for(int j=0;j<ns;j++) m|=ptmask[t^span[j]]; addfl(w,m); } }
static void rec(int w,int k,int i,int lastpiv){ /* basis[i] has leading bit < lastpiv */
  if(i==k){ /* reduce: ensure RREF (pivot cols zero in other rows) */ cosets(w,k); cnt++; return; }
  for(int p=lastpiv-1;p>=k-1-i;p--){
    /* free bits: bits < p that are not pivots of earlier rows... we build with full reduction afterwards: choose free bits among non-pivot positions below p */
    int pivmask=0; for(int j=0;j<i;j++){int b=7; while(!((basis[j]>>b)&1)) b--; pivmask|=1<<b;}
    int freepos[8],nf=0; for(int b=0;b<p;b++) if(!((pivmask>>b)&1)) freepos[nf++]=b;
    /* later pivots (below p) will clear their columns: to keep canonical form we allow free bits only in non-pivot positions; later rows' pivots must avoid positions where we put bits? standard RREF: entries in pivot columns of later rows must be 0. We enforce by post-check. */
    for(int f=0;f<(1<<nf);f++){ unsigned char v=1<<p; for(int j=0;j<nf;j++) if((f>>j)&1) v|=1<<freepos[j]; basis[i]=v; rec(w,k,i+1,p); }
  }
}
static int rrefok(int k){ int pm[8]; for(int i=0;i<k;i++){int b=7; while(!((basis[i]>>b)&1)) b--; pm[i]=b;}
  for(int i=0;i<k;i++) for(int j=0;j<k;j++) if(i!=j && ((basis[i]>>pm[j])&1)) return 0; return 1; }
static void rec2(int w,int k,int i,int lastpiv){
  if(i==k){ if(rrefok(k)){cosets(w,k);cnt++;} return; }
  for(int p=lastpiv-1;p>=k-1-i;p--){ int pivmask=0; for(int j=0;j<i;j++){int b=7; while(!((basis[j]>>b)&1)) b--; pivmask|=1<<b;}
    int freepos[8],nf=0; for(int b=0;b<p;b++) if(!((pivmask>>b)&1)) freepos[nf++]=b;
    for(int f=0;f<(1<<nf);f++){ unsigned char v=1<<p; for(int j=0;j<nf;j++) if((f>>j)&1) v|=1<<freepos[j]; basis[i]=v; rec2(w,k,i+1,p);} } }
static long nodes=0; static int sol[16]; static M solm[16];
static int dfs(M unc,int *rem,int depth){
  nodes++; if(!unc) return 1;
  int capsum=0; for(int w=1;w<=8;w++) capsum+=rem[w]*gtab[w]; if(pc(unc)>capsum) return 0;
  /* lowest uncovered line */
  int t=0; while(!((unc>>t)&1)) t++; M bit=(M)1<<t;
  for(int w=8;w>=1;w--) if(rem[w]){ rem[w]--;
    int cs=0; for(int u=1;u<=8;u++) cs+=rem[u]*gtab[u];
    for(int i=0;i<nL[w];i++){ M m=L[w][i].m; if(!(m&bit)) continue; M nu=unc&~m; if(pc(nu)>cs) continue;
      sol[depth]=w; solm[depth]=m; if(dfs(nu,rem,depth+1)){rem[w]++; return 1;} }
    rem[w]++; }
  return 0;
}
int main(int argc,char**argv){
  int v[8];
  for(int i=0;i<8;i++)for(int j=i+1;j<8;j++)for(int si=-1;si<=1;si+=2)for(int sj=-1;sj<=1;sj+=2){memset(v,0,sizeof v);v[i]=2*si;v[j]=2*sj;addroot(v);}
  for(int s=0;s<256;s++){ if(__builtin_popcount(s)&1) continue; for(int i=0;i<8;i++) v[i]=((s>>i)&1)?-1:1; addroot(v);}
  if(nl!=120){printf("bad nl %d\n",nl);return 1;}
  int B[8][8]; memset(B,0,sizeof B); B[0][0]=4; for(int i=1;i<7;i++){B[i][i-1]=-2;B[i][i]=2;} for(int i=0;i<8;i++)B[7][i]=1;
  for(int l=0;l<120;l++){ unsigned char x=0; for(int i=0;i<8;i++){ int s=ip2(R[l],B[i]); /* =4<r,b> */ if(s%4){printf("nonint\n");return 1;} if(((s/4)%2+2)%2) x|=1<<i; } lab[l]=x; }
  for(int a=0;a<120;a++)for(int b=a+1;b<120;b++) if(lab[a]==lab[b]){printf("dup label\n");return 1;}
  for(int l=0;l<120;l++) ptmask[lab[l]]|=(M)1<<l;
  int h[8]={0}; if(!strcmp(argv[1],"root")){h[0]=2;h[1]=2;} else if(!strcmp(argv[1],"e6")){h[5]=1;h[6]=3;h[7]=4;} else {h[0]=2;}
  OFF=0; for(int l=0;l<120;l++) if(ip2(R[l],h)) OFF|=(M)1<<l; noff=pc(OFF);
  if(!strcmp(argv[1],"gtab")){ OFF=~(M)0>>8; slack=1000; for(int w=1;w<=8;w++){ rec2(w,w-1,0,8); int mx=0; for(int i=0;i<nL[w];i++) if(L[w][i].c>mx) mx=L[w][i].c; printf("g(%d)=%d nflats=%d\n",w,mx,nL[w]); } return 0; }
  int rem[9]={0}; int caps=0; for(int i=2;i<argc;i++){int w=atoi(argv[i]); rem[w]++; caps+=gtab[w];}
  slack=caps-noff; printf("target %s |Off|=%d caps=%d slack=%d\n",argv[1],noff,caps,slack);
  if(slack<0){printf("NONE (cap)\n");return 0;}
  for(int w=1;w<=8;w++) if(rem[w]){ rec2(w,w-1,0,8); printf(" w=%d candidates %d\n",w,nL[w]); }
  int ok=dfs(OFF,rem,0);
  if(ok){ int d=0; for(int w=1;w<=8;w++) d+=rem[w]; M u=0; for(int i=0;i<d;i++) u|=solm[i]; printf("COVER witness ok=%d nodes=%ld\n",(u&OFF)==OFF,nodes);} else printf("NONE nodes=%ld\n",nodes);
  return 0;
}
