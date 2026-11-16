/* AUD-2: min over pairs of 7-flats of |Off(h) \ (La u Lb)| for given h (doubled coords). Same labels as cov.c. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 M;
static int R[120][8],nl=0; static unsigned char lab[120]; static M ptmask[256];
static int pc(M x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static void addroot(int*v){int i=0;while(!v[i])i++;if(v[i]<0)return;memcpy(R[nl],v,sizeof(int)*8);nl++;}
static int ip(int*a,int*b){int s=0;for(int i=0;i<8;i++)s+=a[i]*b[i];return s;}
static M F[50000]; static int nF=0; static unsigned char basis[8];
static int rrefok(int k){int pm[8];for(int i=0;i<k;i++){int b=7;while(!((basis[i]>>b)&1))b--;pm[i]=b;}for(int i=0;i<k;i++)for(int j=0;j<k;j++)if(i!=j&&((basis[i]>>pm[j])&1))return 0;return 1;}
static void cosets(int k){unsigned char span[256];int ns=1;span[0]=0;for(int i=0;i<k;i++){for(int j=0;j<ns;j++)span[ns+j]=span[j]^basis[i];ns*=2;}
 int piv=0;for(int i=0;i<k;i++){int b=7;while(!((basis[i]>>b)&1))b--;piv|=1<<b;}
 for(int t=0;t<256;t++){if(t&piv)continue;M m=0;for(int j=0;j<ns;j++)m|=ptmask[t^span[j]];F[nF++]=m;}}
static void rec(int k,int i,int lp){if(i==k){if(rrefok(k))cosets(k);return;}
 for(int p=lp-1;p>=k-1-i;p--){int pm=0;for(int j=0;j<i;j++){int b=7;while(!((basis[j]>>b)&1))b--;pm|=1<<b;}
  int fp[8],nf=0;for(int b=0;b<p;b++)if(!((pm>>b)&1))fp[nf++]=b;
  for(int f=0;f<(1<<nf);f++){unsigned char v=1<<p;for(int j=0;j<nf;j++)if((f>>j)&1)v|=1<<fp[j];basis[i]=v;rec(k,i+1,p);}}}
int main(int argc,char**argv){int v[8];
 for(int i=0;i<8;i++)for(int j=i+1;j<8;j++)for(int si=-1;si<=1;si+=2)for(int sj=-1;sj<=1;sj+=2){memset(v,0,sizeof v);v[i]=2*si;v[j]=2*sj;addroot(v);}
 for(int s=0;s<256;s++){if(__builtin_popcount(s)&1)continue;for(int i=0;i<8;i++)v[i]=((s>>i)&1)?-1:1;addroot(v);}
 int B[8][8];memset(B,0,sizeof B);B[0][0]=4;for(int i=1;i<7;i++){B[i][i-1]=-2;B[i][i]=2;}for(int i=0;i<8;i++)B[7][i]=1;
 for(int l=0;l<120;l++){unsigned char x=0;for(int i=0;i<8;i++){int s=ip(R[l],B[i]);if(((s/4)%2+2)%2)x|=1<<i;}lab[l]=x;ptmask[x]|=(M)1<<l;}
 rec(6,0,8); fprintf(stderr,"7-flats %d\n",nF);
 int h[8]; for(int i=0;i<8;i++) h[i]=atoi(argv[1+i]); int excl=argc>9; /* 9th arg: exclude lines parallel to h (root covered) */
 M OFF=0; int nperp=0; for(int l=0;l<120;l++){ if(ip(R[l],h)) OFF|=(M)1<<l; else nperp++; }
 if(excl) for(int l=0;l<120;l++){ int par=1; /* R[l] parallel h? */ for(int i=0;i<8;i++)for(int j=0;j<8;j++) if(R[l][i]*h[j]!=R[l][j]*h[i]) par=0; if(par) OFF&=~((M)1<<l);}
 int hist[130]={0}; int best=999;
 static M G[50000]; int nG=0; for(int i=0;i<nF;i++){M m=F[i]&OFF; int dom=0; G[nG++]=m;}
 for(int i=0;i<nG;i++){M a=G[i]; for(int j=i;j<nG;j++){int c=pc(OFF&~(a|G[j])); if(c<best)best=c; if(c<=24)hist[c]++;}}
 printf("|Off|=%d perp-lines=%d min leftover=%d ; counts(<=24):",pc(OFF),nperp,best); for(int c=0;c<=24;c++) if(hist[c]) printf(" %d:%d",c,hist[c]); printf("\n"); return 0;}
