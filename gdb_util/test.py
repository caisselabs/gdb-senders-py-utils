import re

#async_trace::handled<
#    stdx::v1::ct_string<7ul>{std::__1::array<char, 7ul>{char [7]{(char)67, (char)104, (char)97, (char)105, (char)110, (char)65}}}, stdx::v1::ct_string<6ul>{std::__1::array<char, 6ul>{char [6]{(char)76, (char)105, (char)110, (char)107, (char)65}}}, stdx::v1::ct_string<7ul>{std::__1::array<char, 7ul>{char [7]{(char)115, (char)105, (char)103, (char)110, (char)97, (char)108}}}>

test_type = """async_trace::handled<"my_chain", "start_detached", "start", async::_start_detached::op_state<stdx::v1::cts_t<"my_chain">, async::_then::sender<"last-then", async::set_value_t, async::_sequence::sender<"seq", async::_then::sender<"before-wa-then", async::set_value_t, async::_just::sender<"link-start", async::set_value_t, int>, things::$_1>, async::_sequence::detail::wrapper<async::_when_all::sender<"when_all", async::_when_all::sub_sender<async::_just::sender<"just-a0", async::set_value_t, int>, 0ul>, async::_when_all::sub_sender<async::_just::sender<"just-a1", async::set_value_t, int>, 1ul>, async::_when_all::sub_sender<async::_then::sender<"then", async::set_value_t, async::_just::sender<"just-a2", async::set_value_t, int>, things::$_0>, 2ul>>>>, things::$_2>, async::stack_allocator, async::inplace_stop_source, async::env<async::prop<async::get_debug_interface_t, async::debug::named_interface<"my_chain">>, async::env<>>>>"""


ctstring_test = "stdx::v1::ct_string<7ul>{std::__1::array<char, 7ul>{char [7]{(char)67, (char)104, (char)97, (char)105, (char)110, (char)65}}}"


test_sym = """async_trace::handled<
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
"""


test_handled = """async_trace::handled<"my_chain", "start_detached", "start", async_trace::context<async_trace::start_detached_t, "detatched", async::_repeat::sender<"repeat", async::_then::sender<"last-then", async::set_value_t, async::_sequence::sender<"seq", async::_then::sender<"before-wa-then", async::set_value_t, async::_just::sender<"link-start", async::set_value_t, int>, things::$_1>, async::_sequence::detail::wrapper<async::_when_all::sender<"when_all", async::_when_all::sub_sender<async::_just::sender<"just-a0", async::set_value_t, int>, 0ul>, async::_when_all::sub_sender<async::_just::sender<"just-a1", async::set_value_t, int>, 1ul>, async::_when_all::sub_sender<async::_then::sender<"then", async::set_value_t, async::_just::sender<"just-a2", async::set_value_t, int>, things::$_0>, 2ul>>>>, things::$_2>, async::_repeat::$_3>>>"""


test_sched = """async_trace::handled<
  "my_chain", "start_detached", "start",
  async::_start_detached::op_state<
    stdx::v1::cts_t<"my_chain">,
    async::_repeat::sender<
      "repeat",
      async::_then::sender<
	"upon_error",
	async::set_error_t,
	async::_then::sender<
	  "last-then",
	  async::set_value_t,
	  async::_sequence::sender<
	    "seq",
	    async::_then::sender<
	      "before-wa-then",
	      async::set_value_t,
	      async::_sequence::sender<
		"seq",
		async::thread_scheduler<
		  "thread_scheduler">::sender,
		async::_sequence::detail::wrapper<
		  async::_just::sender<
		    "link-start",
		    async::set_value_t,
		    int>>>,
	      things::$_0>,
	    async::_sequence::detail::wrapper<
	      async::_when_any::sender<
		"stop_when",
		async::_when_any::first_complete,
		async::_when_any::sub_sender<
		  async::trigger_scheduler<
		    "happy", int>::sender,
		  0ul>,
		async::_when_any::sub_sender<
		  async::_sequence::sender<
		    "seq",
		    async::time_scheduler<
		      async::timer_mgr::default_domain,
		      "time_scheduler",
		      std::__1::chrono::duration<
			long long,
			std::__1::ratio<1l, 1l>>,
		      async::double_linked_task<
			async::detail::default_timer_task<
			  std::__1::chrono::time_point<
			    std::__1::chrono::steady_clock,
			    std::__1::chrono::duration<
			      long long,
			      std::__1::ratio<1l, 1000000000l>>>>>>::sender,
		    async::_sequence::detail::wrapper<
		      async::_just::sender<
			"timeout",
			async::set_error_t,
			things::error>>>,
		  1ul>>>>,
  things::$_1>,
  things::$_2>,
  async::_repeat::$_3>,
  async::static_allocator,
  async::never_stop_source,
  async::env<
    async::prop<
      async::get_debug_interface_t,
      async::debug::named_interface<"my_chain">>,
    async::env<>>>>
"""

def extract_ct_string(s):

    type_match = re.compile(r"stdx::v1::ct_string<(\d+)ul>{std::__1::array<char, (\d+)ul>{(.+)}}")
    str_element_match = re.compile(r"\(char\)(\d+)")
    
    tm = re.match(type_match, s)
    sm = re.findall(str_element_match, tm.group(3))

    return (tm, "".join(chr(int(m)) for m in sm))

