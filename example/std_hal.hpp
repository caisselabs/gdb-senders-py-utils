#pragma once

#include <async/schedulers/timer_manager.hpp>

#include <condition_variable>
#include <mutex>
#include <thread>
#include <atomic>
#include <chrono>

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


template <typename Rep, typename Period>
struct async::timer_mgr::time_point_for<std::chrono::duration<Rep, Period>> {
    using type = std::chrono::steady_clock::time_point;
};

