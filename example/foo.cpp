#include <async/debug.hpp>
#include <async/start_detached.hpp>
#include <async/just.hpp>
#include <async/then.hpp>
#include <async/when_all.hpp>
#include <async/connect.hpp>
#include <async/sequence.hpp>
#include <async/repeat.hpp>

#include "debug.hpp"
//#include <iostream>


struct debug_context;

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

/**
async_trace::handled<
  "my_chain",
  "start_detached",
  "start",
  async::_start_detached::op_state<
    stdx::v1::cts_t<"my_chain">,
    async::_repeat::sender<
      "repeat",
      async::_then::sender<
	"last-then",
	async::set_value_t,
	async::_sequence::sender<
	  "seq",
	  async::_then::sender<
	    "before-wa-then",
	    async::set_value_t,
	    async::_just::sender<
	      "link-start",
	      async::set_value_t,
	      int>,
	    things::$_1>,
	  async::_sequence::detail::wrapper<
	    async::_when_all::sender<
	      "when_all",
	      async::_when_all::sub_sender<
		async::_just::sender<
		  "just-a0",
		  async::set_value_t,
		  int>,
		0ul>,
	      async::_when_all::sub_sender<
		async::_just::sender<
		  "just-a1",
		  async::set_value_t,
		  int>,
		1ul>,
	      async::_when_all::sub_sender<
		async::_then::sender<
		  "then",
		  async::set_value_t,
		  async::_just::sender<
		    "just-a2",
		    async::set_value_t,
		    int>,
		  things::$_0>,
		2ul>
	      >
	    >
	  >,
	things::$_2>,
      async::_repeat::$_3>,
    async::stack_allocator, async::inplace_stop_source, async::env<async::prop<async::get_debug_interface_t, async::debug::named_interface<"my_chain">>, async::env<>>>>
*/
