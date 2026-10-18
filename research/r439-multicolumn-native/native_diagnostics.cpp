// Expose an uncaught native checker exception consistently across C++ runtimes.
// No checker predicate, return path on success, or input is changed.
// ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
#include <cstdio>
#include <cstdlib>
#include <exception>

namespace {
struct InstallDiagnostics {
  InstallDiagnostics() {
    std::set_terminate([] {
      try {
        if (auto error = std::current_exception()) std::rethrow_exception(error);
      } catch (const std::exception &error) {
        std::fprintf(stderr, "native checker exception: %s\n", error.what());
        std::fflush(stderr);
      } catch (...) {}
      std::abort();
    });
  }
} install;
}
