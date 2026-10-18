// For every 7-dim label subspace F and target h: minimal removal sets X (|X|<=4) with Off(h)\F\X inside some 7-dim label subspace G.
// UBk(F) = #targets h having such an X of size <= k. Reports max over F for k=0..4.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
int lab[112]; int nt=0; int tl[2000][120]; int tn[2000];
static int par(int x){return __builtin_popcount(x)&1;}
int nG=0; u64 G0[43435],G1[43435];
int main(){
  FILE*f=fopen("labs.txt","r"); for(int i=0;i<112;i++) fscanf(f,"%d",&lab[i]); fclose(f);
  f=fopen("targets76.txt","r"); char line[4096];
  while(fgets(line,sizeof line,f)){ char*p=line; int n=0,x,c; while(sscanf(p,"%d%n",&x,&c)==1){tl[nt][n++]=x;p+=c;} if(n){tn[nt]=n;nt++;} } fclose(f);
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){
    int w3=w1^w2; int m1=w1<w2?w1:w2; m1=m1<w3?m1:w3; int M=w1>w2?w1:w2; M=M>w3?M:w3; int m2=w1+w2+w3-m1-M;
    if(!(m1==w1&&m2==w2)) continue;
    u64 a=0,b=0; for(int t=0;t<112;t++) if(!par(lab[t]&w1)&&!par(lab[t]&w2)){ if(t<64) a|=1ULL<<t; else b|=1ULL<<(t-64);} 
    G0[nG]=a; G1[nG]=b; nG++; }
  u64 H0[2000],H1[2000]; for(int h=0;h<nt;h++){H0[h]=H1[h]=0; for(int k=0;k<tn[h];k++){int t=tl[h][k]; if(t<64)H0[h]|=1ULL<<t; else H1[h]|=1ULL<<(t-64);} }
  int best[5]={0}; long hist[5][200]; memset(hist,0,sizeof hist);
  for(int F=0;F<nG;F++){
    int ub[5]={0};
    for(int h=0;h<nt;h++){
      u64 r0=H0[h]&~G0[F], r1=H1[h]&~G1[F];
      int rn=__builtin_popcountll(r0)+__builtin_popcountll(r1);
      if(rn>40) continue;
      int mn=99;
      for(int g=0;g<nG && mn>0;g++){ int c=__builtin_popcountll(r0&~G0[g])+__builtin_popcountll(r1&~G1[g]); if(c<mn) mn=c; }
      for(int k=mn;k<=4;k++) if(k>=0) ub[k]++;
    }
    for(int k=0;k<=4;k++){ hist[k][ub[k]]++; if(ub[k]>best[k]) best[k]=ub[k]; }
  }
  for(int k=0;k<=4;k++){ printf("k=%d max UB=%d  hist:",k,best[k]); for(int i=0;i<=best[k];i++) if(hist[k][i]) printf(" %d:%ld",i,hist[k][i]); printf("\n"); }
}
