
add_executable(foo_ex
	foo.cpp
)

target_compile_features(foo_ex INTERFACE cxx_std_20)
target_link_libraries(foo_ex PUBLIC async)

