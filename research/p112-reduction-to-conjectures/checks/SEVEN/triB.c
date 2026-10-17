// impl B: distinct 7-flat masks (no maximality), sizes sA>=sB>=sC pruning, leftover test = #annihilating alpha>=3 (alpha in F2^9\0)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u;
int lab[120]; unsigned long long ann[120][8]; // bitset of alpha (0..511) with alpha.lab even
int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
u M[140000]; int nm=0; u X[140000];
int cmpu(const void*a,const void*b){u x=*(u*)a,y=*(u*)b; return x<y?-1:x>y;}
int cmps(const void*a,const void*b){return pc(*(u*)b)-pc(*(u*)a);}
int main(){FILE*f=fopen("triB.in","r"); for(int t=0;t<120;t++){fscanf(f,"%d",&lab[t]); memset(ann[t],0,64); for(int a=0;a<512;a++) if(!__builtin_parity(a&lab[t])) ann[t][a>>6]|=1ULL<<(a&63);}
 for(int a=1;a<512;a++) for(int b=a+1;b<512;b++){u m=0; for(int t=0;t<120;t++) if(((ann[t][a>>6]>>(a&63))&1)&&((ann[t][b>>6]>>(b&63))&1)) m|=((u)1)<<t; M[nm++]=m;}
 int k,sz; while(fscanf(f,"%d %d",&k,&sz)==2){u T=0; for(int i=0;i<sz;i++){int t;fscanf(f,"%d",&t);T|=((u)1)<<t;}
  int nx=0; for(int i=0;i<nm;i++) X[nx++]=M[i]&T; qsort(X,nx,sizeof(u),cmpu); int w=0; for(int i=0;i<nx;i++) if(!w||X[i]!=X[w-1]) X[w++]=X[i]; nx=w; qsort(X,nx,sizeof(u),cmps);
  long sol=0; long tested=0;
  for(int i=0;i<nx;i++){int sa=pc(X[i]); if(3*sa<sz)break;
   for(int j=i;j<nx;j++){int sb=pc(X[j]); if(sa+2*sb<sz)break; u Lf=T&~(X[i]|X[j]); if(pc(Lf)>sb) continue; tested++;
     unsigned long long A[8]; for(int q=0;q<8;q++)A[q]=~0ULL;
     for(int t=0;t<120;t++) if((Lf>>t)&1) for(int q=0;q<8;q++)A[q]&=ann[t][q];
     int c=0; for(int q=0;q<8;q++)c+=__builtin_popcountll(A[q]); // includes alpha=0
     if(c>=4) sol++; }}
  printf("B type %d |Off|=%d distinct masks %d tested %ld  covering (A,B) pairs: %ld\n",k,sz,nx,tested,sol); fflush(stdout);}
}
