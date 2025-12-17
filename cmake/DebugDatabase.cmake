# DebugDatabase.cmake
# QRATUM Debug Database Generation Configuration
# Generates DWARF debug symbols for Linux debugging
#
# Usage: cmake -DCMAKE_BUILD_TYPE=Debug -DGENERATE_DEBUG_DB=ON ..

cmake_minimum_required(VERSION 3.20)

option(GENERATE_DEBUG_DB "Generate separate debug database files" ON)
option(DEBUG_DB_COMPRESS "Compress debug database files with dwz" OFF)

# Set debug flags for DWARF generation
set(QRATUM_DEBUG_FLAGS
    "-g3"                    # Maximum debug info (DWARF level 3)
    "-gdwarf-4"              # DWARF version 4 for broad compatibility
    "-fno-omit-frame-pointer" # Preserve frame pointers for stack traces
    "-fno-eliminate-unused-debug-types"  # Keep all type info
)

# Function to configure debug symbols for a target
function(qratum_enable_debug_symbols TARGET_NAME)
    if(NOT TARGET ${TARGET_NAME})
        message(WARNING "Target ${TARGET_NAME} does not exist, skipping debug configuration")
        return()
    endif()

    # Apply debug compile options
    target_compile_options(${TARGET_NAME} PRIVATE ${QRATUM_DEBUG_FLAGS})

    # Ensure no stripping occurs
    set_target_properties(${TARGET_NAME} PROPERTIES
        # Keep debug symbols in binary initially
        ENABLE_EXPORTS ON
    )

    if(GENERATE_DEBUG_DB)
        # Add post-build command to extract debug symbols
        add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
            COMMENT "Extracting debug symbols for ${TARGET_NAME}"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/debug"
            COMMAND ${CMAKE_OBJCOPY} --only-keep-debug
                "$<TARGET_FILE:${TARGET_NAME}>"
                "${CMAKE_BINARY_DIR}/debug/$<TARGET_FILE_NAME:${TARGET_NAME}>.debug"
            COMMAND ${CMAKE_OBJCOPY} --strip-debug "$<TARGET_FILE:${TARGET_NAME}>"
            COMMAND ${CMAKE_OBJCOPY} --add-gnu-debuglink="${CMAKE_BINARY_DIR}/debug/$<TARGET_FILE_NAME:${TARGET_NAME}>.debug"
                "$<TARGET_FILE:${TARGET_NAME}>"
            VERBATIM
        )

        # Optional compression
        if(DEBUG_DB_COMPRESS)
            add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                COMMENT "Compressing debug database for ${TARGET_NAME}"
                COMMAND dwz -m "${CMAKE_BINARY_DIR}/debug/$<TARGET_FILE_NAME:${TARGET_NAME}>.debug"
                    "${CMAKE_BINARY_DIR}/debug/$<TARGET_FILE_NAME:${TARGET_NAME}>.debug" || true
                VERBATIM
            )
        endif()
    endif()

    message(STATUS "Debug symbols enabled for target: ${TARGET_NAME}")
endfunction()

# Function to generate debug index (GDB index for faster loading)
function(qratum_generate_gdb_index TARGET_NAME)
    if(NOT TARGET ${TARGET_NAME})
        return()
    endif()

    if(GENERATE_DEBUG_DB)
        add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
            COMMENT "Generating GDB index for ${TARGET_NAME}"
            COMMAND gdb-add-index "${CMAKE_BINARY_DIR}/debug/$<TARGET_FILE_NAME:${TARGET_NAME}>.debug" 2>/dev/null || true
            VERBATIM
        )
    endif()
endfunction()

# Print configuration summary
message(STATUS "=== QRATUM Debug Database Configuration ===")
message(STATUS "  GENERATE_DEBUG_DB: ${GENERATE_DEBUG_DB}")
message(STATUS "  DEBUG_DB_COMPRESS: ${DEBUG_DB_COMPRESS}")
message(STATUS "  Debug flags: ${QRATUM_DEBUG_FLAGS}")
message(STATUS "  Output directory: \${CMAKE_BINARY_DIR}/debug/")
message(STATUS "============================================")
