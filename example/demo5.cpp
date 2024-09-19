#include <async/start_detached.hpp>
#include <async/just.hpp>
#include <async/then.hpp>
#include <async/when_all.hpp>
#include <async/connect.hpp>
#include <async/sequence.hpp>
#include <async/repeat.hpp>
#include <async/continue_on.hpp>
#include <async/start_on.hpp>
#include <async/schedulers/thread_scheduler.hpp>
#include <async/schedulers/trigger_manager.hpp>
#include <async/schedulers/trigger_scheduler.hpp>

#include <iostream>


namespace things {
  int av = 0;
  
  auto a0 = async::just<"just-a0">(1);
  auto a1 = async::just<"just-a1">(2);
  auto a2 = async::just<"just-a2">(3) | async::then([](auto v){ things::av = v; });
  auto w  = async::when_all(a0, a1, a2);

  using trigger_happy = async::trigger_scheduler<"happy", int>;
  
  int var = 0;
  auto s =
      async::start_on(async::thread_scheduler{}, async::just<"link-start">(42))
    | async::then<"before-wa-then">([](auto v){ things::var = v; })
    | async::seq(w)
    | async::seq(trigger_happy{}.schedule())
    | async::then<"last-then">([](int v, auto ...){ std::cout << "got: " << v << "\n"; })
    | async::repeat();
}


int main() {
  auto d0 = async::start_detached<"my_chain">(things::s);

  while(true) {
    if (std::cin.get() == '\n') {
      async::run_triggers<"happy">(12);
    }
  }
}
