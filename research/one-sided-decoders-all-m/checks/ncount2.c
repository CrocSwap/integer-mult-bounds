// mode 2: for every 7-dim label subspace F and every PAIR of lines {t0,t1}:
// N2 = #targets h with rank lab(Off(h) \ F \ {t0,t1}) <= 7. Report max and histogram.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int lab[112]; int nt=0; int tl[2000][120]; int tn[2000];
static int par(int x){return __builtin_popcount(x)&1;}
// rank of vectors v[0..n) skipping indices s0,s1
static int rk(const int*v,int n,int s0,int s1){int b[9]={0},r=0;for(int i=0;i<n;i++){if(i==s0||i==s1)continue;int x=v[i];for(int k=8;k>=0;k--){if(!(x>>k&1))continue;if(b[k])x^=b[k];else{b[k]=x;r++;break;}}}return r;}
int pid[112][112];
int main(){
  FILE*f=fopen("labs.txt","r"); for(int i=0;i<112;i++) fscanf(f,"%d",&lab[i]); fclose(f);
  f=fopen("targets.txt","r"); char line[4096];
  while(fgets(line,sizeof line,f)){ char*p=line; int n=0,x,c; while(sscanf(p,"%d%n",&x,&c)==1){tl[nt][n++]=x;p+=c;} if(n){tn[nt]=n;nt++;} } fclose(f);
  int np=0; for(int i=0;i<112;i++)for(int j=i+1;j<112;j++){pid[i][j]=pid[j][i]=np++;}
  static int cnt[6216]; long hist[4000]={0}; int best=0,bw1=0,bw2=0,bp=0; long passed=0;
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){
    int w3=w1^w2; int m1=w1<w2?w1:w2; m1=m1<w3?m1:w3; int M=w1>w2?w1:w2; M=M>w3?M:w3; int m2=w1+w2+w3-m1-M;
    if(!(m1==w1&&m2==w2)) continue;
    char inF[112]; for(int t=0;t<112;t++) inF[t]=!par(lab[t]&w1)&&!par(lab[t]&w2);
    memset(cnt,0,sizeof cnt); int all=0;
    for(int h=0;h<nt;h++){
      int R[120],rn=0,v[120]; for(int k=0;k<tn[h];k++){int t=tl[h][k]; if(!inF[t]){R[rn]=t; v[rn]=lab[t]; rn++;}}
      if(rn>38) continue; passed++;
      int r=rk(v,rn,-1,-1);
      if(r<=7){all++; continue;}
      // pairs inside R (and pairs with one element outside R if single removal suffices)
      char single[120]; for(int k=0;k<rn;k++) single[k]=(rk(v,rn,k,-1)<=7);
      for(int k=0;k<rn;k++){
        if(single[k]){ // any partner works
          for(int t=0;t<112;t++) if(t!=R[k]){ // avoid double count when partner also in R and single
            int kk=-1; for(int q=0;q<rn;q++) if(R[q]==t){kk=q;break;}
            if(kk>=0 && single[kk] && kk<k) continue;
            cnt[pid[R[k]][t]]++; }
        } else for(int q=k+1;q<rn;q++) if(!single[q] && rk(v,rn,k,q)<=7) cnt[pid[R[k]][R[q]]]++;
      }
    }
    for(int p=0;p<np;p++){int c=cnt[p]+all; hist[c]++; if(c>best){best=c;bw1=w1;bw2=w2;bp=p;}}
  }
  printf("passed (F,h) %ld; max N2 = %d at w1=%d w2=%d pair#%d\n",passed,best,bw1,bw2,bp);
  for(int i=0;i<=best;i++) if(hist[i]) printf("N2=%d : %ld\n",i,hist[i]);
}
