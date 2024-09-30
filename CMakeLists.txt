cmake_minimum_required(VERSION 3.25)

project(
    gdb-senders-py-utils
    VERSION 0.1.0
    LANGUAGES CXX
    DESCRIPTION
        "gdb helpers to make sender debugging nicer."
)

include(cmake/get_cpm.cmake)
cpmaddpackage("gh:intel/cicd-repo-infrastructure#dev")

#add_versioned_package("gh:intel/cpp-baremetal-senders-and-receivers#4f98dcc")
add_versioned_package(NAME cpp-std-extensions
			   SOURCE_DIR /Users/mjcaisse/sandbox/cpp-std-extensions
			   GIT_TAG HEAD)

add_versioned_package(NAME cpp-baremetal-senders-and-receivers
			   SOURCE_DIR /Users/mjcaisse/sandbox/cpp-baremetal-senders-and-receivers
			   GIT_TAG HEAD)

add_subdirectory(example)

