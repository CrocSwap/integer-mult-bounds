// step B (impl A): two DISTINCT non-root pair directions at one seven a: h=h_ab, h'=h_ac (allowed types D7,A7,E6A1,D6,E6 by types.out).
// For each W-orbit rep L_a, min over (h,h',L_b,L_c) of |Off(h)\(La u Lb) u Off(h')\(La u Lc)|. Generic types (D6,E6): equal Off masks allowed (distinct points of one plane).
#include "e8.h"
#define CAP 28
typedef struct{u*l;int n,cap;}lst;
int main(int argc,char**argv){build();int cap=argc>1?atoi(argv[1]):CAP;
 int Ss[5]={0x01,0x02,0x40,0x81,0xc0},gen[5]={0,0,0,1,1};u*D=0;int nd=0,*dt=0;
 for(int k=0;k<5;k++){u*o;int n=orbit(offS(Ss[k]),&o);printf("type %02x orbit %d\n",Ss[k],n);D=realloc(D,(nd+n)*sizeof(u));dt=realloc(dt,(nd+n)*sizeof(int));
  for(int i=0;i<n;i++){D[nd+i]=o[i];dt[nd+i]=k;}nd+=n;free(o);}
 // orbit reps of maximal masks
 int*seen=calloc(NM,sizeof(int)),*q=malloc(NM*sizeof(int));int nrep=0,reps[64],osz[64];
 for(int s=0;s<NM;s++)if(!seen[s]){int n=1;q[0]=s;seen[s]=1;for(int i=0;i<n;i++)for(int r=0;r<8;r++){int j=mfind(act(r,M[q[i]]));if(j<0){printf("mask not closed\n");return 1;}if(!seen[j]){seen[j]=1;q[n++]=j;}}reps[nrep]=s;osz[nrep++]=n;}
 printf("mask orbits %d:",nrep);for(int i=0;i<nrep;i++)printf(" %d",osz[i]);printf("\n");fflush(stdout);
 long tot=0;
 for(int ri=0;ri<nrep;ri++){u La=M[reps[ri]];lst*L=calloc(nd,sizeof(lst));int nonempty=0;
  for(int h=0;h<nd;h++){u R=D[h]&~La;if(pc(R)>cap+40)continue;
   for(int b=0;b<NM;b++){u X=R&~M[b];if(pc(X)>cap)continue;int dom=0;
    for(int i=0;i<L[h].n;i++){if((L[h].l[i]&X)==L[h].l[i]){dom=1;break;}if((L[h].l[i]&X)==X){L[h].l[i]=L[h].l[--L[h].n];i--;}}
    if(dom)continue;if(L[h].n==L[h].cap){L[h].cap=L[h].cap?2*L[h].cap:8;L[h].l=realloc(L[h].l,L[h].cap*sizeof(u));}L[h].l[L[h].n++]=X;}
   if(L[h].n)nonempty++;}
  int best=999;long sol=0;int bt[2]={-1,-1};
  for(int h=0;h<nd;h++)if(L[h].n)for(int g=h;g<nd;g++)if(L[g].n){if(g==h&&!gen[dt[h]])continue;
   for(int i=0;i<L[h].n;i++)for(int j=0;j<L[g].n;j++){int k=pc(L[h].l[i]|L[g].l[j]);if(k<best){best=k;bt[0]=dt[h];bt[1]=dt[g];}if(k<=cap)sol++;}}
  printf("rep %d (orbit %d): dirs with leftover<=%d: %d ; min union %d (types %02x,%02x); pairs-with-union<=cap %ld\n",ri,osz[ri],cap,nonempty,best,bt[0]>=0?Ss[bt[0]]:0,bt[1]>=0?Ss[bt[1]]:0,sol);fflush(stdout);tot+=sol;
  for(int h=0;h<nd;h++)free(L[h].l);free(L);}
 printf("TOTAL pairs %ld\n",tot);}
