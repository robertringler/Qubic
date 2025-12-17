#!/usr/bin/env bash
# ==============================================================================
# QRATUM Debug Database Generator
# ==============================================================================
# Builds all C++ components with full DWARF debug symbols and generates
# separate .debug files for debugging without bloating release binaries.
#
# Platform: Linux (DWARF)
# Branch: main (stable baseline)
# Components: libquasim, QuASIM core
#
# Usage:
#   ./scripts/build_debug_database.sh [options]
#
# Options:
#   --clean       Clean build directory before building
#   --compress    Compress debug files with dwz
#   --gdb-index   Generate GDB index for faster symbol loading
#   --verbose     Enable verbose build output
#   --help        Show this help message
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build/debug-db"
DEBUG_OUTPUT_DIR="${BUILD_DIR}/debug"
LOG_FILE="${BUILD_DIR}/build.log"

# Default options
CLEAN_BUILD=false
COMPRESS_DEBUG=false
GDB_INDEX=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    head -30 "$0" | grep -E "^#" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

check_dependencies() {
    log_info "Checking build dependencies..."
    
    local missing=()
    
    for cmd in cmake g++ objcopy; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        log_error "Install with: sudo apt-get install build-essential cmake binutils"
        exit 1
    fi
    
    # Check GCC version for DWARF 4 support
    local gcc_version
    gcc_version=$(g++ -dumpversion | cut -d. -f1)
    if [[ "$gcc_version" -lt 7 ]]; then
        log_warn "GCC version $gcc_version detected. GCC 7+ recommended for full DWARF 4 support."
    fi
    
    log_success "All dependencies satisfied"
}

# ==============================================================================
# Parse Arguments
# ==============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --compress)
            COMPRESS_DEBUG=true
            shift
            ;;
        --gdb-index)
            GDB_INDEX=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# ==============================================================================
# Main Build Process
# ==============================================================================

