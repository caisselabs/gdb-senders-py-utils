/**
 *  timeout_after version
 */
#include "debug_simple.hpp"
#include "std_hal.hpp"

#include <async/start_detached.hpp>
#include <async/just.hpp>
#include <async/then.hpp>
#include <async/when_all.hpp>
#include <async/when_any.hpp>
#include <async/connect.hpp>
#include <async/sequence.hpp>
#include <async/repeat.hpp>
#include <async/continue_on.hpp>
#include <async/start_on.hpp>
#include <async/timeout_after.hpp>
#include <async/schedulers/thread_scheduler.hpp>
#include <async/schedulers/trigger_manager.hpp>
#include <async/schedulers/trigger_scheduler.hpp>
#include <async/schedulers/time_scheduler.hpp>
#include <async/schedulers/timer_manager.hpp>

#include <iostream>
#include <chrono>

template <> inline auto async::injected_timer_manager<> = std_timer_manager_t{};
template <> inline auto async::injected_debug_handler<> = async_trace::debug_handler{};


using namespace std::chrono_literals;

namespace things {

  struct error { int value{}; };

  using trigger_happy = async::trigger_scheduler<"happy", int>;

  auto get_trigger =
      trigger_happy{}.schedule()
    | async::timeout_after(3s, error{66})
    ;
  
  auto s =
      async::start_on(async::thread_scheduler{}, async::just<"link-start">(42))
    | async::then<"before-wa-then">([](auto v){ return v+3; })
    | async::seq<"trigger-seq">(get_trigger)
    | async::then<"last-then">([](int v, auto ...){ std::cout << "got: " << v << "\n"; })
    | async::upon_error([](error v){ std::cout << "error{" << v.value << "}\n"; })
    | async::repeat()
    ;
}


int main() {
  auto d0 = async::start_detached_unstoppable<"my_chain">(things::s);

  while(true) {
    int input;
    std::cin >> input;
    async::run_triggers<"happy">(input);
  }
}
