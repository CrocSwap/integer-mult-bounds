int main(void){
 int nl;if(scanf("%d",&nl)!=1||nl<0||nl>112)return 2;
 for(int i=0;i<nl;i++)if(scanf("%d",&LAB[i])!=1)return 2;
 unsigned long long hi,lo;int c,d;
 while(scanf("%llx %llx %d %d",&hi,&lo,&c,&d)==4){
   if(c<0||c>6||d<0||d>6)return 2;
   u128 mask=((u128)hi<<64)|lo;int n=opts4(mask,c,d,0);
   u128 *keys=malloc(sizeof(u128)*(n+1));for(int i=0;i<n;i++)keys[i]=((u128)OP[i].k3<<64)|OP[i].k4;
   qsort(keys,n,sizeof(u128),cmp128);int count=0;for(int i=0;i<n;i++)if(i==0||keys[i]!=keys[i-1])count++;
   printf("%d",count);for(int i=0;i<n;i++)if(i==0||keys[i]!=keys[i-1])printf(" %llx:%llx",(u64)(keys[i]>>64),(u64)keys[i]);printf("\n");free(keys);
 }
 return 0;
}
