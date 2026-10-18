// SIX3IND kernel (independent of SIX/s6x.c). usage: k3 data3.txt A B s lim chunk nchunk [refine3]
//  Pairs (V1,V2) of label flats of dims A,B (V1 up to frame-stabiliser orbit, V2 all). X = L(V1) u L(V2).
//  h qualifies iff exists 7-flat G with |(Off(h)\X)\G| <= s  (s=0: exact rank<=7; s>0: relaxed 'remove <=s lines per h').
//  Test via dual vectors: K={w1,w2,w1^w2} kills a set R of labels iff R in Z[w1]&Z[w2]; need |R&Z[w1]&Z[w2]|>=|R|-s.
//  Flats enumerated as duals W (greedy-min basis canonical), L(V)=AND of Z[w], w in W.   refine3: exact third 3-flat for relaxed rank>=8.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef __int128 i128; typedef unsigned long long u64;
static int LAB[112]; static u128 Z[512];
static int NGEN; static int GEN[32][112];
#define MAXD 6000
static int ND; static int kind[MAXD]; static long long V1v[MAXD][8], V2v[MAXD][8]; static u128 OFF[MAXD]; static int cap[MAXD];
static inline int pc(u128 x){ return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64)); }
// ---- flats
static u128 *OUT; static long long NOUT, CAPOUT;
static void rec(int d,int k,int *span,int nspan,int last,u128 m){
  if(d==k){ if(m){ if(NOUT>=CAPOUT){ CAPOUT*=2; OUT=realloc(OUT,CAPOUT*sizeof(u128)); } OUT[NOUT++]=m; } return; }
  for(int x=last+1;x<512;x++){
    int bad=0; for(int i=1;i<nspan;i++){ int y=x^span[i]; if(y<=x){ bad=1; break; } }   // x not in span (y==0 impossible-> y<x) and x min of coset
    if(bad) continue;
    int sp2[512]; for(int i=0;i<nspan;i++){ sp2[i]=span[i]; sp2[nspan+i]=span[i]^x; }
    rec(d+1,k,sp2,2*nspan,x,m&Z[x]);
  }
}
static int cmpu(const void*a,const void*b){ u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:(x>y); }
static u128 *flats(int dim,long long *n){ int k=9-dim; CAPOUT=1<<20; OUT=malloc(CAPOUT*sizeof(u128)); NOUT=0; int sp[1]={0}; u128 all=0; for(int t=0;t<112;t++) all|=((u128)1)<<t;
  rec(0,k,sp,1,0,all); qsort(OUT,NOUT,sizeof(u128),cmpu); long long u=0; for(long long i=0;i<NOUT;i++) if(i==0||OUT[i]!=OUT[i-1]) OUT[u++]=OUT[i]; *n=u; return OUT; }
// ---- qualifier
static int qual(u128 R,int s){ int c=pc(R); int need=c-s; if(need<=0) return 1;
  int cand[512]; int nc=0; for(int w=1;w<512;w++) if(pc(R&Z[w])>=need) cand[nc++]=w;
  for(int a=0;a<nc;a++){ u128 Ra=R&Z[cand[a]]; for(int b=a+1;b<nc;b++) if(pc(Ra&Z[cand[b]])>=need) return 1; }
  return 0; }
// ---- exact rational rank (integer elimination, gcd-normalised, int128)
static i128 gabs(i128 a){ return a<0?-a:a; }
static i128 gg(i128 a,i128 b){ a=gabs(a); b=gabs(b); while(b){ i128 t=a%b; a=b; b=t; } return a; }
static int rankQ(int *lst,int n){ i128 Bm[8][8]; int piv[8]; int r=0;
  for(int q=0;q<2*n && r<8;q++){ int h=lst[q/2]; if(q&1){ if(kind[h]!=2) continue; }
    i128 v[8]; for(int k=0;k<8;k++) v[k]= (q&1)? V2v[h][k]:V1v[h][k];
    for(int j=0;j<r;j++){ int p=piv[j]; if(v[p]==0) continue; i128 a=Bm[j][p], b=v[p]; i128 g=0; for(int k=0;k<8;k++){ v[k]=a*v[k]-b*Bm[j][k]; g=gg(g,v[k]); } if(g>1) for(int k=0;k<8;k++) v[k]/=g; }
    int p=-1; for(int k=0;k<8;k++) if(v[k]){ p=k; break; } if(p<0) continue;
    for(int k=0;k<8;k++) Bm[r][k]=v[k]; piv[r]=p; r++; }
  return r; }
