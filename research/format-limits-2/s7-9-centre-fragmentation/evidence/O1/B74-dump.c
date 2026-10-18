#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// E8 as Construction A of extended Hamming [8,4]; 112 lines = 14 octads x 8 sign patterns mod +-
int oct[14],nl=0; int vec[112][8], blk[112]; int ip[112][112];
int main(){
  // generator of extended Hamming: weight-4 codewords
  int gen[4]={0xF0,0xCC,0xAA,0xFF}; int seen[256]={0}; int k=0;
  for(int m=0;m<16;m++){int w=0;for(int b=0;b<4;b++)if(m>>b&1)w^=gen[b]; if(__builtin_popcount(w)==4&&!seen[w]){seen[w]=1;oct[k++]=w;}}
  if(k!=14){printf("k=%d\n",k);return 1;}
  for(int c=0;c<14;c++){ int pos[4],q=0;for(int i=0;i<8;i++)if(oct[c]>>i&1)pos[q++]=i;
    for(int s=0;s<8;s++){ // fix sign of pos[0] = +, other 3 bits free
      memset(vec[nl],0,sizeof(vec[nl])); vec[nl][pos[0]]=1;
      for(int j=1;j<4;j++)vec[nl][pos[j]]=(s>>(j-1)&1)?-1:1; blk[nl]=c;nl++;}}
  for(int a=0;a<112;a++)for(int b=0;b<112;b++){int d=0;for(int i=0;i<8;i++)d+=vec[a][i]*vec[b][i];ip[a][b]=d;}
  // sanity
  int cnt0=0,cnt2=0,other=0;for(int b=1;b<112;b++){int d=ip[0][b];if(d==0)cnt0++;else if(abs(d)==2)cnt2++;else other++;}
  printf("line0: orth %d, |ip|=2 %d, other %d\n",cnt0,cnt2,other);
  long hist[16][5]; memset(hist,0,sizeof hist); // reach(eff) x nblocks
  long total=0;
  for(int a=0;a<112;a++)for(int b=a+1;b<112;b++)for(int c=b+1;c<112;c++)for(int d=c+1;d<112;d++){
    int S[4]={a,b,c,d}; int bm=0;for(int i=0;i<4;i++)bm|=1<<blk[S[i]]; int nb=__builtin_popcount(bm);
    int cls[8]={0};
    for(int t=0;t<112;t++){ if(bm>>blk[t]&1)continue; int ok=1,code=0;
      int s0=ip[t][a]; if(!s0)continue;
      for(int i=1;i<4;i++){int v=ip[t][S[i]]; if(!v){ok=0;break;} if((v>0)!=(s0>0))code|=1<<(i-1);}
      if(ok)cls[code]++; }
    int mx=0;for(int i=0;i<8;i++)if(cls[i]>mx)mx=cls[i];
    if(mx>15)mx=15; hist[mx][nb]++; total++; if(mx>=10&&nb==4){printf("F %d %d %d %d\n",a,b,c,d);}
  }
  for(int r=15;r>=7;r--){printf("eff reach %2d:",r);for(int n=1;n<=4;n++)printf(" nb%d=%ld",n,hist[r][n]);printf("\n");}
  return 0;}
