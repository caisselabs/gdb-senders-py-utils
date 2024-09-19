#pragma once

#include <async/start_detached.hpp>
#include <async/just.hpp>
#include <async/then.hpp>
#include <async/sequence.hpp>
#include <async/let.hpp>
#include <async/when_all.hpp>
#include <async/when_any.hpp>
#include <async/repeat.hpp>
#include <async/retry.hpp>

#include <boost/mp11/list.hpp>
#include <boost/mp11/map.hpp>
#include <type_traits>


namespace mp11 = boost::mp11;


namespace async_trace {

// tags for the different node types
struct start_detached_t;
struct just_t;
struct then_t;
struct sequence_t;
struct let_t;
struct when_all_t;
struct when_any_t;
struct repeat_t;
struct retry_t;
struct none_t;

template <typename Tag, stdx::ct_string Name, typename... Sndrs>
struct context {
  using tag_t = Tag;
  using sndrs_t = mp11::mp_list<Sndrs...>;
};



namespace detail {
// --------
// extract_name

template <typename T>
struct extract_name;

template <template <stdx::ct_string, class...> class T, stdx::ct_string Name, typename... Ts>
struct extract_name <T<Name, Ts...>> {
  static constexpr stdx::ct_string value = Name;
};

template <typename Tag, stdx::ct_string Name, typename... Ts>
struct extract_name <context<Tag, Name, Ts...>> {
  static constexpr stdx::ct_string value = Name;
};


template <typename T>
constexpr stdx::ct_string extract_name_v = extract_name<T>::value;
// --------



// --------
// lookup_tag

template <typename T>
struct lookup_tag;

template <typename Tag, stdx::ct_string N, typename... Ts>
struct lookup_tag<context<Tag, N, Ts...>>                  {  using type = Tag; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_just::sender<N, Ts...>>          { using type = just_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_let::sender<N, Ts...>>           { using type = let_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_repeat::sender<N, Ts...>>        { using type = repeat_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_retry::sender<N, Ts...>>         { using type = retry_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_sequence::sender<N, Ts...>>      { using type = sequence_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_when_all::sender<N, Ts...>>      { using type = when_all_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_when_any::sender<N, Ts...>>      { using type = when_any_t; };

template <stdx::ct_string N, typename... Ts>
struct lookup_tag<async::_then::sender<N, Ts...>>          { using type = then_t; };

template <typename... Ts>
struct lookup_tag<async::_start_detached::op_state<Ts...>> { using type = start_detached_t; };


template <typename T>
using lookup_tag_t = typename lookup_tag<T>::type;
}


// -------------------------------------------------------------------------
// Given an op_state, use the sender onion as the context
template <typename T>
struct extract_context {
  using type = context<detail::lookup_tag_t<T>, detail::extract_name_v<T>, T>;
};

template <typename stdx::ct_string Name, typename... Ts>
struct extract_context<async::_just::sender<Name, Ts...>> {
  using type = context<just_t, Name>;
};

template <typename stdx::ct_string Name, typename... Ts>
struct extract_context<async::_then::sender<Name, Ts...>> {
  using type = context<then_t, Name>;
};

template <typename stdx::ct_string Name, typename... Ts>
struct extract_context<async::_when_all::sender<Name, Ts...>> {
  using type = context<when_all_t, Name, Ts...>;
};

template <typename stdx::ct_string Name, typename... Ts>
struct extract_context<async::_just::op_state<Name, Ts...>> {
  using type = context<just_t, Name>;
};

template <typename stdx::ct_string Name, typename Sndr, typename... Ts>
struct extract_context<async::_let::op_state<Name, Sndr, Ts...>> {
  using type = context<let_t, Name, Sndr>;
};

template <typename stdx::ct_string Name, typename Sndr, typename... Ts>
struct extract_context<async::_repeat::op_state<Name, Sndr, Ts...>> {
  using type = context<repeat_t, Name, Sndr>;
};

template <typename stdx::ct_string Name, typename Sndr, typename... Ts>
struct extract_context<async::_retry::op_state<Name, Sndr, Ts...>> {
  using type = context<retry_t, Name, Sndr>;
};

template <typename stdx::ct_string Name, typename Sndr, typename... Ts>
struct extract_context<async::_sequence::op_state<Name, Sndr, Ts...>> {
  using type = context<sequence_t, Name, Sndr>;
};

template <typename U, typename Sndr, typename... Ts>
struct extract_context<async::_start_detached::op_state<U, Sndr, Ts...>> {
  using type = context<start_detached_t, "detatched", Sndr>;
};

template <typename stdx::ct_string Name, typename Rcvr, typename... Sndrs>
struct extract_context<async::_when_all::op_state<Name, Rcvr, Sndrs...>> {
  using type = context<when_all_t, Name, Sndrs...>;
};

template <typename stdx::ct_string Name, typename Rcvr, typename... Sndrs>
struct extract_context<async::_when_all::sync_op_state<Name, Rcvr, Sndrs...>> {
  using type = context<when_all_t, Name, Sndrs...>;
};

template <typename stdx::ct_string Name, typename StopPolicy, typename Rcvr, typename... Sndrs>
struct extract_context<async::_when_any::op_state<Name, StopPolicy, Rcvr, Sndrs...>> {
  using type = context<when_any_t, Name, Sndrs...>;
};

template <typename stdx::ct_string Name, typename... Ts>
struct extract_context<async::_then::receiver<Name, Ts...>> {
  using type = context<then_t, Name>;
};

template <typename T>
using extract_context_t = typename extract_context<T>::type;
// -------------------------------------------------------------------------
// -------------------------------------------------------------------------

// -------------------------------------------------------------------------
// given a sender type what are the senders that it links to
template <typename T>
struct sub_senders {
  using type = mp11::mp_list<>;
};

template <typename ...Ts>
struct sub_senders <mp11::mp_list<Ts...>> {
  using type = mp11::mp_list<Ts...>;
};

template <stdx::ct_string Name, typename Tag, typename Sndr, typename... Ts>
struct sub_senders <async::_then::sender<Name, Tag, Sndr, Ts...>> {
  using type = mp11::mp_list<Sndr>;
};

template <stdx::ct_string Name, typename Sndr, typename... Ts>
struct sub_senders <async::_let::sender<Name, Sndr, Ts...>> {
  using type = mp11::mp_list<Sndr>;
};

template <stdx::ct_string Name, typename Sndr, typename... Ts>
struct sub_senders <async::_repeat::sender<Name, Sndr, Ts...>> {
  using type = mp11::mp_list<Sndr>;
};

template <stdx::ct_string Name, typename Sndr, typename... Ts>
struct sub_senders <async::_retry::sender<Name, Sndr, Ts...>> {
  using type = mp11::mp_list<Sndr>;
};

template <stdx::ct_string Name, typename SndrA, typename SndrB>
struct sub_senders <async::_sequence::sender<Name,
					     SndrA,
					     async::_sequence::detail::wrapper<SndrB>>>{
  using type = mp11::mp_list<SndrA, SndrB>;
};

template <stdx::ct_string Name, typename... Sndrs, size_t ... N>
struct sub_senders <async::_when_all::sender<Name, async::_when_all::sub_sender<Sndrs, N>...>> {
  using type = mp11::mp_list<Sndrs...>;
};

template <typename Sndr, size_t N>
struct sub_senders <async::_when_all::sub_sender<Sndr, N>> {
  using type = mp11::mp_list<Sndr>;
};

template <stdx::ct_string Name, typename T, typename... Sndrs>
struct sub_senders <async::_when_any::sender<Name, T, Sndrs...>> {
  using type = mp11::mp_list<Sndrs...>;
};

template <typename ...T>
using sub_senders_t = mp11::mp_flatten<mp11::mp_list<typename sub_senders<T>::type...>>;
// -------------------------------------------------------------------------
// -------------------------------------------------------------------------


// -------------------------------------------------------------------------
// -------------------------------------------------------------------------
template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
bool handled{};
// -------------------------------------------------------------------------
// -------------------------------------------------------------------------


// -------------------------------------------------------------------------
// TODO: Rework to detect if the different signals exist before reseting them.
// -------------------------------------------------------------------------
namespace detail {
struct general_reset_t;
struct reset_with_error_t;
struct reset_with_eval_predicate_t;

template <typename T, stdx::ct_string C, stdx::ct_string L, typename Ctx>
auto reset_handled_impl = [] {
  handled<C, L, "start", Ctx> = false;
  handled<C, L, "set_value", Ctx> = false;
 };

template <stdx::ct_string C, stdx::ct_string L, typename Ctx>
auto reset_handled_impl<reset_with_error_t, C, L, Ctx> = [] {
  reset_handled_impl<general_reset_t, C, L, Ctx>();
  handled<C, L, "set_error", Ctx> = false;
  handled<C, L, "set_stopped", Ctx> = false;
 };

template <stdx::ct_string C, stdx::ct_string L, typename Ctx>
auto reset_handled_impl<reset_with_eval_predicate_t, C, L, Ctx> = [] {
  reset_handled_impl<reset_with_error_t, C, L, Ctx>();
  handled<C, L, "eval_predicate", Ctx> = false;
 }; 
}

using reset_map = mp11::mp_list<
  mp11::mp_list<just_t, detail::general_reset_t>,
  mp11::mp_list<then_t, detail::general_reset_t>,
  mp11::mp_list<sequence_t, detail::general_reset_t>,
  mp11::mp_list<let_t, detail::general_reset_t>,
  mp11::mp_list<when_all_t, detail::general_reset_t>,
  mp11::mp_list<when_any_t, detail::general_reset_t>,
  mp11::mp_list<repeat_t, detail::reset_with_eval_predicate_t>,
  mp11::mp_list<retry_t, detail::general_reset_t>
  >;

template <stdx::ct_string C, typename Ctx>
auto reset_handled = [] {
  using Tag = detail::lookup_tag_t<Ctx>;
  constexpr stdx::ct_string L = detail::extract_name_v<Ctx>;
  using reset_type_t = mp11::mp_second<mp11::mp_map_find<reset_map, Tag>>;

  //std::cout << "reset_handled " << C.value.data() << " " << L.value.data() << std::endl;
  detail::reset_handled_impl<reset_type_t, C, L, Ctx>();
 }; 
// -------------------------------------------------------------------------
// -------------------------------------------------------------------------


template <stdx::ct_string C, typename Ctx, typename Graph>
auto recursively_reset_handled = [](){

  reset_handled<C, Ctx>();

  using sub_nodes_t = sub_senders_t<Graph>;
  
  []<template <class...> class List, typename... Subs>(List<Subs...>){
    (..., recursively_reset_handled<C, extract_context_t<Subs>, Subs>());
  }(sub_nodes_t{});
 };


// -------------------------------------------------------------------------
// -------------------------------------------------------------------------
  

namespace detail {

template <typename C, typename T>
struct contains {
  static constexpr bool value = false;
};

template <template <class...> class C, typename... Ts, typename T>
struct contains <C<Ts...>, T> {
  static constexpr bool value = (false || ... || std::is_same_v<Ts, T>);
};
}

template <typename C, typename T>
constexpr bool contains_v = detail::contains<C, T>::value;

// list of tags to recursively reset when a start signal is received  
using reset_recursively_t = mp11::mp_list<repeat_t>;
  

struct debug_handler {

  template <stdx::ct_string C, stdx::ct_string L, stdx::ct_string S, typename Ctx>
  constexpr auto signal(auto ...) -> void {
    using context_t = extract_context_t<Ctx>;
    using tag_t = typename context_t::tag_t;
    using sndrs_t = typename context_t::sndrs_t;

    if constexpr (S == stdx::ct_string("start") && contains_v<reset_recursively_t, tag_t>) {
      recursively_reset_handled<C, context_t, sndrs_t>();
    }

    handled<C, L, S, context_t> = true;
  }
};
}
