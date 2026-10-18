/* Complete portable setup-state serialization; used identically by both builds. */
static void put128(FILE *f, u128 v) {
  unsigned char bytes[16];
  for (int i=0;i<16;i++) bytes[i]=(unsigned char)(v>>(8*i));
  if (fwrite(bytes,1,16,f)!=16) { perror("setup write"); exit(2); }
}
static void export_setup(int ri,int na,int *act,u128 *R1,int *capr,u128 **LG,int *LGn) {
  const char *base=getenv("MASK_SETUP");
  if (!base) return;
  char path[4096];
  int size=snprintf(path,sizeof(path),"%s-%d.bin",base,ri);
  if (size<0 || size>=(int)sizeof(path)) { fprintf(stderr,"setup path too long\n");exit(2); }
  FILE *f=fopen(path,"wb");
  if (!f) { perror("setup open"); exit(2); }
  put128(f,(u128)ri);put128(f,(u128)na);
  for (int i=0;i<na;i++) {
    put128(f,(u128)act[i]);put128(f,R1[i]);put128(f,(u128)capr[i]);put128(f,(u128)LGn[i]);
    for (int j=0;j<LGn[i];j++) put128(f,LG[i][j]);
  }
  if (fclose(f)) { perror("setup close"); exit(2); }
}