main() {
    echo "============================================================"
    echo "  QRATUM Debug Database Generator"
    echo "  Platform: Linux (DWARF)"
    echo "  Branch: main (stable baseline)"
    echo "============================================================"
    echo ""
    
    check_dependencies
    
    # Clean if requested
    if [[ "$CLEAN_BUILD" == true ]]; then
        log_info "Cleaning build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    # Create directories
    mkdir -p "$BUILD_DIR"
    mkdir -p "$DEBUG_OUTPUT_DIR"
    
    # Start logging
    exec > >(tee -a "$LOG_FILE") 2>&1
    log_info "Build log: $LOG_FILE"
    log_info "Debug output: $DEBUG_OUTPUT_DIR"
    
    # Build libquasim
    build_libquasim
    
    # Build QuASIM core
    build_quasim_core
    
    # Generate manifest
    generate_manifest
    
    # Summary
    echo ""
    echo "============================================================"
    log_success "Debug database generation complete!"
    echo "============================================================"
    echo ""
    echo "Debug files location: $DEBUG_OUTPUT_DIR"
    echo ""
    ls -lah "$DEBUG_OUTPUT_DIR"/*.debug 2>/dev/null || log_warn "No .debug files found"
    echo ""
    echo "Usage with GDB:"
    echo "  gdb -ex 'set debug-file-directory $DEBUG_OUTPUT_DIR' ./your_binary"
    echo ""
}

build_libquasim() {
    local component="libquasim"
    local src_dir="${PROJECT_ROOT}/runtime/libquasim"
    local build_subdir="${BUILD_DIR}/${component}"
    
    if [[ ! -d "$src_dir" ]]; then
        log_warn "Source directory not found: $src_dir - skipping $component"
        return
    fi
    
    log_info "Building $component with debug symbols..."
    
    mkdir -p "$build_subdir"
    cd "$build_subdir"
    
    # CMake configure
    local cmake_args=(
        -DCMAKE_BUILD_TYPE=Debug
        -DCMAKE_C_FLAGS="-g3 -gdwarf-4 -fno-omit-frame-pointer"
        -DCMAKE_CXX_FLAGS="-g3 -gdwarf-4 -fno-omit-frame-pointer"
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    )
    
    if [[ "$VERBOSE" == true ]]; then
        cmake "${cmake_args[@]}" "$src_dir"
        cmake --build . --verbose
    else
        cmake "${cmake_args[@]}" "$src_dir" > /dev/null
        cmake --build . -- -j"$(nproc)"
    fi
    
    # Extract debug symbols
    extract_debug_symbols "$build_subdir" "$component"
    
    log_success "$component build complete"
}

build_quasim_core() {
    local component="QuASIM"
    local src_dir="${PROJECT_ROOT}/QuASIM"
    local build_subdir="${BUILD_DIR}/${component}"
    
    if [[ ! -d "$src_dir" ]]; then
        log_warn "Source directory not found: $src_dir - skipping $component"
        return
    fi
    
    log_info "Building $component with debug symbols..."
    
    mkdir -p "$build_subdir"
    cd "$build_subdir"
    
    # CMake configure
    local cmake_args=(
        -DCMAKE_BUILD_TYPE=Debug
        -DCMAKE_C_FLAGS="-g3 -gdwarf-4 -fno-omit-frame-pointer"
        -DCMAKE_CXX_FLAGS="-g3 -gdwarf-4 -fno-omit-frame-pointer"
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    )
    
    if [[ "$VERBOSE" == true ]]; then
        cmake "${cmake_args[@]}" "$src_dir"
        cmake --build . --verbose
    else
        cmake "${cmake_args[@]}" "$src_dir" > /dev/null
        cmake --build . -- -j"$(nproc)"
    fi
    
    # Extract debug symbols
    extract_debug_symbols "$build_subdir" "$component"
    
    log_success "$component build complete"
}

extract_debug_symbols() {
    local build_dir="$1"
    local component="$2"
    
    log_info "Extracting debug symbols for $component..."
    
    # Find all ELF binaries (libraries and executables)
    while IFS= read -r -d '' binary; do
        local basename
        basename=$(basename "$binary")
        local debug_file="${DEBUG_OUTPUT_DIR}/${basename}.debug"
        
        # Check if it's an ELF file
        if file "$binary" | grep -q "ELF"; then
            log_info "  Processing: $basename"
            
            # Extract debug symbols to separate file
            objcopy --only-keep-debug "$binary" "$debug_file"
            
            # Strip debug from original (optional - keep for dev)
            # objcopy --strip-debug "$binary"
            
            # Add debug link
            objcopy --add-gnu-debuglink="$debug_file" "$binary" 2>/dev/null || true
            
            # Generate GDB index if requested
            if [[ "$GDB_INDEX" == true ]] && command -v gdb &>/dev/null; then
                gdb --batch -ex "save gdb-index $DEBUG_OUTPUT_DIR" "$debug_file" 2>/dev/null || true
            fi
            
            # Compress if requested
            if [[ "$COMPRESS_DEBUG" == true ]] && command -v dwz &>/dev/null; then
                dwz "$debug_file" 2>/dev/null || true
            fi
        fi
    done < <(find "$build_dir" -type f \( -name "*.a" -o -name "*.so" -o -executable \) -print0 2>/dev/null)
}

generate_manifest() {
    local manifest_file="${DEBUG_OUTPUT_DIR}/debug_database_manifest.json"
    
    log_info "Generating debug database manifest..."
    
    cat > "$manifest_file" << EOF
{
    "version": "1.0.0",
    "generated": "$(date -Iseconds)",
    "platform": "linux",
    "debug_format": "DWARF-4",
    "branch": "main",
    "commit": "$(cd "$PROJECT_ROOT" && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "components": [
        {
            "name": "libquasim",
            "type": "static_library",
            "source": "runtime/libquasim/"
        },
        {
            "name": "QuASIM",
            "type": "library",
            "source": "QuASIM/"
        }
    ],
    "debug_files": [
$(find "$DEBUG_OUTPUT_DIR" -name "*.debug" -printf '        "%f",\n' 2>/dev/null | sed '$ s/,$//')
    ],
    "build_flags": {
        "CMAKE_BUILD_TYPE": "Debug",
        "debug_level": "-g3",
        "dwarf_version": "-gdwarf-4",
        "frame_pointer": "-fno-omit-frame-pointer"
    }
}
EOF
    
    log_success "Manifest generated: $manifest_file"
}

# Run main
main "$@"