// ---- mapping masks by generators
static u128 TB[32][14][256];
static void mktab(){ for(int g=0;g<NGEN;g++) for(int by=0;by<14;by++) for(int v=0;v<256;v++){ u128 o=0; for(int b=0;b<8;b++) if((v>>b)&1 && by*8+b<112) o|=((u128)1)<<GEN[g][by*8+b]; TB[g][by][v]=o; } }
static u128 mapm(u128 m,int g){ u128 o=0; for(int by=0;by<14;by++) o|=TB[g][by][(unsigned)((m>>(8*by))&255)]; return o; }
static long long fidx(u128 *A,long long n,u128 m){ long long lo=0,hi=n-1; while(lo<=hi){ long long mid=(lo+hi)/2; if(A[mid]==m) return mid; if(A[mid]<m) lo=mid+1; else hi=mid-1; } return -1; }
static int *uf; static int fnd(int x){ while(uf[x]!=x){ uf[x]=uf[uf[x]]; x=uf[x]; } return x; }
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); int A=atoi(argv[2]),B=atoi(argv[3]),s=atoi(argv[4]),lim=atoi(argv[5]),ch=atoi(argv[6]),nch=atoi(argv[7]); int refine=argc>8?atoi(argv[8]):0;
  for(int i=0;i<112;i++) fscanf(f,"%d",&LAB[i]);
  fscanf(f,"%d",&NGEN); for(int g=0;g<NGEN;g++) for(int t=0;t<112;t++) fscanf(f,"%d",&GEN[g][t]);
  int nn; fscanf(f,"%d",&nn); ND=0;
  for(int i=0;i<nn;i++){ int kd; long long a[8],b[8]; u64 lo,hi; int c; fscanf(f,"%d",&kd); for(int k=0;k<8;k++) fscanf(f,"%lld",&a[k]); for(int k=0;k<8;k++) fscanf(f,"%lld",&b[k]); fscanf(f,"%llu %llu %d",&lo,&hi,&c);
    if(c>lim) continue; kind[ND]=kd; for(int k=0;k<8;k++){ V1v[ND][k]=a[k]; V2v[ND][k]=b[k]; } OFF[ND]=((u128)hi<<64)|lo; if(pc(OFF[ND])!=c){ fprintf(stderr,"off count mismatch\n"); return 1; } ND++; }
  fclose(f);
  for(int w=0;w<512;w++){ Z[w]=0; for(int t=0;t<112;t++) if(!(__builtin_popcount(w&LAB[t])&1)) Z[w]|=((u128)1)<<t; }
  mktab();
  long long n7; u128 *F7=flats(7,&n7); u128 *F7c=malloc(n7*sizeof(u128)); memcpy(F7c,F7,n7*sizeof(u128)); free(OUT);
  for(int h=0;h<ND;h++){ int b=0; for(long long g=0;g<n7;g++){ int c=pc(OFF[h]&F7c[g]); if(c>b) b=c; } cap[h]=b; }
  long long na,nb; u128 *FA=flats(A,&na); u128 *FAc=malloc(na*sizeof(u128)); memcpy(FAc,FA,na*sizeof(u128)); free(OUT);
  u128 *FB; if(B==A){ FB=FAc; nb=na; } else { FB=flats(B,&nb); }
  int gwB=0; for(long long j=0;j<nb;j++){ int c=pc(FB[j]); if(c>gwB) gwB=c; }
  u128 *V3=NULL; long long n3=0; if(refine){ u128 *t=flats(3,&n3); V3=malloc(n3*sizeof(u128)); memcpy(V3,t,n3*sizeof(u128)); }
  fprintf(stderr,"ND %d 7flats %lld flatsA %lld flatsB %lld gwB %d V3 %lld\n",ND,n7,na,nb,gwB,n3);
  // orbits of V1
  uf=malloc(na*sizeof(int)); for(long long i=0;i<na;i++) uf[i]=i;
  for(long long i=0;i<na;i++) for(int g=0;g<NGEN;g++){ long long j=fidx(FAc,na,mapm(FAc[i],g)); if(j<0){ fprintf(stderr,"image not a flat\n"); return 1; } int x=fnd(i),y=fnd(j); if(x!=y) uf[x]=y; }
  int nrep=0; int *reps=malloc(na*sizeof(int)); int *osz=calloc(na,sizeof(int)); for(long long i=0;i<na;i++) osz[fnd(i)]++; for(long long i=0;i<na;i++) if(fnd(i)==i) reps[nrep++]=i;
  fprintf(stderr,"V1 orbits %d\n",nrep);
  int overall=0,maxn=0,refmax=0; long long hist[9]={0}; static int act[MAXD]; static u128 R1[MAXD]; static int lst[MAXD]; long long npairs8=0;
  for(int ri=0;ri<nrep;ri++){ if(ri%nch!=ch) continue; u128 X1=FAc[reps[ri]]; int nact=0, vmax=0;
    for(int h=0;h<ND;h++){ u128 r=OFF[h]&~X1; if(pc(r)<=cap[h]+gwB+s){ act[nact]=h; R1[nact]=r; nact++; } }
    for(long long j=0;j<nb;j++){ u128 X2=FB[j]; int n=0;
      for(int a=0;a<nact;a++){ u128 r=R1[a]&~X2; if(pc(r)>cap[act[a]]+s) continue; if(qual(r,s)) lst[n++]=act[a]; }
      if(n>maxn) maxn=n;
      if(n){ int rk=rankQ(lst,n); hist[rk]++; if(rk>vmax) vmax=rk;
        if(rk>=8){ npairs8++; printf("RANK%d rep %d j %lld n %d\n",rk,ri,j,n);
          if(refine){ int e=0; int bestq=-1; for(long long q=0;q<n3;q++){ u128 X=X1|X2|V3[q]; int m=0; static int l2[MAXD]; for(int c=0;c<n;c++){ int h=lst[c]; u128 r=OFF[h]&~X; if(pc(r)>cap[h]) continue; if(qual(r,0)) l2[m++]=h; } if(m){ int r2=rankQ(l2,m); if(r2>e){ e=r2; bestq=q; } } }
            printf("  REFINE exact-with-3flat max rank %d (V3 idx %d)\n",e,bestq); if(e>refmax) refmax=e; } } }
    }
    if(vmax>overall) overall=vmax; printf("rep %d lines %d orbit %d active %d maxrank %d\n",ri,pc(X1),osz[reps[ri]],nact,vmax); fflush(stdout);
  }
  printf("RESULT dims %d %d s %d lim %d chunk %d/%d: nreps %d, max relaxed rank %d, max #dirs %d, #pairs rank>=8: %lld, refine max exact rank %d; hist",A,B,s,lim,ch,nch,nrep,overall,maxn,npairs8,refmax);
  for(int r=1;r<=8;r++) printf(" %d:%lld",r,hist[r]); printf("\n");
  return 0; }
