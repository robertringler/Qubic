#!/bin/bash
# run_kaggle_benchmark.sh
#
# QRATUM-Chess Kaggle Competition Pipeline
#
# Fully automated pipeline for Kaggle chess competition domination:
# 1. Downloads real Kaggle competition data
# 2. Runs actual QRATUM engine (no mocks)
# 3. Produces compliant Kaggle submissions
# 4. Submits automatically
# 5. Tracks ranking, ELO, novelty motifs, and performance drift
# 6. Iterates hyperparameters based on leaderboard feedback
#
# Usage:
#   ./scripts/run_kaggle_benchmark.sh --submit --optimize --track --no-mock
#   ./scripts/run_kaggle_benchmark.sh --competition chess-competition
#   ./scripts/run_kaggle_benchmark.sh --quick

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
COMPETITION=""
DEPTH=15
TIME_LIMIT=""
MAX_POSITIONS=""
DATA_DIR="data/kaggle/current"
OUTPUT_DIR="submissions"
QUICK_MODE=false
SUBMIT=false
OPTIMIZE=false
TRACK=false
NO_MOCK=false
ENABLE_TRIMODAL=false
ENABLE_NOVELTY=false
NOVELTY_PRESSURE=0.5

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --competition|-c)
            COMPETITION="$2"
            shift 2
            ;;
        --depth)
            DEPTH="$2"
            shift 2
            ;;
        --time-limit)
            TIME_LIMIT="$2"
            shift 2
            ;;
        --max-positions)
            MAX_POSITIONS="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --submit)
            SUBMIT=true
            shift
            ;;
        --optimize)
            OPTIMIZE=true
            shift
            ;;
        --track)
            TRACK=true
            shift
            ;;
        --no-mock)
            NO_MOCK=true
            shift
            ;;
        --enable-trimodal)
            ENABLE_TRIMODAL=true
            shift
            ;;
        --enable-novelty-pressure)
            ENABLE_NOVELTY=true
            shift
            ;;
        --novelty-pressure)
            NOVELTY_PRESSURE="$2"
            shift 2
            ;;
        --quick)
            QUICK_MODE=true
            DEPTH=10
            MAX_POSITIONS=20
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --competition, -c ID   Kaggle competition ID"
            echo "  --depth N              Search depth (default: 15)"
            echo "  --time-limit MS        Time limit per position in ms"
            echo "  --max-positions N      Maximum positions to test"
            echo "  --output-dir DIR       Output directory (default: submissions)"
            echo "  --submit               Submit to Kaggle after generation"
            echo "  --optimize             Enable hyperparameter optimization"
            echo "  --track                Track leaderboard ranking"
            echo "  --no-mock              Enforce no mock data (real competition only)"
            echo "  --enable-trimodal      Enable tri-modal cortex fusion"
            echo "  --enable-novelty-pressure  Enable novelty pressure"
            echo "  --novelty-pressure N   Novelty pressure value (0.0-1.0, default: 0.5)"
            echo "  --quick                Quick mode (depth=10, max=20)"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║   🏆 QRATUM-Chess Kaggle Competition Pipeline                                ║"
echo "║                                                                              ║"
echo "║   Objective: Sustained Leaderboard Supremacy                                 ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verify Kaggle CLI is installed
if ! command -v kaggle &> /dev/null; then
    echo -e "${RED}✗ Error: Kaggle CLI not found. Install with: pip install kaggle${NC}"
    exit 1
fi

# Check for Kaggle credentials
if [ ! -f "$HOME/.kaggle/kaggle.json" ] && [ -z "$KAGGLE_USERNAME" ]; then
    echo -e "${RED}✗ Error: Kaggle credentials not found.${NC}"
    echo "Please either:"
    echo "  1. Create ~/.kaggle/kaggle.json with your API credentials"
    echo "  2. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables"
    echo "Get your API key from: https://www.kaggle.com/settings/account"
    exit 1
fi

# Create directories
mkdir -p "$DATA_DIR"
mkdir -p "$OUTPUT_DIR"

# Build Python command
PYTHON_CMD="python3 run_qratum_chess_kaggle.py"

# Add competition if specified
if [ -n "$COMPETITION" ]; then
    PYTHON_CMD="$PYTHON_CMD --competition $COMPETITION"
fi

# Add depth
PYTHON_CMD="$PYTHON_CMD --depth $DEPTH"

# Add time limit if specified
if [ -n "$TIME_LIMIT" ]; then
    PYTHON_CMD="$PYTHON_CMD --time-limit $TIME_LIMIT"
fi

# Add max positions if specified
if [ -n "$MAX_POSITIONS" ]; then
    PYTHON_CMD="$PYTHON_CMD --max-positions $MAX_POSITIONS"
fi

# Add output directory
PYTHON_CMD="$PYTHON_CMD --output-dir $OUTPUT_DIR"

# Add flags
if [ "$SUBMIT" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --submit"
fi

if [ "$OPTIMIZE" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --optimize"
fi

if [ "$TRACK" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --track"
fi

if [ "$NO_MOCK" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --no-mock"
fi

if [ "$ENABLE_TRIMODAL" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --enable-trimodal"
fi

if [ "$ENABLE_NOVELTY" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --enable-novelty-pressure --novelty-pressure $NOVELTY_PRESSURE"
fi

# Add disable randomness for reproducibility
PYTHON_CMD="$PYTHON_CMD --disable-randomness"

# Print configuration
echo -e "${YELLOW}Configuration:${NC}"
if [ -n "$COMPETITION" ]; then
    echo "  Competition: $COMPETITION"
fi
echo "  Search depth: $DEPTH"
if [ -n "$TIME_LIMIT" ]; then
    echo "  Time limit: ${TIME_LIMIT}ms"
fi
if [ -n "$MAX_POSITIONS" ]; then
    echo "  Max positions: $MAX_POSITIONS"
fi
echo "  Submit: $SUBMIT"
echo "  Optimize: $OPTIMIZE"
echo "  Track: $TRACK"
if [ "$ENABLE_NOVELTY" = true ]; then
    echo "  Novelty pressure: $NOVELTY_PRESSURE"
fi
echo ""

# Execute pipeline
echo -e "${YELLOW}Running QRATUM-Chess Kaggle Pipeline...${NC}"
echo ""

if eval "$PYTHON_CMD"; then
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}✓ Pipeline completed successfully${NC}                                           ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}✗ Pipeline failed${NC}"
    exit 1
fi
