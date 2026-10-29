// K579T impl A: A3 pair cover with an exempt set E of <= CAP lines (size-only relaxation; E = U = union of the 6 leftovers).
// usage: ./a3e a3.txt CAP [maxreps]   prints per-rep survivor counts; dumps survivors' U to surv_CAP.txt
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u;
static inline int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int NP,NM,NG; u off[6],*M; int perm[32][120],*par;
u rd(FILE*f){unsigned long long a,b;fscanf(f,"%llu %llu",&a,&b);return ((u)b<<64)|a;}
int fnd(int x){while(par[x]!=x)x=par[x]=par[par[x]];return x;}
int cmp(const void*a,const void*b){u x=*(u*)a,y=*(u*)b;return x<y?-1:x>y;}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");int CAP=atoi(argv[2]);int MAXR=1<<30,K=argc>3?atoi(argv[3]):0,ST=argc>4?atoi(argv[4]):1;
 fscanf(f,"%d %d %d",&NP,&NM,&NG);for(int i=0;i<6;i++)off[i]=rd(f);M=malloc(NM*sizeof(u));for(int i=0;i<NM;i++)M[i]=rd(f);
 for(int g=0;g<NG;g++)for(int t=0;t<120;t++)fscanf(f,"%d",&perm[g][t]);
 u*S=malloc(NM*sizeof(u));for(int i=0;i<NM;i++)S[i]=M[i];qsort(S,NM,sizeof(u),cmp);
 par=malloc(NM*sizeof(int));int*SI=malloc(NM*4);for(int i=0;i<NM;i++){u*q=bsearch(&M[i],S,NM,sizeof(u),cmp);SI[q-S]=i;}for(int i=0;i<NM;i++)par[i]=i;
 for(int i=0;i<NM;i++)for(int g=0;g<NG;g++){u y=0;for(int t=0;t<120;t++)if((M[i]>>t)&1)y|=(u)1<<perm[g][t];
   u*p=bsearch(&y,S,NM,sizeof(u),cmp);if(!p){printf("CLOSURE FAIL\n");return 1;}
   int j=SI[p-S];
   int a=fnd(i),b=fnd(j);if(a!=b)par[a]=b;}
 int nrep=0;for(int i=0;i<NM;i++)if(fnd(i)==i)nrep++;printf("orbits %d\n",nrep);fflush(stdout);
 char fn[64];sprintf(fn,"surv_%d_%d_%d.txt",CAP,K,ST);FILE*o=fopen(fn,"w");
 int*l1=malloc(NM*4),*l2=malloc(NM*4),*l3=malloc(NM*4);long long tot=0,t2=0;int done=0;
 int rk=-1;for(int r=0;r<NM&&done<MAXR;r++){if(fnd(r)!=r)continue;rk++;if(rk%ST!=K)continue;done++;int osz=0;for(int i=0;i<NM;i++)if(fnd(i)==r)osz++;
  u L0=M[r],A1=off[0]&~L0,A2=off[1]&~L0,A3=off[2]&~L0;int n1=0,n2=0,n3=0;
  for(int i=0;i<NM;i++){if(pc(A1&~M[i])<=CAP)l1[n1++]=i;if(pc(A2&~M[i])<=CAP)l2[n2++]=i;if(pc(A3&~M[i])<=CAP)l3[n3++]=i;}
  long long sv=0,s2=0;
  for(int a=0;a<n1;a++){u L1=M[l1[a]],U1=A1&~L1,B12=off[3]&~L1,B13=off[4]&~L1;
   for(int b=0;b<n2;b++){u L2=M[l2[b]];u U2=U1|((A2|B12)&~L2);if(pc(U2)>CAP)continue;s2++;u C23=off[5]&~L2,D=A3|B13|C23;
    for(int c=0;c<n3;c++){u U3=U2|(D&~M[l3[c]]);if(pc(U3)<=CAP){sv++;
      fprintf(o,"%d %d %d %d %d %llu %llu\n",r,l1[a],l2[b],l3[c],pc(U3),(unsigned long long)U3,(unsigned long long)(U3>>64));}}}}
  printf("rep %d orbit %d |L0| %d lists %d %d %d triples %lld quads %lld\n",r,osz,pc(L0),n1,n2,n3,s2,sv);fflush(stdout);tot+=sv*osz;t2+=s2;}
 printf("DONE CAP %d reps %d weighted_quads %lld triples %lld\n",CAP,done,tot,t2);fclose(o);}
