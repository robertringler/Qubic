#!/usr/bin/env python3
"""QRATUM Chess Kaggle Benchmark Script.

Runs QRATUM AsymmetricAdaptiveSearch engine against Kaggle benchmark positions
and optionally submits results to the Kaggle leaderboard.

Usage:
    python qratum_chess/benchmarks/benchmark_kaggle.py
    python qratum_chess/benchmarks/benchmark_kaggle.py --submit
    python qratum_chess/benchmarks/benchmark_kaggle.py --submit --message "QRATUM v1.0"
    python qratum_chess/benchmarks/benchmark_kaggle.py --input kaggle_data.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add repository root to path
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from qratum_chess.benchmarks.kaggle_config import KaggleConfig, load_config
from qratum_chess.benchmarks.kaggle_integration import (
    KaggleIntegration,
    KaggleBenchmarkPosition,
)
from qratum_chess.benchmarks.kaggle_submission import KaggleSubmission
from qratum_chess.search.aas import AsymmetricAdaptiveSearch, AASConfig
from qratum_chess.core.position import Position


def print_banner() -> None:
    """Print the Kaggle benchmark banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🤖 QRATUM Chess - Kaggle Leaderboard Benchmark                             ║
║                                                                              ║
║   AsymmetricAdaptiveSearch vs Kaggle Chess Positions                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run QRATUM Chess engine against Kaggle benchmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to Kaggle leaderboard JSON file (if not downloading)",
    )
    
    parser.add_argument(
        "--download", "-d",
        action="store_true",
        help="Download fresh data from Kaggle API",
    )
    
    parser.add_argument(
        "--competition",
        type=str,
        default="chess-engine-leaderboard",
        help="Kaggle competition ID (default: chess-engine-leaderboard)",
    )
    
    parser.add_argument(
        "--submit", "-s",
        action="store_true",
        help="Submit results to Kaggle leaderboard",
    )
    
    parser.add_argument(
        "--message", "-m",
        type=str,
        default="QRATUM Chess Engine - AsymmetricAdaptiveSearch",
        help="Submission message/description",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate submission format without actually submitting",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="kaggle_benchmark_results.json",
        help="Output file for results (default: kaggle_benchmark_results.json)",
    )
    
    parser.add_argument(
        "--depth",
        type=int,
        default=15,
        help="Search depth for engine (default: 15)",
    )
    
    parser.add_argument(
        "--time-limit",
        type=float,
        default=5000.0,
        help="Time limit per position in milliseconds (default: 5000)",
    )
    
    parser.add_argument(
        "--use-sample",
        action="store_true",
        help="Use sample positions instead of real Kaggle data",
    )
    
    parser.add_argument(
        "--credentials",
        type=str,
        help="Path to kaggle.json credentials file",
    )
    
    parser.add_argument(
        "--use-env",
        action="store_true",
        help="Use environment variables for Kaggle credentials",
    )
    
    return parser.parse_args()


