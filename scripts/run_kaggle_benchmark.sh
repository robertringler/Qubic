#!/bin/bash
# run_kaggle_benchmark.sh
#
# Kaggle Chess Benchmark Runner for QRATUM-Chess
#
# This script:
# 1. Downloads the latest Kaggle chess leaderboard data
# 2. Runs QRATUM engine against benchmark positions
# 3. Generates comparison report with leaderboard
#
# Usage:
#   ./scripts/run_kaggle_benchmark.sh
#   ./scripts/run_kaggle_benchmark.sh --depth 20
#   ./scripts/run_kaggle_benchmark.sh --quick

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEPTH=15
TIME_LIMIT=""
MAX_POSITIONS=""
KAGGLE_DATA_DIR="$HOME/.kaggle_chess"
OUTPUT_DIR="benchmarks/kaggle_results"
QUICK_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
            echo "  --depth N              Search depth (default: 15)"
            echo "  --time-limit MS        Time limit per position in ms"
            echo "  --max-positions N      Maximum positions to test"
            echo "  --output-dir DIR       Output directory (default: benchmarks/kaggle_results)"
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
echo "║   🤖 QRATUM-Chess Kaggle Benchmark Runner                                    ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create directories
mkdir -p "$KAGGLE_DATA_DIR"
mkdir -p "$OUTPUT_DIR"

# Download Kaggle leaderboard data
LEADERBOARD_FILE="$KAGGLE_DATA_DIR/kaggle_chess_leaderboard.json"
echo -e "${YELLOW}[1/3] Downloading Kaggle chess leaderboard data...${NC}"

if command -v curl &> /dev/null; then
    curl -L -o "$LEADERBOARD_FILE" \
        https://www.kaggle.com/api/v1/benchmarks/kaggle/chess/versions/1/leaderboard \
        2>&1 | grep -E "(%|curl)" || true
    
    if [ -f "$LEADERBOARD_FILE" ] && [ -s "$LEADERBOARD_FILE" ]; then
        echo -e "${GREEN}✓ Leaderboard data downloaded successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Download may have failed, will use fallback positions${NC}"
    fi
else
    echo -e "${RED}✗ Error: curl not found. Please install curl.${NC}"
    exit 1
fi

# Run the benchmark
echo -e "${YELLOW}[2/3] Running QRATUM engine benchmark...${NC}"
echo "  Configuration:"
echo "    - Search depth: $DEPTH"
if [ -n "$TIME_LIMIT" ]; then
    echo "    - Time limit: ${TIME_LIMIT}ms"
fi
if [ -n "$MAX_POSITIONS" ]; then
    echo "    - Max positions: $MAX_POSITIONS"
fi
echo ""

# Build Python command
PYTHON_CMD="python3 -c \"
import sys
from pathlib import Path

# Add repository to path
repo_root = Path('$PWD')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from qratum_chess.benchmarks.kaggle_integration import KaggleLeaderboardLoader
from qratum_chess.benchmarks.benchmark_kaggle import KaggleBenchmarkRunner
from qratum_chess.search.aas import AsymmetricAdaptiveSearch

# Initialize components
loader = KaggleLeaderboardLoader()
runner = KaggleBenchmarkRunner()
engine = AsymmetricAdaptiveSearch()

# Load leaderboard
print('Loading Kaggle leaderboard data...')
try:
    leaderboard = loader.load_from_file('$LEADERBOARD_FILE')
    print(f'Loaded {len(leaderboard.test_positions)} test positions')
except Exception as e:
    print(f'Warning: Failed to load leaderboard: {e}')
    print('Using standard benchmark positions instead')
    leaderboard = loader.parse_leaderboard({})

# Run benchmark
results = runner.run_benchmark(
    engine,
    leaderboard,
    depth=$DEPTH,
    time_limit_ms=${TIME_LIMIT:-None},
    max_positions=${MAX_POSITIONS:-None}
)

# Generate and print summary
summary = runner.generate_summary(results)
runner.print_summary(summary)

# Save results
output_path = runner.save_results('$OUTPUT_DIR', results)
print(f'\\nResults saved to: {output_path}')

# Compare with leaderboard
comparison = runner.compare_with_leaderboard(leaderboard, summary)
print('\\nLeaderboard Comparison:')
print(f'  QRATUM score: {comparison[\"qratum_score\"]*100:.1f}%')
print(f'  Estimated rank: #{comparison[\"estimated_rank\"]}')
print('\\n  Top 5 submissions:')
for sub in comparison['top_submissions'][:5]:
    print(f'    #{sub[\"rank\"]}: {sub[\"team_name\"]} - {sub[\"score\"]:.4f}')
\""

# Execute Python benchmark
if eval "$PYTHON_CMD"; then
    echo -e "${GREEN}✓ Benchmark completed successfully${NC}"
else
    echo -e "${RED}✗ Benchmark failed${NC}"
    exit 1
fi

# Generate summary report
echo -e "${YELLOW}[3/3] Generating summary report...${NC}"

REPORT_FILE="$OUTPUT_DIR/latest_report.txt"
cat > "$REPORT_FILE" << EOF
QRATUM-Chess Kaggle Benchmark Report
====================================
Generated: $(date)

Configuration:
  - Search depth: $DEPTH
  - Time limit: ${TIME_LIMIT:-None}
  - Max positions: ${MAX_POSITIONS:-All}
  - Output directory: $OUTPUT_DIR

Results:
  See JSON files in $OUTPUT_DIR for detailed results.

To view results:
  cat $OUTPUT_DIR/kaggle_summary_*.json | jq .

EOF

echo -e "${GREEN}✓ Report saved to: $REPORT_FILE${NC}"

# Print completion message
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}✓ Kaggle benchmark completed successfully${NC}                                   ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                                              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  Results location: $OUTPUT_DIR${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

exit 0
