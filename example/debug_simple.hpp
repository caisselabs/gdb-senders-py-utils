#pragma once

#include <async/debug.hpp>

namespace async_trace {
template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
bool handled{};

struct debug_handler {
  template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
  constexpr auto signal(auto ...) -> void {
    // std::cout << "signal<" << C.value.data() << ", " << L.value.data() << ", " << S.value.data() << ">\n";
    handled<C, L, S, Ctx> = true;
  }
};
}
