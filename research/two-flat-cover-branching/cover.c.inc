// Branch on a label that neither current span covers. Every branch raises a rank.
// Any target cover extends at least one child; terminal pairs dominate all covers.
static int cover_dfs(const int *lab,int nl,const int*b3,int n3,const int*b4,int n4,
                     int c,int d,int stopfirst,int no){
  int x=0;
  for(int i=0;i<nl;i++) if(!inspan(b3,n3,lab[i])&&!inspan(b4,n4,lab[i])){x=lab[i];break;}
  if(!x){
    if(stopfirst) return 1;
    int rest[112],nr=0,rb[9];
    for(int i=0;i<nl;i++)if(!inspan(b4,n4,lab[i]))rest[nr++]=lab[i];
    if(rrefv(rest,nr,rb)!=n3)return no;
    nr=0;for(int i=0;i<nl;i++)if(!inspan(b3,n3,lab[i]))rest[nr++]=lab[i];
    if(rrefv(rest,nr,rb)!=n4)return no;
    if(no>=MAXFL){fprintf(stderr,"OPTION OVERFLOW\n");exit(2);}
    OPT*o=&OP[no++];o->k3=packkey((int*)b3,n3);o->k4=packkey((int*)b4,n4);
    o->n3=n3;o->n4=n4;memcpy(o->b3,b3,sizeof(int)*n3);memcpy(o->b4,b4,sizeof(int)*n4);
    return no;
  }
  int vs[9],nb[9];
  if(n3<c){memcpy(vs,b3,sizeof(int)*n3);vs[n3]=x;int n=rrefv(vs,n3+1,nb);
    no=cover_dfs(lab,nl,nb,n,b4,n4,c,d,stopfirst,no);if(stopfirst&&no)return 1;}
  if(n4<d){memcpy(vs,b4,sizeof(int)*n4);vs[n4]=x;int n=rrefv(vs,n4+1,nb);
    no=cover_dfs(lab,nl,b3,n3,nb,n,c,d,stopfirst,no);if(stopfirst&&no)return 1;}
  return no;
}
int opts4c(u128 D,int c,int d,int stopfirst,int no0){
  int lab[112],nl=0;
  for(int t=0;t<112;t++)if((D>>t)&1)lab[nl++]=LAB[t];
  int b[9];if(rrefv(lab,nl,b)>c+d)return no0;
  int empty[1]={0};return cover_dfs(lab,nl,empty,0,empty,0,c,d,stopfirst,no0);
}
