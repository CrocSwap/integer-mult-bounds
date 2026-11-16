// Independent check of SMALL2 Lemma N: for every 7-dim label subspace F and every L (|L|<=4),
// at most 2 directions h (|Off(h)|<=76) have Off(h)\F\L inside a 7-dim label subspace.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
static int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int lab[112]; u128 hm[512]; u128 G[50000]; int nG=0; u128 OFF[1300]; int nh;
int main(){
  FILE*f=fopen("ln_in.txt","r");
  for(int t=0;t<112;t++) fscanf(f,"%d",&lab[t]);
  fscanf(f,"%d",&nh);
  for(int k=0;k<nh;k++){int n;fscanf(f,"%d",&n);OFF[k]=0;for(int i=0;i<n;i++){int t;fscanf(f,"%d",&t);OFF[k]|=((u128)1)<<t;}}
  for(int z=1;z<512;z++){hm[z]=0;for(int t=0;t<112;t++) if(!(__builtin_popcount(z&lab[t])&1)) hm[z]|=((u128)1)<<t;}
  for(int a=1;a<512;a++)for(int b=a+1;b<512;b++){int c=a^b; if(c<b) continue; G[nG++]=hm[a]&hm[b];}
  fprintf(stderr,"7-flats %d dirs %d\n",nG,nh);
  // per F: for each h, list of minimal exceptional sets E (|E|<=4)
  static u128 Ex[1300][64]; static int nE[1300];
  long viol=0, pairs=0; int maxcnt=0;
  for(int fi=0;fi<nG;fi++){
    u128 F=G[fi]; int act[1300],na=0;
    for(int k=0;k<nh;k++){
      u128 R=OFF[k]&~F; if(pc(R)>40) continue;
      nE[k]=0;
      for(int g=0;g<nG;g++){
        u128 E=R&~G[g]; if(pc(E)>4) continue;
        // keep minimal, dedupe
        int skip=0;
        for(int j=0;j<nE[k];j++){ if((Ex[k][j]&~E)==0){skip=1;break;} }
        if(skip) continue;
        int m=0; for(int j=0;j<nE[k];j++) if((E&~Ex[k][j])!=0) Ex[k][m++]=Ex[k][j];
        nE[k]=m; if(m<64) Ex[k][nE[k]++]=E; else {fprintf(stderr,"overflow\n");exit(1);}
      }
      if(nE[k]) act[na++]=k;
    }
    pairs+=na; if(na>maxcnt) maxcnt=na;
    // triple check: 3 distinct active h with E1|E2|E3 of size <=4
    for(int x=0;x<na;x++)for(int y=x+1;y<na;y++){
      int a=act[x],b=act[y];
      for(int i=0;i<nE[a];i++)for(int j=0;j<nE[b];j++){
        u128 U=Ex[a][i]|Ex[b][j]; if(pc(U)>4) continue;
        for(int w=y+1;w<na;w++){int c=act[w];
          for(int l=0;l<nE[c];l++) if(pc(U|Ex[c][l])<=4){viol++; if(viol<5) fprintf(stderr,"VIOLATION F=%d h=%d,%d,%d |L|=%d\n",fi,a,b,c,pc(U|Ex[c][l]));}
        }
      }
    }
  }
  printf("F checked %d, total active (F,h) %ld, max active per F %d, violations %ld\n",nG,pairs,maxcnt,viol);
  return 0;
}
