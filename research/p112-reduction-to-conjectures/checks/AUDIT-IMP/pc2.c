// AUDIT-IMP: independent pair-coverability check (kpr15 (C1) as used by WALL 8.2(a)).
// For every target T = Off(h) with |Off| <= 72 (112 roots R, 8 frame F, 128 norm-4 N70), decide whether T is covered by
// two label flats of dim <= 7: exists 7-dim F1 with rank(T \ F1) <= 7. For frame targets also test 6-dim F' (rank(T\F') >= 8 required).
// Labels are 9-bit ints; subspaces = common kernels of dot-functionals (basis independent). Build: cc -O2 pc2.c -o pc2
#include <stdio.h>
#include <string.h>
static int LAB[112];
static int par(int x){return __builtin_popcount(x)&1;}
static int rk(int*xs,int n){int b[9]={0},r=0;for(int i=0;i<n;i++){int x=xs[i];for(int k=8;k>=0;k--)if((x>>k)&1){if(b[k])x^=b[k];else{b[k]=x;r++;break;}}}return r;}
int main(){FILE*f=fopen("dirs.txt","r");for(int i=0;i<112;i++)fscanf(f,"%d",&LAB[i]);
 char kind[4];int n,T[112];int nd=0;int covR=0,covN=0,covF=0,badF=0,frameMin=99;
 while(fscanf(f,"%s %d",kind,&n)==2){for(int i=0;i<n;i++)fscanf(f,"%d",&T[i]);nd++;
  int ncov=0;int in[112],out[112];
  for(int a=1;a<512;a++)for(int b=a+1;b<512;b++){int c=a^b;if(c<b)continue; // 2-dim space {a,b,c}
    int ni=0,no=0;for(int i=0;i<n;i++){int u=LAB[T[i]];if(!par(u&a)&&!par(u&b))in[ni++]=u;else out[no++]=u;}
    int ro=rk(out,no);if(ro<=7){ncov++;int ri=rk(in,ni);int mn=ri<ro?ri:ro;if(mn<frameMin&&kind[0]=='F')frameMin=mn;}}
  if(ncov){if(kind[0]=='R')covR++;else if(kind[0]=='N')covN++;else covF++;}
  if(kind[0]=='F'){ // all 6-dim F' = kernels of 3-dim functional spaces {a,b,c} independent
    for(int a=1;a<512;a++)for(int b=a+1;b<512;b++)for(int c=b+1;c<512;c++){if(c==(a^b))continue;
      // canonical: a,b,c minimal reps? count each subspace possibly many times: harmless
      int no=0;for(int i=0;i<n;i++){int u=LAB[T[i]];if(par(u&a)||par(u&b)||par(u&c))out[no++]=u;}
      if(rk(out,no)<=7){badF++;}}
  }
 }
 printf("targets %d; pair-coverable: roots %d, N70 %d, frame %d; min part rank over frame 7+7 covers %d; frame covers with a <=6-dim part %d\n",nd,covR,covN,covF,frameMin,badF);
 return 0;}
