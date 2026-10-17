// T3+1 (impl A): for each maximal rank-7 Levi type (tri7.in Off sets), is Off(h) \ {l} coverable by three 7-flats for some line l?
// Exhaustive over all pairs (A,B) of maximal masks (no pruning); test leftover L=T\(A|B): exists l in L (or none) with rank(L\l)<=7.
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128; int lab[120]; int par(int x){return __builtin_parity(x);}
int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int rk(u128 x){int b[9]={0},nb=0; for(int t=0;t<120;t++) if((x>>t)&1){int v=lab[t]; for(int i=0;i<nb;i++){int w=v^b[i]; if(w<v)v=w;} if(v){b[nb++]=v; for(int i=nb-1;i>0&&b[i]>b[i-1];i--){int s=b[i];b[i]=b[i-1];b[i-1]=s;}}} return nb;}
static u128 F[140000]; int nf=0;
int cmp(const void*a,const void*b){int x=pc(*(u128*)a),y=pc(*(u128*)b); return y-x;}
int main(){FILE*f=fopen("tri7.in","r"); for(int t=0;t<120;t++) fscanf(f,"%d",&lab[t]);
 for(int a=1;a<512;a++) for(int b=a+1;b<512;b++){u128 m=0; for(int t=0;t<120;t++) if(!par(a&lab[t])&&!par(b&lab[t])) m|=((u128)1)<<t; F[nf++]=m;}
 int k,sz; while(fscanf(f,"%d %d",&k,&sz)==2){u128 T=0; for(int i=0;i<sz;i++){int t; fscanf(f,"%d",&t); T|=((u128)1)<<t;}
  static u128 G[140000],H[140000]; int ng=0,nh=0; for(int i=0;i<nf;i++) G[ng++]=F[i]&T; qsort(G,ng,sizeof(u128),cmp);
  for(int i=0;i<ng;i++){int dom=0; for(int j=0;j<nh;j++) if((G[i]&H[j])==G[i]){dom=1;break;} if(!dom) H[nh++]=G[i];}
  int minrk=99; long cov0=0,cov1=0;
  for(int i=0;i<nh;i++) for(int j=i;j<nh;j++){u128 L=T&~(H[i]|H[j]); int sl=pc(L); if(sl>37) continue; int r=rk(L); if(r<minrk)minrk=r;
    if(r<=7){cov0++;continue;} if(r==8){ for(int t=0;t<120;t++) if((L>>t)&1){ if(rk(L&~(((u128)1)<<t))<=7){cov1++;break;} } } }
  printf("type k=%d |Off|=%d maxmasks=%d minrank(|L|<=37)=%d  pairs covering: plain %ld, with one extra line %ld\n",k,sz,nh,minrk,cov0,cov1); fflush(stdout);}
}
