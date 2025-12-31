# Kaggle Chess Leaderboard Integration

Complete guide for running QRATUM Chess engine benchmarks against Kaggle chess positions and submitting results to Kaggle leaderboards.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [API Configuration](#api-configuration)
- [Submission Workflow](#submission-workflow)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

## Overview

The Kaggle integration enables QRATUM Chess to:

1. **Load benchmark positions** from Kaggle chess competitions
2. **Run engine analysis** using AsymmetricAdaptiveSearch (AAS)
3. **Format results** according to Kaggle submission requirements
4. **Submit results** to Kaggle leaderboards
5. **Track performance** and leaderboard rankings

### Features

✅ Kaggle API authentication and credential management  
✅ Download benchmark positions from competitions  
✅ Run QRATUM engine against test positions  
✅ Format results for CSV/JSON submission  
✅ Automatic submission to Kaggle leaderboards  
✅ Leaderboard ranking retrieval  
✅ Comprehensive error handling  
✅ Dry-run mode for testing  
✅ Integration with existing benchmark suite

## Setup

### 1. Install Dependencies

```bash
pip install kaggle>=1.6.0
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### 2. Obtain Kaggle API Credentials

#### Option A: Web Interface

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json` to `~/.kaggle/kaggle.json`

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

#### Option B: Manual Creation

Create `~/.kaggle/kaggle.json`:

```json
{
  "username": "your_kaggle_username",
  "key": "your_api_key_here"
}
```

Then set permissions:

```bash
chmod 600 ~/.kaggle/kaggle.json
```

#### Option C: Environment Variables

```bash
export KAGGLE_USERNAME="your_kaggle_username"
export KAGGLE_KEY="your_api_key_here"
```

### 3. Verify Setup

```bash
# Test Kaggle API access
python3 -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✓ Authentication successful')"
```

## Usage

### Command Line Interface

#### Basic Benchmark (No Submission)

```bash
# Using Python script
python3 qratum_chess/benchmarks/benchmark_kaggle.py

# Using shell wrapper
./scripts/run_kaggle_benchmark.sh
```

#### Benchmark with Submission

```bash
# Submit to Kaggle
python3 qratum_chess/benchmarks/benchmark_kaggle.py --submit

# Submit with custom message
python3 qratum_chess/benchmarks/benchmark_kaggle.py --submit --message "QRATUM v1.0 - AAS engine"

# Using shell wrapper
./scripts/run_kaggle_benchmark.sh --submit --message "QRATUM v1.0"
```

#### Advanced Options

```bash
# Download fresh data from Kaggle
python3 qratum_chess/benchmarks/benchmark_kaggle.py --download --submit

# Use local data file
python3 qratum_chess/benchmarks/benchmark_kaggle.py --input kaggle_data.json

# Dry run (validate without submitting)
python3 qratum_chess/benchmarks/benchmark_kaggle.py --submit --dry-run

# Custom search parameters
python3 qratum_chess/benchmarks/benchmark_kaggle.py --depth 20 --time-limit 10000

# Use sample positions for testing
python3 qratum_chess/benchmarks/benchmark_kaggle.py --use-sample
```

### Python API

#### Basic Usage

```python
from qratum_chess.benchmarks import (
    KaggleConfig,
    KaggleIntegration,
    KaggleSubmission,
)

# Load configuration
config = KaggleConfig()

# Load benchmark positions
integration = KaggleIntegration(config)
positions = integration.create_sample_positions()

# Run benchmark (implement your benchmark logic)
results = run_my_benchmark(positions)

# Submit to Kaggle
submission = KaggleSubmission(config)
result = submission.submit_to_kaggle(
    results,
    message="QRATUM Chess v1.0"
)

print(f"Success: {result.success}")
print(f"Submission ID: {result.submission_id}")
```

#### Download Leaderboard Data

```python
from qratum_chess.benchmarks import KaggleIntegration, KaggleConfig

config = KaggleConfig()
integration = KaggleIntegration(config)

# Download leaderboard
leaderboard = integration.download_leaderboard_data(
    competition_id="chess-engine-leaderboard",
    save_path="leaderboard.json"
)

print(f"Positions: {len(leaderboard.positions)}")
print(f"Top engines: {leaderboard.get_top_engines(n=5)}")
```

#### Load from File

```python
from qratum_chess.benchmarks import KaggleIntegration

integration = KaggleIntegration()
leaderboard = integration.load_leaderboard_from_file("kaggle_data.json")

for position in leaderboard.positions:
    print(f"{position.position_id}: {position.fen}")
```

## API Configuration

### Competition Configuration

```python
from qratum_chess.benchmarks.kaggle_config import KaggleCompetitionConfig

config = KaggleCompetitionConfig(
    competition_id="chess-engine-leaderboard",
    competition_name="Chess Engine Leaderboard",
    submission_format="csv",
    required_fields=["position_id", "best_move", "evaluation"]
)
```

### Submission Format

```python
from qratum_chess.benchmarks.kaggle_config import SubmissionFormat

format_spec = SubmissionFormat(
    format_type="csv",
    headers=["position_id", "best_move", "evaluation", "nodes_searched", "time_ms"]
)

# Validate submission data
is_valid, error = format_spec.validate_submission_data(results)
```

## Submission Workflow

### 1. Prepare Results

Results must be a list of dictionaries with required fields:

```python
results = [
    {
        "position_id": "pos_1",
        "best_move": "e2e4",
        "evaluation": 0.25,
        "nodes_searched": 1000000,
        "time_ms": 150.5
    },
    {
        "position_id": "pos_2",
        "best_move": "d2d4",
        "evaluation": 0.15,
        "nodes_searched": 950000,
        "time_ms": 145.2
    },
    # ... more results
]
```

### 2. Validate Format

```python
from qratum_chess.benchmarks import KaggleSubmission, KaggleConfig

config = KaggleConfig()
submission = KaggleSubmission(config)

is_valid, error = submission.validate_submission(results)
if not is_valid:
    print(f"Validation error: {error}")
```

### 3. Submit

```python
# Submit to Kaggle
result = submission.submit_to_kaggle(
    results,
    message="QRATUM Chess Engine v1.0",
    dry_run=False  # Set to True for testing
)

if result.success:
    print(f"✓ Submitted: {result.submission_id}")
else:
    print(f"✗ Failed: {result.error}")
```

### 4. Check Status

```python
# Wait for scoring
if result.submission_id:
    status = submission.get_submission_status(
        result.submission_id,
        timeout=300  # 5 minutes
    )
    
    print(f"Score: {status.score}")
    print(f"Position: {status.leaderboard_position}")
```

### 5. Display Summary

```python
submission.display_submission_summary(result)
```

Output:
```
======================================================================
Kaggle Submission Summary
======================================================================
✓ Status: SUCCESS
  Submission ID: 12345678
  Message: Submission successful
  Score: 0.8542
  
  Current Leaderboard Standing:
    Position: #15
    Score: 0.8542
======================================================================
```

## Examples

### Example 1: Simple Benchmark

```bash
# Run on sample positions (no Kaggle API needed)
python3 qratum_chess/benchmarks/benchmark_kaggle.py --use-sample
```

### Example 2: Download and Benchmark

```bash
# Download fresh data and run benchmark
python3 qratum_chess/benchmarks/benchmark_kaggle.py --download
```

### Example 3: Benchmark and Submit

```bash
# Complete workflow: download, benchmark, submit
python3 qratum_chess/benchmarks/benchmark_kaggle.py \
    --download \
    --submit \
    --message "QRATUM AAS v1.0 - depth 20" \
    --depth 20 \
    --time-limit 10000
```

### Example 4: Shell Script

```bash
# Simple submission
./scripts/run_kaggle_benchmark.sh --submit

# With custom message
./scripts/run_kaggle_benchmark.sh --submit --message "QRATUM v1.0"

# Dry run test
./scripts/run_kaggle_benchmark.sh --submit --dry-run
```

### Example 5: Integration with Gauntlet

```python
from qratum_chess.benchmarks import AdversarialGauntlet, KaggleIntegration
from qratum_chess.search.aas import AsymmetricAdaptiveSearch

# Initialize engine
engine = AsymmetricAdaptiveSearch()

# Load Kaggle positions
integration = KaggleIntegration()
positions = integration.create_sample_positions()

# Run gauntlet benchmark
gauntlet = AdversarialGauntlet()
match_rate, results = gauntlet.run_kaggle_benchmark(
    engine,
    positions,
    depth=15,
    time_limit_ms=5000
)

print(f"Match rate: {match_rate * 100:.1f}%")
```

## Troubleshooting

### Authentication Errors

**Problem:** `Kaggle credentials not found`

**Solutions:**
1. Verify `~/.kaggle/kaggle.json` exists and has correct format
2. Check file permissions: `chmod 600 ~/.kaggle/kaggle.json`
3. Try using environment variables instead
4. Re-download credentials from Kaggle website

### API Request Failures

**Problem:** `HTTP 401: Unauthorized`

**Solutions:**
1. Check API key is valid and not expired
2. Verify username matches your Kaggle account
3. Ensure API access is enabled in account settings

**Problem:** `HTTP 404: Not Found`

**Solutions:**
1. Verify competition ID is correct
2. Check you have accepted competition rules
3. Ensure competition is still active

**Problem:** `HTTP 429: Too Many Requests`

**Solutions:**
1. Wait a few minutes before retrying
2. Reduce submission frequency
3. Check Kaggle API rate limits

### Submission Errors

**Problem:** `Validation failed: Missing required field`

**Solutions:**
1. Check all required fields are present in results
2. Verify field names match submission format
3. Ensure no null/missing values

**Problem:** `Invalid submission format`

**Solutions:**
1. Verify CSV headers match required format
2. Check for correct data types
3. Ensure no duplicate position IDs

### Data Loading Errors

**Problem:** `No positions found in leaderboard data`

**Solutions:**
1. Use `--use-sample` flag for testing
2. Check JSON file structure
3. Try downloading fresh data
4. Verify competition has test data available

## API Reference

### KaggleConfig

Configuration management for Kaggle API.

```python
config = KaggleConfig(
    credentials_path=None,  # Path to kaggle.json
    use_env_credentials=False,  # Use env vars
    competition_config=None,  # Competition settings
    submission_format=None  # Format specification
)
```

### KaggleIntegration

Load and parse Kaggle leaderboard data.

```python
integration = KaggleIntegration(config=None)

# Load from file
leaderboard = integration.load_leaderboard_from_file("data.json")

# Download from API
leaderboard = integration.download_leaderboard_data(
    competition_id="chess-engine-leaderboard",
    save_path="leaderboard.json"
)

# Create sample positions
positions = integration.create_sample_positions()
```

### KaggleSubmission

Submit results to Kaggle competitions.

```python
submission = KaggleSubmission(config)

# Submit results
result = submission.submit_to_kaggle(
    results,
    message="Submission message",
    dry_run=False
)

# Check status
status = submission.get_submission_status(submission_id, timeout=300)

# Get leaderboard position
position, score = submission.get_leaderboard_position(username=None)

# Display summary
submission.display_submission_summary(result)
```

### KaggleBenchmarkPosition

Represents a single benchmark position.

```python
position = KaggleBenchmarkPosition(
    position_id="pos_1",
    fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    description="Starting position",
    expected_move="e2e4",
    difficulty=1.0
)

# Access QRATUM Position
qratum_pos = position.position
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Never commit credentials** to version control
2. `.kaggle/` and `kaggle.json` are in `.gitignore`
3. Set proper file permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Use environment variables in CI/CD pipelines
5. Rotate API keys regularly
6. Validate all API responses before processing
7. Handle rate limiting gracefully

## Performance Tips

1. **Cache downloaded data** to avoid repeated API calls
2. **Use appropriate depth** for time constraints
3. **Batch positions** for efficient processing
4. **Monitor rate limits** to avoid API throttling
5. **Use dry-run** mode for testing submissions

## Support

For issues or questions:

1. Check this documentation
2. Review troubleshooting section
3. Check Kaggle API documentation: https://github.com/Kaggle/kaggle-api
4. Review QRATUM Chess benchmark docs: `qratum_chess/benchmarks/README_AUTOMATION.md`

## License

QRATUM Chess Kaggle Integration is part of the QRATUM project.
See LICENSE file for details.
