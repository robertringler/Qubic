# Kaggle Chess Benchmark Integration for QRATUM-Chess

This document describes how to use the Kaggle Chess Leaderboard API integration with QRATUM-Chess benchmarking infrastructure.

## Overview

The Kaggle integration allows you to:
- Download and parse Kaggle chess leaderboard data
- Run QRATUM engine against benchmark positions from Kaggle
- Compare QRATUM's performance with other engines on the leaderboard
- Integrate Kaggle benchmarks into the adversarial gauntlet

## Setup

### Prerequisites

1. **Python 3.8+** with the following packages:
   - All standard QRATUM-Chess dependencies
   - `requests` (optional, for API access)

2. **curl** - For downloading leaderboard data

3. **Kaggle API Credentials** (Optional):
   If you want to use authenticated Kaggle API access:
   
   ```bash
   # Create Kaggle API credentials file
   mkdir -p ~/.kaggle
   echo '{"username":"YOUR_USERNAME","key":"YOUR_API_KEY"}' > ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   ```
   
   Get your API key from: https://www.kaggle.com/settings/account

### Installation

No additional installation is required. The Kaggle integration modules are part of the QRATUM-Chess benchmarking suite.

## Usage

### Quick Start - Shell Script

The easiest way to run a Kaggle benchmark:

```bash
# Run with default settings
./scripts/run_kaggle_benchmark.sh

# Quick mode (reduced depth and positions)
./scripts/run_kaggle_benchmark.sh --quick

# Custom depth
./scripts/run_kaggle_benchmark.sh --depth 20

# Limit number of positions
./scripts/run_kaggle_benchmark.sh --max-positions 50

# Custom output directory
./scripts/run_kaggle_benchmark.sh --output-dir ~/my_results
```

### Python API

#### Load Kaggle Leaderboard Data

```python
from qratum_chess.benchmarks.kaggle_integration import KaggleLeaderboardLoader

# Load from file
loader = KaggleLeaderboardLoader()
leaderboard = loader.load_from_file("kaggle_chess_leaderboard.json")

# Access leaderboard data
print(f"Benchmark: {leaderboard.benchmark_name}")
print(f"Version: {leaderboard.version}")
print(f"Test positions: {len(leaderboard.test_positions)}")
print(f"Submissions: {len(leaderboard.submissions)}")

# Get top submissions
top_5 = loader.get_top_submissions(n=5, leaderboard=leaderboard)
for sub in top_5:
    print(f"#{sub.rank}: {sub.team_name} - {sub.score}")
```

#### Run Benchmark

```python
from qratum_chess.benchmarks.kaggle_integration import KaggleLeaderboardLoader
from qratum_chess.benchmarks.benchmark_kaggle import KaggleBenchmarkRunner
from qratum_chess.search.aas import AsymmetricAdaptiveSearch

# Initialize components
loader = KaggleLeaderboardLoader()
runner = KaggleBenchmarkRunner()
engine = AsymmetricAdaptiveSearch()

# Load leaderboard
leaderboard = loader.load_from_file("kaggle_chess_leaderboard.json")

# Run benchmark
results = runner.run_benchmark(
    engine,
    leaderboard,
    depth=15,                # Search depth
    time_limit_ms=5000,     # Optional time limit per position
    max_positions=100        # Optional position limit
)

# Generate and print summary
summary = runner.generate_summary(results)
runner.print_summary(summary)

# Save results
output_path = runner.save_results("benchmarks/kaggle_results/", results)
print(f"Results saved to: {output_path}")
```

#### Compare with Leaderboard

```python
# Compare QRATUM with leaderboard
comparison = runner.compare_with_leaderboard(leaderboard, summary)

print(f"QRATUM score: {comparison['qratum_score']*100:.1f}%")
print(f"Estimated rank: #{comparison['estimated_rank']}")
print("\nTop 5 submissions:")
for sub in comparison['top_submissions']:
    print(f"  #{sub['rank']}: {sub['team_name']} - {sub['score']:.4f}")
```

#### Integration with Adversarial Gauntlet

```python
from qratum_chess.benchmarks.gauntlet import AdversarialGauntlet, AdversaryType

# Initialize gauntlet
gauntlet = AdversarialGauntlet(engine_name="QRATUM-Chess")

# Run Kaggle benchmark as adversary
kaggle_score = gauntlet.run_kaggle_benchmark_adversary(
    engine,
    leaderboard_file="kaggle_chess_leaderboard.json",
    depth=15,
    max_positions=50
)

print(f"Kaggle adversary score: {kaggle_score*100:.1f}%")
```

### Download Kaggle Data Manually

```bash
# Download leaderboard data
curl -L -o ~/Downloads/kaggle_chess_leaderboard.json \
  https://www.kaggle.com/api/v1/benchmarks/kaggle/chess/versions/1/leaderboard

# Or use Python
python3 -c "
from qratum_chess.benchmarks.kaggle_integration import download_kaggle_leaderboard
download_kaggle_leaderboard('~/Downloads/kaggle_chess_leaderboard.json')
"
```

## Output Format

### Results JSON Structure

```json
{
  "results": [
    {
      "test_id": "test_001",
      "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
      "best_move": "e2e4",
      "evaluation": 0.25,
      "depth_reached": 15,
      "nodes_searched": 125000,
      "time_ms": 450.2,
      "expected_move": "e2e4",
      "expected_eval": 0.20,
      "move_matches": true,
      "eval_diff": 0.05,
      "category": "opening",
      "difficulty": "easy"
    }
  ],
  "summary": {
    "total_positions": 50,
    "move_accuracy": 0.82,
    "avg_eval_diff": 0.15,
    "avg_depth": 14.8,
    "avg_nodes": 120000,
    "avg_time_ms": 425.5,
    "total_time_ms": 21275.0,
    "results_by_category": {
      "opening": {"count": 10, "move_accuracy": 0.90},
      "middlegame": {"count": 25, "move_accuracy": 0.80},
      "endgame": {"count": 15, "move_accuracy": 0.75}
    },
    "results_by_difficulty": {
      "easy": {"count": 15, "move_accuracy": 0.95},
      "medium": {"count": 20, "move_accuracy": 0.85},
      "hard": {"count": 15, "move_accuracy": 0.70}
    }
  }
}
```

