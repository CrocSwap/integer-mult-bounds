// KILL-A8 impl C: exhaustive (non-SAT) relaxed pair-cover for the A_{P-1} chain, P=3 (control) / 4.
// Want 7-flat masks L_0..L_{P-1} and a 6-dim label subspace X with Off(h_ab) \ X subset of L_a u L_b for all pairs.
// Equivalent: per pair the leftover Off(h_ab)\(L_a u L_b) and the union of all leftovers has label rank <= 6.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef unsigned __int128 u128;
int X1=0,P,NM,lab[120]; u128 off[6],M[50000]; int pa[6],pb[6],NP;
static int rk(u128 s){int b[9],n=0;for(int t=0;t<120;t++)if((s>>t)&1){int v=lab[t];for(int k=0;k<n;k++){int w=v^b[k];if(w<v)v=w;}if(v){b[n++]=v;if(n>6)return n;}}return n;}
static int pcnt(u128 x);
static int ok(u128 s){if(rk(s)<=6)return 1;if(!X1)return 0;for(int t=0;t<120;t++)if((s>>t)&1)if(rk(s&~((u128)1<<t))<=6)return 1;return 0;}
static int pcnt(u128 x){return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64));}
typedef struct{uint64_t key;u128 left;}E; E*H[6]; uint64_t HS[6]; int*lst[6]; long nl[6],cap[6];
static void put(int q,uint32_t i,uint32_t j,u128 lf){uint64_t k=((uint64_t)i<<20|j)+1,h=(k*0x9E3779B97F4A7C15ull)&(HS[q]-1);while(H[q][h].key){h=(h+1)&(HS[q]-1);}H[q][h].key=k;H[q][h].left=lf;}
static int get(int q,uint32_t i,uint32_t j,u128*lf){uint64_t k=((uint64_t)i<<20|j)+1,h=(k*0x9E3779B97F4A7C15ull)&(HS[q]-1);while(H[q][h].key){if(H[q][h].key==k){*lf=H[q][h].left;return 1;}h=(h+1)&(HS[q]-1);}return 0;}
int pid(int a,int b){for(int q=0;q<NP;q++)if(pa[q]==a&&pb[q]==b)return q;return -1;}
int main(int argc,char**argv){u128 FR=0;if(argc>4){unsigned long long lo,hi;FILE*g=fopen(argv[3],"r");int k=atoi(argv[4]);for(int i=0;i<=k;i++)fscanf(g,"%llu %llu %*d",&lo,&hi);FR=((u128)hi<<64)|lo;fclose(g);}FILE*f=fopen(argv[1],"r");if(argc>2)X1=atoi(argv[2]);fscanf(f,"%d %d",&P,&NM);for(int t=0;t<120;t++)fscanf(f,"%d",&lab[t]);
 NP=0;for(int a=0;a<P;a++)for(int b=a+1;b<P;b++){pa[NP]=a;pb[NP]=b;NP++;}
 for(int q=0;q<NP+NM;q++){unsigned long long lo,hi;fscanf(f,"%llu %llu",&lo,&hi);u128 v=((u128)hi<<64)|lo;if(q<NP)off[q]=v&~FR;else M[q-NP]=v;}
 int*c=malloc(NM*sizeof(int));
 for(int q=0;q<NP;q++){int no=pcnt(off[q]);for(int i=0;i<NM;i++)c[i]=pcnt(off[q]&M[i]);
  cap[q]=1<<20;lst[q]=malloc(cap[q]*2*sizeof(int));nl[q]=0;
  for(int i=0;i<NM;i++){if(c[i]+36<no-20-X1)continue;for(int j=0;j<NM;j++){if(c[i]+c[j]<no-20-X1)continue;u128 lf=off[q]&~M[i]&~M[j];if(pcnt(lf)>20+X1)continue;if(!ok(lf))continue;
   if(nl[q]==cap[q]){cap[q]*=2;lst[q]=realloc(lst[q],cap[q]*2*sizeof(int));}lst[q][2*nl[q]]=i;lst[q][2*nl[q]+1]=j;nl[q]++;}}
  HS[q]=1;while(HS[q]<4*(uint64_t)nl[q]+16)HS[q]<<=1;H[q]=calloc(HS[q],sizeof(E));
  for(long r=0;r<nl[q];r++){int i=lst[q][2*r],j=lst[q][2*r+1];put(q,i,j,off[q]&~M[i]&~M[j]);}
  fprintf(stderr,"pair %d (%d,%d): |Off|=%d allowed ordered (L_a,L_b) = %ld\n",q,pa[q],pb[q],no,nl[q]);}
 if(P==2){printf("frame=%s X1=%d P=2 allowed=%ld\n",argc>4?argv[4]:"none",X1,nl[0]);return 0;}
 // index lists of pairs (0,b) by first coordinate: lst sorted by i already (outer loop i)
 long*st[6];for(int b=1;b<P;b++){int q=pid(0,b);st[b]=calloc(NM+1,sizeof(long));for(long r=0;r<nl[q];r++)st[b][lst[q][2*r]+1]++;for(int i=0;i<NM;i++)st[b][i+1]+=st[b][i];}
 long sol=0,partial=0;int q01=pid(0,1),q02=pid(0,2),q12=pid(1,2);
 for(long r=0;r<nl[q01];r++){int i0=lst[q01][2*r],i1=lst[q01][2*r+1];u128 l01=off[q01]&~M[i0]&~M[i1];
  for(long s=st[2][i0];s<st[2][i0+1];s++){int i2=lst[q02][2*s+1];u128 l02=off[q02]&~M[i0]&~M[i2],l12;if(!get(q12,i1,i2,&l12))continue;u128 U=l01|l02|l12;if(!ok(U))continue;
   if(P==3){sol++;if(sol==1)fprintf(stderr,"control solution masks %d %d %d |U|=%d\n",i0,i1,i2,pcnt(U));continue;}
   partial++;int q03=pid(0,3),q13=pid(1,3),q23=pid(2,3);
   for(long w=st[3][i0];w<st[3][i0+1];w++){int i3=lst[q03][2*w+1];u128 l03=off[q03]&~M[i0]&~M[i3],l13,l23;if(!get(q13,i1,i3,&l13)||!get(q23,i2,i3,&l23))continue;
    u128 V=U|l03|l13|l23;if(!ok(V))continue;sol++;if(sol<=3)fprintf(stderr,"P4 solution %d %d %d %d\n",i0,i1,i2,i3);}}}
 printf("frame=%s X1=%d P=%d triangle(0,1,2)-consistent=%ld solutions=%ld\n",argc>4?argv[4]:"none",X1,P,partial,sol);return 0;}
