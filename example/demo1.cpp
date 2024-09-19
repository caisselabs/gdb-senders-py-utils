#include <async/debug.hpp>
#include <async/start_detached.hpp>
#include <async/just.hpp>
#include <async/then.hpp>
#include <async/when_all.hpp>
#include <async/connect.hpp>
#include <async/sequence.hpp>
#include <async/repeat.hpp>


namespace async_trace {

template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
bool handled{};

struct debug_handler {
  template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
  constexpr auto signal(auto ...) -> void {
    handled<C, L, S, Ctx> = true;
  }
};

}

template <>
inline auto async::injected_debug_handler<> = async_trace::debug_handler{};


namespace things {
  int av = 0;
  
  auto a0 = async::just<"just-a0">(0);
  auto a1 = async::just<"just-a1">(1);
  auto a2 = async::just<"just-a2">(2) | async::then([](auto v){ things::av = v; });
  auto w  = async::when_all(a0, a1, a2);

  int var = 0;
  auto s =
      async::just<"link-start">(42)
    | async::then<"before-wa-then">([](auto v){ things::var = v; })
    | async::seq(w)
    | async::then<"last-then">([](auto ...){ ++things::var; })
    | async::repeat();
}


int main() {
  auto d = async::start_detached<"my_chain">(things::s);

  while(true) {}
  return things::var;
}