def run_benchmark_on_position(
    engine: AsymmetricAdaptiveSearch,
    position: KaggleBenchmarkPosition,
    depth: int,
    time_limit_ms: float
) -> dict[str, Any]:
    """Run benchmark on a single position.
    
    Args:
        engine: Chess engine to use.
        position: Benchmark position.
        depth: Search depth.
        time_limit_ms: Time limit in milliseconds.
        
    Returns:
        Benchmark result dictionary.
    """
    if position.position is None:
        return {
            "position_id": position.position_id,
            "error": "Invalid position",
            "best_move": "",
            "evaluation": 0.0,
            "nodes_searched": 0,
            "time_ms": 0.0,
        }
    
    try:
        start_time = time.perf_counter()
        
        # Search for best move
        best_move, evaluation, stats = engine.search(
            position.position,
            depth=depth,
            time_limit_ms=time_limit_ms
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        result = {
            "position_id": position.position_id,
            "fen": position.fen,
            "description": position.description,
            "best_move": best_move.to_uci() if best_move else "",
            "evaluation": float(evaluation) if evaluation is not None else 0.0,
            "nodes_searched": stats.nodes_searched if stats else 0,
            "time_ms": elapsed_ms,
            "depth_reached": stats.depth_reached if stats else 0,
        }
        
        # Compare with expected move if available
        if position.expected_move and best_move:
            result["matches_expected"] = (best_move.to_uci() == position.expected_move)
        
        return result
    
    except Exception as e:
        return {
            "position_id": position.position_id,
            "error": str(e),
            "best_move": "",
            "evaluation": 0.0,
            "nodes_searched": 0,
            "time_ms": 0.0,
        }


def run_benchmark_suite(
    positions: list[KaggleBenchmarkPosition],
    depth: int = 15,
    time_limit_ms: float = 5000.0
) -> list[dict[str, Any]]:
    """Run benchmark suite on all positions.
    
    Args:
        positions: List of benchmark positions.
        depth: Search depth.
        time_limit_ms: Time limit per position.
        
    Returns:
        List of benchmark results.
    """
    # Initialize engine
    config = AASConfig(
        opening_width=2.0,
        middlegame_focus=1.5,
        endgame_precision=2.0,
    )
    engine = AsymmetricAdaptiveSearch(config=config)
    
    print(f"\nRunning benchmark on {len(positions)} positions...")
    print(f"Search depth: {depth}")
    print(f"Time limit: {time_limit_ms:.0f} ms per position")
    print("")
    
    results = []
    
    for i, position in enumerate(positions, 1):
        print(f"[{i}/{len(positions)}] Position {position.position_id}: ", end="", flush=True)
        
        result = run_benchmark_on_position(
            engine, position, depth, time_limit_ms
        )
        
        results.append(result)
        
        # Print result
        if "error" in result and result["error"]:
            print(f"ERROR - {result['error']}")
        else:
            move = result.get("best_move", "none")
            eval_score = result.get("evaluation", 0.0)
            nodes = result.get("nodes_searched", 0)
            time_taken = result.get("time_ms", 0.0)
            
            print(f"{move} (eval: {eval_score:+.2f}, nodes: {nodes}, time: {time_taken:.0f}ms)")
    
    return results


def print_benchmark_summary(results: list[dict[str, Any]]) -> None:
    """Print benchmark summary statistics.
    
    Args:
        results: List of benchmark results.
    """
    total = len(results)
    errors = sum(1 for r in results if "error" in r and r["error"])
    successful = total - errors
    
    print("\n" + "=" * 70)
    print("Benchmark Summary")
    print("=" * 70)
    print(f"Total positions: {total}")
    print(f"Successful: {successful}")
    print(f"Errors: {errors}")
    
    if successful > 0:
        avg_time = sum(r.get("time_ms", 0) for r in results) / successful
        avg_nodes = sum(r.get("nodes_searched", 0) for r in results) / successful
        avg_depth = sum(r.get("depth_reached", 0) for r in results) / successful
        
        print(f"\nAverage time per position: {avg_time:.2f} ms")
        print(f"Average nodes searched: {avg_nodes:.0f}")
        print(f"Average depth reached: {avg_depth:.1f}")
        
        # Calculate matches if expected moves available
        with_expected = [r for r in results if "matches_expected" in r]
        if with_expected:
            matches = sum(1 for r in with_expected if r["matches_expected"])
            match_rate = matches / len(with_expected) * 100
            print(f"\nExpected move match rate: {match_rate:.1f}% ({matches}/{len(with_expected)})")
    
    print("=" * 70 + "\n")


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    print_banner()
    
    # Load Kaggle configuration
    try:
        if args.submit or args.download:
            config = load_config(
                credentials_path=args.credentials,
                use_env=args.use_env
            )
            print("✓ Kaggle credentials loaded")
        else:
            config = None
            print("✓ Running in offline mode (no submission)")
    except Exception as e:
        print(f"✗ Failed to load Kaggle credentials: {e}")
        if args.submit or args.download:
            print("\nTo submit results, you need Kaggle API credentials:")
            print("1. Go to https://www.kaggle.com/settings")
            print("2. Click 'Create New API Token'")
            print("3. Save kaggle.json to ~/.kaggle/kaggle.json")
            return 1
        config = None
    
    # Load or download benchmark positions
    integration = KaggleIntegration(config)
    
    try:
        if args.use_sample:
            print("\n✓ Using sample benchmark positions")
            positions = integration.create_sample_positions()
        elif args.download and config:
            print(f"\n⬇ Downloading data from Kaggle competition: {args.competition}")
            leaderboard_data = integration.download_leaderboard_data(
                competition_id=args.competition,
                save_path="kaggle_leaderboard.json"
            )
            positions = leaderboard_data.positions
            
            if not positions:
                print("⚠ No positions found in leaderboard data, trying to download test data...")
                positions = integration.download_benchmark_positions(
                    competition_id=args.competition,
                    save_path="kaggle_test_positions.json"
                )
            
            if not positions:
                print("⚠ No positions found, using sample positions")
                positions = integration.create_sample_positions()
        elif args.input:
            print(f"\n✓ Loading benchmark data from: {args.input}")
            leaderboard_data = integration.load_leaderboard_from_file(args.input)
            positions = leaderboard_data.positions
        else:
            print("\n✓ Using sample benchmark positions (use --input or --download for real data)")
            positions = integration.create_sample_positions()
        
        print(f"✓ Loaded {len(positions)} benchmark positions")
    
    except Exception as e:
        print(f"✗ Failed to load benchmark positions: {e}")
        return 1
    
    # Run benchmarks
    results = run_benchmark_suite(
        positions,
        depth=args.depth,
        time_limit_ms=args.time_limit
    )
    
    # Print summary
    print_benchmark_summary(results)
    
    # Save results to file
    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "engine": "AsymmetricAdaptiveSearch",
            "depth": args.depth,
            "time_limit_ms": args.time_limit,
            "total_positions": len(positions),
        },
        "results": results,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Results saved to: {args.output}")
    
    # Submit to Kaggle if requested
    if args.submit and config:
        print("\n" + "=" * 70)
        print("Submitting to Kaggle Leaderboard")
        print("=" * 70)
        
        submission = KaggleSubmission(config)
        
        # Submit results
        result = submission.submit_to_kaggle(
            results,
            message=args.message,
            dry_run=args.dry_run
        )
        
        # Display result
        submission.display_submission_summary(result)
        
        # If successful and not dry run, wait for score
        if result.success and not args.dry_run and result.submission_id:
            print("⏳ Waiting for submission to be scored...")
            status = submission.get_submission_status(result.submission_id, timeout=300)
            submission.display_submission_summary(status)
        
        if not result.success:
            return 1
    
    elif args.submit:
        print("\n⚠ --submit requires Kaggle credentials (use --credentials or --use-env)")
    
    print("\n✓ Benchmark complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
