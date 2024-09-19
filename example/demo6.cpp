/**
 *  timeout_after version
 */

#include <async/debug.hpp>
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

#include <condition_variable>
#include <mutex>
#include <thread>
#include <atomic>

using namespace std::chrono_literals;


namespace {
struct std_hal {
    using time_point_t = std::chrono::steady_clock::time_point;
    using task_t = async::timer_task<time_point_t>;

    static inline std::mutex m{};
    static inline std::condition_variable cv{};
    static inline std::thread t{};
    static inline time_point_t next_wakeup{};
    static inline bool running{};
    static inline std::atomic_bool stop_src{};

    static auto enable() -> void {
        std::lock_guard lock{m};
        if (not running) {
            running = true;
            t = std::thread{
                [&]() {
                    while (not stop_src) {
                        {
                            std::unique_lock lock{m};
                            cv.wait_until(lock, next_wakeup, [&] {
                                return stop_src or next_wakeup <= now();
                            });
                        }
                        if (not stop_src) {
                            async::timer_mgr::service_task();
                        }
                    }
                }};

        }
    }
    static auto disable() -> void { set_event_time(time_point_t::max()); }
    static auto set_event_time(time_point_t tp) -> void {
        {
            std::lock_guard lock{m};
            next_wakeup = tp;
        }
        cv.notify_one();
    }
    static auto now() -> time_point_t {
        return std::chrono::steady_clock::now();
    }

    static auto stop() {
        stop_src = true;
        cv.notify_one();
        t.join();
    }
};

using std_timer_manager_t = async::generic_timer_manager<std_hal>;
} // namespace
template <>
[[maybe_unused]] inline auto async::injected_timer_manager<> = std_timer_manager_t{};

template <typename Rep, typename Period>
struct async::timer_mgr::time_point_for<std::chrono::duration<Rep, Period>> {
    using type = std::chrono::steady_clock::time_point;
};



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

  struct error { int value{}; };

  using trigger_happy = async::trigger_scheduler<"happy", int>;

  auto get_trigger =
      trigger_happy{}.schedule()
    | async::timeout_after(5s, error{66})
    ;
  
  auto s =
      async::start_on(async::thread_scheduler{}, async::just<"link-start">(42))
    | async::then<"before-wa-then">([](auto v){ return v+3; })
    | async::seq(get_trigger)
    | async::then<"last-then">([](int v, auto ...){ std::cout << "got: " << v << "\n"; })
    | async::upon_error([](error v){ std::cout << "error{" << v.value << "}\n"; })
    | async::repeat();
}


int main() {
  auto d0 = async::start_detached_unstoppable<"my_chain">(things::s);

  while(true) {
    if (std::cin.get() == '\n') {
      async::run_triggers<"happy">(12);
    }
  }
}
