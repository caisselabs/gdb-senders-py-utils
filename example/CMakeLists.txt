
add_executable(demo1
	demo1.cpp
)
target_compile_features(demo1 INTERFACE cxx_std_20)
target_link_libraries(demo1 PUBLIC async)

add_executable(demo2
	demo2.cpp
)
target_compile_features(demo2 INTERFACE cxx_std_20)
target_link_libraries(demo2 PUBLIC async)

add_executable(demo3
	demo3.cpp
)
target_compile_features(demo3 INTERFACE cxx_std_20)
target_link_libraries(demo3 PUBLIC async)


add_executable(demo5
	demo5.cpp
)
target_compile_features(demo5 INTERFACE cxx_std_20)
target_link_libraries(demo5 PUBLIC async)

add_executable(demo6
	demo6.cpp
)
target_compile_features(demo6 INTERFACE cxx_std_20)
target_link_libraries(demo6 PUBLIC async)

