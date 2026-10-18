      if(getenv("EXPORT")) {
        char export_path[1024]; snprintf(export_path,sizeof(export_path),"%s-%d-%d.json",getenv("EXPORT"),ri,j); FILE *out=fopen(export_path,"w"); if(!out) return 3;
        fprintf(out,"{\"dims\":[%d,%d,%d,%d],\"target\":%d,\"rep\":%d,\"v2idx\":%d,\"x1\":\"%016llx%016llx\",\"x2\":\"%016llx%016llx\",\"directions\":[",adim,bdim,cdim,ddim,target,ri,j,(u64)(X1>>64),(u64)X1,(u64)(X2>>64),(u64)X2);
        for(int ci=0;ci<nc;ci++){
          int h=cand[ci]; if(ci) fprintf(out,",");
          fprintf(out,"{\"id\":%d,\"vectors\":[",h);
          for(int w=0;w<(htyp[h]==2?2:1);w++){if(w) fprintf(out,",");fprintf(out,"[");for(int k=0;k<8;k++){if(k)fprintf(out,",");fprintf(out,"%d",w?hv2[h][k]:hv[h][k]);}fprintf(out,"]");}
          fprintf(out,"],\"off\":\"%016llx%016llx\",\"options\":[",(u64)(OFF[h]>>64),(u64)OFF[h]);
          for(int e=Sstart[ci];e<Sstart[ci+1];e++){if(e>Sstart[ci])fprintf(out,",");fprintf(out,"[\"%llx\",\"%llx\"]",allS3[e],allS4[e]);}
          fprintf(out,"]}");
        }
        fprintf(out,"]}\n");fclose(out);fprintf(stderr,"EXPORTED rep %d pair %d nc %d options %d\n",ri,j,nc,tot); if(getenv("EXPORT_ONLY")) continue;
      }
