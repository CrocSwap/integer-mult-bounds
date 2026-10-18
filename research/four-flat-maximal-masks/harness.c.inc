/* Scalar interface for an independently generated exact set-family oracle. */
int main(void) {
  int count;
  while (scanf("%d",&count)==1) {
    if(count<0 || count>44000) return 2;
    u128 *input=malloc(sizeof(u128)*(size_t)(count+1));
    u128 *output=malloc(sizeof(u128)*(size_t)(count+1));
    if(!input || !output) return 2;
    for(int i=0;i<count;i++) {
      u64 hi,lo;
      if(scanf("%llx %llx",&hi,&lo)!=2) return 2;
      input[i]=((u128)hi<<64)|lo;
      if(i && input[i]<=input[i-1]) return 2;
    }
    int kept=SELECTED_MASKS(input,count,output);
    printf("%d",kept);
    for(int i=0;i<kept;i++) printf(" %016llx%016llx",(u64)(output[i]>>64),(u64)output[i]);
    printf("\n");free(input);free(output);
  }
  if(!feof(stdin)) return 2;
  return ferror(stdout)?2:0;
}
