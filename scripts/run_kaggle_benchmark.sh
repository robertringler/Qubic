#!/bin/bash
# QRATUM Chess - Kaggle Leaderboard Benchmark Wrapper
# 
# This script downloads Kaggle chess leaderboard data and runs QRATUM engine benchmarks.
# Optionally submits results back to Kaggle leaderboard.
#
# Usage:
#   ./scripts/run_kaggle_benchmark.sh                    # Run benchmark only
#   ./scripts/run_kaggle_benchmark.sh --submit           # Run and submit to leaderboard
#   ./scripts/run_kaggle_benchmark.sh --submit --message "QRATUM v1.0"

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPETITION_ID="chess-engine-leaderboard"
DATA_FILE="kaggle_leaderboard_data.json"
RESULTS_FILE="kaggle_benchmark_results.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
SUBMIT_FLAG=""
MESSAGE_FLAG=""
DRY_RUN_FLAG=""
USE_SAMPLE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --submit|-s)
            SUBMIT_FLAG="--submit"
            shift
            ;;
        --message|-m)
            MESSAGE_FLAG="--message \"$2\""
            shift 2
            ;;
        --dry-run)
            DRY_RUN_FLAG="--dry-run"
            shift
            ;;
        --sample)
            USE_SAMPLE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --submit, -s              Submit results to Kaggle leaderboard"
            echo "  --message, -m MESSAGE     Submission message/description"
            echo "  --dry-run                 Validate submission without posting"
            echo "  --sample                  Use sample positions (no download)"
            echo "  --help, -h                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Run benchmark only"
            echo "  $0 --submit                     # Run and submit"
            echo "  $0 --submit --message \"v1.0\"    # Run and submit with message"
            echo "  $0 --sample                     # Use sample positions"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║   🤖 QRATUM Chess - Kaggle Benchmark Wrapper                                 ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$REPO_ROOT"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check for Kaggle credentials if submitting
if [ -n "$SUBMIT_FLAG" ]; then
    if [ -f "$HOME/.kaggle/kaggle.json" ]; then
        echo -e "${GREEN}✓ Kaggle credentials found at ~/.kaggle/kaggle.json${NC}"
    elif [ -n "$KAGGLE_USERNAME" ] && [ -n "$KAGGLE_KEY" ]; then
        echo -e "${GREEN}✓ Kaggle credentials found in environment variables${NC}"
    else
        echo -e "${RED}✗ Kaggle credentials not found${NC}"
        echo ""
        echo "To submit results, you need Kaggle API credentials:"
        echo "1. Go to https://www.kaggle.com/settings"
        echo "2. Click 'Create New API Token'"
        echo "3. Save kaggle.json to ~/.kaggle/kaggle.json"
        echo ""
        echo "Or set environment variables:"
        echo "  export KAGGLE_USERNAME=your_username"
        echo "  export KAGGLE_KEY=your_api_key"
        exit 1
    fi
fi

# Download Kaggle leaderboard data (if not using sample)
if [ "$USE_SAMPLE" = false ]; then
    echo ""
    echo -e "${YELLOW}⬇ Attempting to download Kaggle leaderboard data...${NC}"
    
    # Try using kaggle CLI if available
    if command -v kaggle &> /dev/null; then
        echo "Using kaggle CLI..."
        if kaggle competitions leaderboard "$COMPETITION_ID" --show > "$DATA_FILE" 2>&1; then
            echo -e "${GREEN}✓ Downloaded leaderboard data via kaggle CLI${NC}"
        else
            echo -e "${YELLOW}⚠ Could not download via kaggle CLI, will use Python API${NC}"
            rm -f "$DATA_FILE"
        fi
    else
        echo "kaggle CLI not found, will use Python API"
    fi
    
    # If download failed or no CLI, use Python API download
    if [ ! -f "$DATA_FILE" ]; then
        echo "Will download via Python API during benchmark execution"
    fi
fi

# Run QRATUM Chess benchmark
echo ""
echo -e "${YELLOW}🚀 Running QRATUM Chess benchmark...${NC}"
echo ""

PYTHON_CMD="python3 qratum_chess/benchmarks/benchmark_kaggle.py"

if [ "$USE_SAMPLE" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --use-sample"
elif [ -f "$DATA_FILE" ]; then
    PYTHON_CMD="$PYTHON_CMD --input $DATA_FILE"
else
    PYTHON_CMD="$PYTHON_CMD --download"
fi

if [ -n "$SUBMIT_FLAG" ]; then
    PYTHON_CMD="$PYTHON_CMD $SUBMIT_FLAG"
fi

if [ -n "$MESSAGE_FLAG" ]; then
    PYTHON_CMD="$PYTHON_CMD $MESSAGE_FLAG"
fi

if [ -n "$DRY_RUN_FLAG" ]; then
    PYTHON_CMD="$PYTHON_CMD $DRY_RUN_FLAG"
fi

PYTHON_CMD="$PYTHON_CMD --output $RESULTS_FILE"

# Execute benchmark
if eval $PYTHON_CMD; then
    echo ""
    echo -e "${GREEN}✓ Benchmark completed successfully${NC}"
    
    # Show results summary
    if [ -f "$RESULTS_FILE" ]; then
        echo ""
        echo -e "${BLUE}Results saved to: $RESULTS_FILE${NC}"
        
        # Extract summary from JSON
        if command -v jq &> /dev/null; then
            echo ""
            echo "Quick Summary:"
            jq -r '.metadata | "  Engine: \(.engine)\n  Positions: \(.total_positions)\n  Depth: \(.depth)\n  Time limit: \(.time_limit_ms) ms"' "$RESULTS_FILE"
        fi
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}✗ Benchmark failed${NC}"
    exit 1
fi