## Metrics Explanation

### Move Accuracy
Percentage of positions where QRATUM's best move matches the expected/reference move from the Kaggle benchmark. This is the primary metric for comparison.

### Evaluation Difference
Average absolute difference between QRATUM's position evaluation and the expected evaluation. Lower is better.

### Nodes Per Second (NPS)
Calculated as `avg_nodes / (avg_time_ms / 1000)`. Indicates search efficiency.

### Search Depth
Average depth reached during search. Higher depth generally indicates more thorough analysis.

### Category Breakdown
- **Opening**: Standard opening positions
- **Middlegame**: Complex tactical and strategic positions
- **Endgame**: Endgame positions requiring precise calculation

### Difficulty Breakdown
- **Easy**: Straightforward positions with clear best moves
- **Medium**: Positions requiring tactical awareness
- **Hard**: Complex positions with non-obvious solutions

## Integration with Existing Benchmarks

The Kaggle integration is designed to work seamlessly with QRATUM's existing benchmark infrastructure:

```python
from qratum_chess.benchmarks.runner import BenchmarkRunner, BenchmarkConfig

# Create benchmark config with Kaggle gauntlet enabled
config = BenchmarkConfig(
    run_gauntlet=True,
    gauntlet_games=100
)

# Run full benchmark suite
runner = BenchmarkRunner(config)
summary = runner.run(engine, evaluator=None)

# Kaggle adversary will be included if registered in gauntlet
```

## Troubleshooting

### Issue: Download fails

**Problem**: `curl` fails to download leaderboard data

**Solution**:
- Check internet connection
- Verify the Kaggle API endpoint is accessible
- Try downloading manually and specifying the file path
- Use fallback mode (script will use standard positions)

### Issue: No test positions in leaderboard

**Problem**: Leaderboard JSON doesn't contain test positions

**Solution**: The loader will automatically fall back to standard benchmark positions. This is normal for some Kaggle benchmark formats.

### Issue: Engine search fails

**Problem**: Engine throws errors during search

**Solution**:
- Reduce search depth with `--depth 10`
- Add time limit with `--time-limit 3000`
- Check that the engine is properly initialized
- Verify Position objects are valid

### Issue: Slow performance

**Problem**: Benchmark takes too long to run

**Solution**:
- Use `--quick` mode for faster testing
- Reduce `--max-positions` to test fewer positions
- Lower `--depth` to reduce search time
- Add `--time-limit` to cap search time per position

## Advanced Usage

### Custom Position Sets

```python
# Create custom benchmark positions
from qratum_chess.benchmarks.kaggle_integration import (
    KaggleBenchmarkPosition,
    KaggleLeaderboard
)
from qratum_chess.core.position import Position

positions = [
    KaggleBenchmarkPosition(
        fen="your_fen_here",
        position=Position.from_fen("your_fen_here"),
        test_id="custom_001",
        category="custom",
        difficulty="hard"
    )
]

leaderboard = KaggleLeaderboard(
    benchmark_name="custom_benchmark",
    version="1.0",
    test_positions=positions
)

# Run benchmark with custom positions
runner = KaggleBenchmarkRunner()
results = runner.run_benchmark(engine, leaderboard, depth=15)
```

### Batch Processing

```python
# Process multiple leaderboard files
import glob

for leaderboard_file in glob.glob("data/kaggle_*.json"):
    print(f"Processing {leaderboard_file}...")
    leaderboard = loader.load_from_file(leaderboard_file)
    results = runner.run_benchmark(engine, leaderboard, depth=12)
    runner.save_results(f"results/{Path(leaderboard_file).stem}/")
```

## API Reference

### KaggleLeaderboardLoader

- `load_from_file(filepath)`: Load leaderboard from JSON file
- `load_from_dict(data)`: Load leaderboard from dictionary
- `parse_leaderboard(data)`: Parse raw Kaggle API data
- `extract_positions(leaderboard)`: Extract benchmark positions
- `get_top_submissions(n, leaderboard)`: Get top N submissions
- `export_positions_to_fen_file(filepath)`: Export positions as FEN

### KaggleBenchmarkRunner

- `run_benchmark(engine, leaderboard, depth, time_limit_ms, max_positions)`: Run full benchmark
- `generate_summary(results)`: Generate summary statistics
- `save_results(output_dir, results)`: Save results to files
- `print_summary(summary)`: Print summary to console
- `compare_with_leaderboard(leaderboard, summary)`: Compare with leaderboard

### AdversarialGauntlet

- `run_kaggle_benchmark_adversary(engine, leaderboard_file, depth, max_positions)`: Run as adversary test

## Support

For issues, questions, or contributions related to the Kaggle integration:

1. Check the main QRATUM-Chess documentation
2. Review the benchmark runner documentation in `qratum_chess/benchmarks/`
3. Consult the existing test files for usage examples

## Future Enhancements

Planned improvements:
- Direct API authentication for automated downloads
- Support for submitting results to Kaggle (if API allows)
- More sophisticated position selection algorithms
- Multi-engine comparison mode
- Visualization dashboard for results

## License

This integration is part of QRATUM-Chess and follows the same license terms as the main project.
