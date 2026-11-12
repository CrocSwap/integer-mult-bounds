#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
typedef unsigned __int128 u;
static int pc(u a){return __builtin_popcountll((uint64_t)a)+__builtin_popcountll((uint64_t)(a>>64));}
static int lo(u a){uint64_t l=(uint64_t)a;return l?__builtin_ctzll(l):64+__builtin_ctzll((uint64_t)(a>>64));}
#define B(x) (((u)1)<<(x))
static u *img;int NI;long long nodes=0;int JOBS=1,JOB=0;long long cnt2=0;
static u Dfound;int found=0;
static u orbm[8];int NO=0;
/* HIT */
static void hit(int*lst,int n,u D,int r,u F,int depth){
  nodes++;
  if(n==0){found=1;Dfound=D;return;}
  if(r==0)return;
  int best=-1,bp=999;
  for(int i=0;i<n;i++){int p=pc(img[lst[i]]&~F);if(p<bp){bp=p;best=lst[i];if(p<=1)break;}}
  if(bp==0)return;
  if(r<n){ /* greedy disjoint packing bound */
    u used=0;int c=0;
    for(int i=0;i<n;i++){u e=img[lst[i]]&~F; if(!(e&used)){used|=e;c++;if(c>r)return;}}
  }
  u e=img[best]&~F; int*nl=malloc(sizeof(int)*n);
  u F2=F;
  while(e){int x=lo(e);e&=e-1;
    if(depth==1){ if((cnt2++)%JOBS!=JOB){F2|=B(x);continue;} }
    int m=0;for(int i=0;i<n;i++)if(!(img[lst[i]]&B(x)))nl[m++]=lst[i];
    hit(nl,m,D|B(x),r-1,F2,depth+1); if(found){free(nl);return;}
    F2|=B(x);
  }
  free(nl);
}
/* FRAMES */
static u *tet;static u Fm=0,ORT[120];static int CASEC=0;
static int okA(u A,u D2){if(A&Fm)return 0;if(CASEC){u a=A;while(a){int x=lo(a);a&=a-1;if((D2&~B(x))&~ORT[x])return 0;}}return 1;}int NF;
static u fb[16384];int nfb=0;
static int killed(int f,u D){for(int t=0;t<14;t++)if(pc(tet[f*14+t]&D)>=2)return 1;return 0;}
static void fr(int*lst,int n,u D,int r,int depth){
  nodes++;
  if(n==0){found=1;Dfound=D;return;}
  if(r==0)return;
  int best=-1,bo=1<<30;
  for(int i=0;i<n;i++){int f=lst[i],o=0;
    for(int t=0;t<14;t++){int c=pc(tet[f*14+t]&D);o+= c==1?7:(r>=2?28:0);}
    if(o<bo){bo=o;best=f;if(o==0)break;}}
  if(bo==0)return;
  int sv=nfb;int*nl=malloc(sizeof(int)*n);
  for(int t=0;t<14&&!found;t++){u T=tet[best*14+t];int c=pc(T&D);
    u av=T&~D;
    if(c==1){u a=av;while(a&&!found){int x=lo(a);a&=a-1;u A=B(x);u D2=D|A;int ok=okA(A,D2);for(int k=0;k<nfb&&ok;k++)if((fb[k]&D2)==fb[k]){ok=0;break;}
        if(depth==0&&(cnt2++)%JOBS!=JOB)ok=0;
        if(ok){int m=0;for(int i=0;i<n;i++)if(!killed(lst[i],D2))nl[m++]=lst[i];
          /* nl is reused by deeper levels only via own malloc */
          fr(nl,m,D2,r-1,depth+1);}
        fb[nfb++]=A;}}
    else if(c==0&&r>=2){u a=av;while(a&&!found){int x=lo(a);a&=a-1;u b=a;while(b&&!found){int y=lo(b);b&=b-1;u A=B(x)|B(y);u D2=D|A;int ok=okA(A,D2);for(int k=0;k<nfb&&ok;k++)if((fb[k]&D2)==fb[k]){ok=0;break;}
        if(depth==0&&(cnt2++)%JOBS!=JOB)ok=0;
        if(ok){int m=0;for(int i=0;i<n;i++)if(!killed(lst[i],D2))nl[m++]=lst[i];
          fr(nl,m,D2,r-1-1,depth+1);}
        fb[nfb++]=A;}}}
  }
  nfb=sv;free(nl);
}
int main(int argc,char**argv){
  /* usage: hit K JOBS JOB orbit | fr K NFR JOBS JOB */
  FILE*f;
  if(!strcmp(argv[1],"hit")){
    int K=atoi(argv[2]);JOBS=atoi(argv[3]);JOB=atoi(argv[4]);int o=atoi(argv[5]);
    f=fopen("imgs.bin","rb");img=malloc(16*393120);NI=0;uint64_t ab[2];
    while(fread(ab,8,2,f)==2)img[NI++]=((u)ab[1]<<64)|ab[0];
    /* orbits from orbs.txt: lines each: bitmask lo hi */
    f=fopen("orbm.txt","r");unsigned long long a,b;while(fscanf(f,"%llu %llu",&a,&b)==2)orbm[NO++]=((u)b<<64)|a;
    u F=0;for(int i=0;i<o;i++)F|=orbm[i];
    int x=lo(orbm[o]);
    int*l=malloc(4*NI);int m=0;for(int i=0;i<NI;i++)if(!(img[i]&B(x)))l[m++]=i;
    hit(l,m,B(x),K-1,F,1);
  } else {
    int K=atoi(argv[2]),NFR=atoi(argv[3]);JOBS=atoi(argv[4]);JOB=atoi(argv[5]);
    int mode=argc>6?atoi(argv[6]):0; /* 0 plain, 1 case C (pairwise orth), 2 case N: D contains 0,2 + orbit rep */
    int oo=argc>7?atoi(argv[7]):0;
    {FILE*g=fopen("orth.txt","r");unsigned long long a,b;int i=0;while(fscanf(g,"%llu %llu",&a,&b)==2)ORT[i++]=((u)b<<64)|a;
     g=fopen("orbm.txt","r");while(fscanf(g,"%llu %llu",&a,&b)==2)orbm[NO++]=((u)b<<64)|a;}
    f=fopen("frames.bin","rb");tet=malloc(16*14*2025);int k=0;uint64_t ab[2];
    while(fread(ab,8,2,f)==2)tet[k++]=((u)ab[1]<<64)|ab[0];
    NF=k/14;if(NFR&&NFR<NF)NF=NFR;
    u D=B(0);int r=K-1;
    if(mode==1)CASEC=1;
    if(mode==2){D=B(0)|B(2);int x=lo(orbm[oo]);for(int i=0;i<oo;i++)Fm|=orbm[i];D|=B(x);r=K-3;}
    int*l=malloc(4*NF);int m=0;for(int i=0;i<NF;i++)if(!killed(i,D))l[m++]=i;
    fr(l,m,D,r,0);
  }
  printf("found=%d nodes=%lld",found,nodes);
  if(found){printf(" D=");for(int i=0;i<120;i++)if(Dfound&B(i))printf("%d ",i);}
  printf("\n");return 0;
}
