// For every 7-dim label subspace F (annihilator of span{w1,w2}) and every line t0:
// N(F,t0) = #targets h with rank lab(Off(h) \ F \ {t0}) <= 7.  Report max N, and histogram.
// Also mode 2: two removed lines (L_o = {t0,t1}): N2(F,{t0,t1}).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int lab[112]; int nt=0; int tl[2000][120]; int tn[2000];
static int rank_of(int *v,int n){ int b[9]={0}; int r=0; for(int i=0;i<n;i++){int x=v[i]; for(int k=8;k>=0;k--){ if(!(x>>k&1)) continue; if(b[k]) x^=b[k]; else {b[k]=x; r++; break;} } } return r; }
static int par(int x){return __builtin_popcount(x)&1;}
int main(int argc,char**argv){
  int mode=argc>1?atoi(argv[1]):1;
  FILE*f=fopen("labs.txt","r"); for(int i=0;i<112;i++) fscanf(f,"%d",&lab[i]); fclose(f);
  f=fopen("targets.txt","r"); char line[4096];
  while(fgets(line,sizeof line,f)){ char*p=line; int n=0,x,c; while(sscanf(p,"%d%n",&x,&c)==1){tl[nt][n++]=x;p+=c;} if(n){tn[nt]=n;nt++;} } fclose(f);
  fprintf(stderr,"targets %d\n",nt);
  long hist[2000]={0}; int best=0; int bw1=0,bw2=0,bt=0;
  int seen[512][512]; memset(seen,0,sizeof seen);
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){
    int w3=w1^w2; int a=w1,b=w2,c=w3; // canonical: smallest two of {w1,w2,w3}
    int m1=a<b?a:b; m1=m1<c?m1:c; int M=a>b?a:b; M=M>c?M:c; int m2=a+b+c-m1-M;
    if(!(m1==w1&&m2==w2)) continue;
    int inF[112]; for(int t=0;t<112;t++) inF[t]=!par(lab[t]&w1)&&!par(lab[t]&w2);
    if(mode==1){
      int cnt[112]; memset(cnt,0,sizeof cnt);
      for(int h=0;h<nt;h++){
        int R[120],rn=0; for(int k=0;k<tn[h];k++){int t=tl[h][k]; if(!inF[t]) R[rn++]=t;}
        int v[120]; for(int k=0;k<rn;k++) v[k]=lab[R[k]];
        int r=rank_of(v,rn);
        if(r<=7){ for(int t=0;t<112;t++) cnt[t]++; }
        else if(r==8){ for(int k=0;k<rn;k++){ int u[120],un=0; for(int j=0;j<rn;j++) if(j!=k) u[un++]=v[j]; if(rank_of(u,un)<=7) cnt[R[k]]++; } }
      }
      for(int t=0;t<112;t++){ hist[cnt[t]]++; if(cnt[t]>best){best=cnt[t];bw1=w1;bw2=w2;bt=t;} }
    }
  }
  printf("max N = %d at w1=%d w2=%d t0=%d\n",best,bw1,bw2,bt);
  for(int i=0;i<=best;i++) if(hist[i]) printf("N=%d : %ld (F,t0) pairs\n",i,hist[i]);
}
