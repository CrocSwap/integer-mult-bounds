// impl A (C): usage ./A K type(root|d7) ; leftovers of Off(h) by two 7-flats (F2^9 codim-2 flats), size<=K; prints unique minimal leftovers
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
int lab[120], co[120][8];
static int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static int cmp(const void*a,const void*b){u128 x=*(u128*)a,y=*(u128*)b;return x<y?-1:x>y;}
int main(int argc,char**argv){
  int K=atoi(argv[1]); int isd7=!strcmp(argv[2],"d7");
  FILE*f=fopen("lines.txt","r"); for(int t=0;t<120;t++){fscanf(f,"%d",&lab[t]);for(int k=0;k<8;k++)fscanf(f,"%d",&co[t][k]);}
  int h[8]; for(int k=0;k<8;k++)h[k]=co[0][k];
  int ri=0;
  if(isd7){ int s=-1; for(int t=1;t<120;t++){int d=0;for(int k=0;k<8;k++)d+=co[0][k]*co[t][k]; if(d==0){s=t;break;}} for(int k=0;k<8;k++)h[k]+=co[s][k]; ri=-1;}
  u128 T=0; int nz=0; for(int t=0;t<120;t++){int d=0;for(int k=0;k<8;k++)d+=h[k]*co[t][k]; if(d){T|=(u128)1<<t;nz++;}}
  fprintf(stderr,"|Off|=%d\n",nz);
  static u128 Z[512]; for(int a=1;a<512;a++){u128 m=0;for(int t=0;t<120;t++)if(!(__builtin_popcount(a&lab[t])&1))m|=(u128)1<<t;Z[a]=m&T;}
  u128*M=malloc(sizeof(u128)*131072*2);long nm=0;
  for(int a=1;a<512;a++)for(int b=a+1;b<512;b++){M[nm++]=Z[a]&Z[b];}
  qsort(M,nm,sizeof(u128),cmp); long k=0; for(long i=0;i<nm;i++) if(i==0||M[i]!=M[i-1]) M[k++]=M[i]; nm=k;
  // keep maximal
  u128*X=malloc(sizeof(u128)*nm);long nx=0;
  for(long i=0;i<nm;i++){int dom=0;for(long j=0;j<nm&&!dom;j++) if(j!=i&&(M[i]&M[j])==M[i]) dom=1; if(!dom)X[nx++]=M[i];}
  fprintf(stderr,"flat masks %ld maximal %ld\n",nm,nx);
  int need=nz-K; u128*L=malloc(sizeof(u128)*50000000);long nl=0;
  for(long i=0;i<nx;i++)for(long j=i;j<nx;j++){u128 u=X[i]|X[j]; if(pc(u)<need)continue; if(ri==0 && !((u)&1)) continue; // root: line0 covered
    if(nl<49999999) L[nl++]=T&~u; else {fprintf(stderr,"OVERFLOW\n");return 1;}}
  qsort(L,nl,sizeof(u128),cmp); k=0; for(long i=0;i<nl;i++) if(i==0||L[i]!=L[i-1]) L[k++]=L[i]; nl=k;
  fprintf(stderr,"unique leftovers %ld\n",nl);
  // sort by size then minimal filter
  for(int s=0;s<=K;s++)for(long i=0;i<nl;i++) if(pc(L[i])==s){int sub=0; for(long j=0;j<nl&&!sub;j++) if(j!=i&&pc(L[j])<s&&(L[j]&L[i])==L[j]) sub=1; if(!sub){printf("%d",s);for(int t=0;t<120;t++)if((L[i]>>t)&1)printf(" %d",t);printf("\n");}}
}
