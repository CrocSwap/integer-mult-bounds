# External execution adapter for the pinned PR436 shell wrapper on paths with spaces.
# No source files or mathematical checks are changed. Trigger at execution time:
# bash has not installed the target script name while reading BASH_ENV on macOS.
imb_python() { command "$PYTHON" -I -B "$@"; }
imb_path_adapter() {
  case "${BASH_SOURCE[1]:-}" in
    */e8-r740-replica32/parent436/verify.sh)
      IFS=$'\n'
      PY=imb_python
      if [[ -n "${CK:-}" ]]; then
        INC="-I${HERE}/portable-include"$'\n'"-I${CK}"$'\n'"-I${BI}"
      fi
      ;;
  esac
}
trap imb_path_adapter DEBUG
