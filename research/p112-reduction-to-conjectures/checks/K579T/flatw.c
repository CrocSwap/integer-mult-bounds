// max total weight of lines in a k-flat (labels in a k-dim F2 subspace), k=3,4; also max of union of three 4-flats + one 3-flat is bounded by sums.
#include <stdio.h>
int lab[120],c[120],wt[512],has[512];
int main(){for(int i=0;i<120;i++)scanf("%d",&lab[i]);for(int i=0;i<120;i++)scanf("%d",&c[i]);
 for(int i=0;i<120;i++){wt[lab[i]]=c[i];has[lab[i]]=1;}
 int best3=0,best4=0,mx4lines=0;
 for(int a=0;a<120;a++)for(int b=a+1;b<120;b++)for(int d=b+1;d<120;d++){
  int A=lab[a],B=lab[b],D=lab[d]; int s[8]={0,A,B,A^B,D,A^D,B^D,A^B^D};
  if(A==B||(A^B)==D) continue;
  int w=0;for(int k=1;k<8;k++)w+=wt[s[k]]; if(w>best3)best3=w;
  for(int e=d+1;e<120;e++){int E=lab[e];int in=0;for(int k=0;k<8;k++)if(s[k]==E)in=1; if(in)continue;
   int w4=w,n=0;for(int k=0;k<8;k++){w4+=wt[s[k]^E];} for(int k=1;k<8;k++)n+=has[s[k]];for(int k=0;k<8;k++)n+=has[s[k]^E];
   if(w4>best4)best4=w4; if(n>mx4lines)mx4lines=n;}}
 printf("max weight 3-flat %d, 4-flat %d, max lines in 4-flat %d -> W(E)<= %d\n",best3,best4,mx4lines,3*best4+best3);}
