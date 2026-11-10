# Literal applied-source notes

The projection composed all54patches. These notes supply sourcefacts to Pro; they do not replace the complete effect-transfer proof. All line numbers below count raw LF bytes and retain formfeeds.

- bfd/opncls.c: New directory-test return precedes all fdclose/error branches in this function; no close(fd) occurs on that earlyreturn. This is a sourcepath fact, not actualleak observation; fixedregularinput mayexcludeit.

- bfd/opncls.c: _maybe_make_executable uses stat/umask/chmod on bfd_get_filename only for write_direction and EXEC_P|DYNAMIC; it is reached on close_all_done localret, before bfd_close combines thatresult with earlierwrite_contentsret. Therefore metadataeffect is not conditioned on overall bfd_close success.

- bfd/bfd.c + bfd/format.c + ld/ldmain.c: bfd_init sets default error_handler_fprintf; ldmain savesdefault theninstallsld_bfd_error_handler. Patched print_warnmsg calls_bfd_error_handler; format-check paths restore orig_error_handler before print_warnmsg. These are literalregistration/restorationedges, not arbitrarycallback purity proof.

- ld/ldmain.c: Mapfilefopen failure emits ordinaryeinfo (removed%F), thenfallsthrough has_map_file=true andlang_process. Exacterror/control equivalence with unpatched2.42 does not hold atthisbranch; role/effectpreservation must be distinct.

- ld/ldmisc.c: newfatal flushesstdout, calls vfinfo(stderr,fmt,arg,true), va_end, flushesstderr, thenxexit1. ldmain registeredld_cleanup viaxatexit at280.

- ld/ldlang.c: stat_alloc alreadyexisted inbase andcallsobstack_alloc(&stat_obstack,size). Newstat_memdup/stat_strdup addobstackalloc+memcpy+conditionalmemset/strlen; patch37moves callers toexisting statobstackallocation family. lang_init beginsstat_obstack; lang_finish hereonlyfreesoutputtable/remapinput. No false per-objectfree or release theorem.

- ld/plugin.c: plugin_opt_plugin actuallydlopen(plugin,RTLD_NOW) beforelinkingrecord, newfatalonloadfailure. Cleanupinvokes registeredcleanup_handler then dlclose. Registration/effectfrontierexplicit; no assumptionthat unknownpluginconstructors/finalizers arepure.

- ld/ldelf.c: ELF_PACKAGE_METADATA getenv branchcopiesenvironmentvaluewhennoexplicitmetadata. Itsabsence needsactualcontrolled-environmentcondition, not sourcepin alone.

- gas/output-file.c: Byteequalbase/applied outputlifecycle: createwithbfd_openw; closeclearsstdoutput beforeclose; choosesclose_all_done iferrors/noalwaysoutput elsebfd_close; mayunlink_if_ordinary if!keep_it; cleanupfunctionsrunthenas_fatal ifcloseresfalse.

Fullunits, exactfunctioncuts, hashes, before/after equality and licensepins are in CRITICAL-SOURCE-EXCERPTS-v1.json. No further decoding, builds, original execution or policy changes occurred during this readback.
