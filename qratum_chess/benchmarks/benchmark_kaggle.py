"""Kaggle Chess Benchmark Runner for QRATUM-Chess.

This module runs the QRATUM AsymmetricAdaptiveSearch engine against
Kaggle benchmark positions and analyzes the results.

Usage:
    benchmark = KaggleBenchmarkRunner()
    results = benchmark.run_benchmark(engine, leaderboard)
    benchmark.save_results(results, "benchmarks/kaggle_results/")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json
import time

from qratum_chess.benchmarks.kaggle_integration import (
    KaggleLeaderboard,
    KaggleBenchmarkPosition,
    KaggleLeaderboardLoader,
)
from qratum_chess.core.position import Position, Move


@dataclass
class KaggleBenchmarkResult:
    """Result from running QRATUM engine on a single position.
    
    Attributes:
        test_id: ID of the test position.
        fen: FEN string of the position.
        best_move: Best move found by QRATUM engine (UCI format).
        evaluation: Evaluation score from QRATUM engine.
        depth_reached: Search depth reached.
        nodes_searched: Number of nodes searched.
        time_ms: Time taken in milliseconds.
        expected_move: Expected best move from Kaggle data (if available).
        expected_eval: Expected evaluation from Kaggle data (if available).
        move_matches: Whether the move matches the expected move.
        eval_diff: Difference between QRATUM eval and expected eval.
        category: Position category.
        difficulty: Position difficulty.
    """
    test_id: str
    fen: str
    best_move: str
    evaluation: float
    depth_reached: int
    nodes_searched: int
    time_ms: float
    expected_move: str | None = None
    expected_eval: float | None = None
    move_matches: bool = False
    eval_diff: float | None = None
    category: str = "general"
    difficulty: str = "medium"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "test_id": self.test_id,
            "fen": self.fen,
            "best_move": self.best_move,
            "evaluation": self.evaluation,
            "depth_reached": self.depth_reached,
            "nodes_searched": self.nodes_searched,
            "time_ms": self.time_ms,
            "expected_move": self.expected_move,
            "expected_eval": self.expected_eval,
            "move_matches": self.move_matches,
            "eval_diff": self.eval_diff,
            "category": self.category,
            "difficulty": self.difficulty,
        }


@dataclass
class KaggleBenchmarkSummary:
    """Summary of Kaggle benchmark results.
    
    Attributes:
        total_positions: Total number of positions tested.
        move_accuracy: Percentage of moves matching expected moves.
        avg_eval_diff: Average evaluation difference.
        avg_depth: Average search depth.
        avg_nodes: Average nodes searched.
        avg_time_ms: Average time per position.
        total_time_ms: Total time for all positions.
        results_by_category: Results grouped by category.
        results_by_difficulty: Results grouped by difficulty.
        timestamp: Timestamp of the benchmark run.
    """
    total_positions: int = 0
    move_accuracy: float = 0.0
    avg_eval_diff: float = 0.0
    avg_depth: float = 0.0
    avg_nodes: float = 0.0
    avg_time_ms: float = 0.0
    total_time_ms: float = 0.0
    results_by_category: dict[str, dict[str, Any]] = field(default_factory=dict)
    results_by_difficulty: dict[str, dict[str, Any]] = field(default_factory=dict)
    timestamp: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "total_positions": self.total_positions,
            "move_accuracy": self.move_accuracy,
            "avg_eval_diff": self.avg_eval_diff,
            "avg_depth": self.avg_depth,
            "avg_nodes": self.avg_nodes,
            "avg_time_ms": self.avg_time_ms,
            "total_time_ms": self.total_time_ms,
            "results_by_category": self.results_by_category,
            "results_by_difficulty": self.results_by_difficulty,
            "timestamp": self.timestamp,
        }


class KaggleBenchmarkRunner:
    """Runs QRATUM engine against Kaggle benchmark positions.
    
    Orchestrates benchmark execution, result collection, and analysis.
    """
    
    def __init__(self):
        """Initialize the Kaggle benchmark runner."""
        self.loader = KaggleLeaderboardLoader()
        self.results: list[KaggleBenchmarkResult] = []
    
    def load_leaderboard(self, filepath: str | Path) -> KaggleLeaderboard:
        """Load Kaggle leaderboard data.
        
        Args:
            filepath: Path to the leaderboard JSON file.
            
        Returns:
            Loaded leaderboard data.
        """
        return self.loader.load_from_file(filepath)
    
    def run_benchmark(
        self,
        engine,
        leaderboard: KaggleLeaderboard,
        depth: int = 15,
        time_limit_ms: float | None = None,
        max_positions: int | None = None
    ) -> list[KaggleBenchmarkResult]:
        """Run benchmark on all positions.
        
        Args:
            engine: QRATUM engine instance (e.g., AsymmetricAdaptiveSearch).
            leaderboard: Kaggle leaderboard data.
            depth: Search depth for the engine.
            time_limit_ms: Optional time limit per position.
            max_positions: Optional limit on number of positions to test.
            
        Returns:
            List of benchmark results.
        """
        positions = leaderboard.test_positions
        
        if max_positions:
            positions = positions[:max_positions]
        
        self.results = []
        
        print(f"\n{'='*60}")
        print(f"Running QRATUM-Chess Kaggle Benchmark")
        print(f"{'='*60}")
        print(f"Positions to test: {len(positions)}")
        print(f"Search depth: {depth}")
        if time_limit_ms:
            print(f"Time limit: {time_limit_ms}ms per position")
        print(f"{'='*60}\n")
        
        for idx, benchmark_pos in enumerate(positions):
            print(f"Testing position {idx+1}/{len(positions)}: {benchmark_pos.test_id}")
            
            result = self._run_single_position(
                engine,
                benchmark_pos,
                depth,
                time_limit_ms
            )
            
            self.results.append(result)
            
            # Print immediate result
            status = "✓" if result.move_matches else "✗"
            print(f"  {status} Best move: {result.best_move} "
                  f"(eval: {result.evaluation:.2f}, "
                  f"nodes: {result.nodes_searched}, "
                  f"time: {result.time_ms:.0f}ms)")
        
        return self.results
    
    def _run_single_position(
        self,
        engine,
        benchmark_pos: KaggleBenchmarkPosition,
        depth: int,
        time_limit_ms: float | None
    ) -> KaggleBenchmarkResult:
        """Run engine on a single position.
        
        Args:
            engine: QRATUM engine instance.
            benchmark_pos: Benchmark position to test.
            depth: Search depth.
            time_limit_ms: Optional time limit.
            
        Returns:
            Benchmark result for this position.
        """
        position = benchmark_pos.position
        
        start_time = time.perf_counter()
        
        try:
            # Run engine search
            if time_limit_ms:
                best_move, eval_score, stats = engine.search(
                    position,
                    depth=depth,
                    time_limit_ms=time_limit_ms
                )
            else:
                best_move, eval_score, stats = engine.search(
                    position,
                    depth=depth
                )
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            # Extract stats
            best_move_uci = best_move.to_uci() if best_move else "none"
            depth_reached = stats.depth_reached if stats else depth
            nodes_searched = stats.nodes_searched if stats else 0
            
        except Exception as e:
            # Handle engine errors gracefully
            print(f"  Warning: Engine error on {benchmark_pos.test_id}: {e}")
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            best_move_uci = "error"
            eval_score = 0.0
            depth_reached = 0
            nodes_searched = 0
        
        # Compare with expected results
        move_matches = False
        eval_diff = None
        
        if benchmark_pos.expected_move:
            move_matches = (best_move_uci.lower() == benchmark_pos.expected_move.lower())
        
        if benchmark_pos.expected_eval is not None:
            eval_diff = abs(eval_score - benchmark_pos.expected_eval)
        
        return KaggleBenchmarkResult(
            test_id=benchmark_pos.test_id,
            fen=benchmark_pos.fen,
            best_move=best_move_uci,
            evaluation=eval_score,
            depth_reached=depth_reached,
            nodes_searched=nodes_searched,
            time_ms=elapsed_ms,
            expected_move=benchmark_pos.expected_move,
            expected_eval=benchmark_pos.expected_eval,
            move_matches=move_matches,
            eval_diff=eval_diff,
            category=benchmark_pos.category,
            difficulty=benchmark_pos.difficulty,
        )
    
    def generate_summary(
        self,
        results: list[KaggleBenchmarkResult] | None = None
    ) -> KaggleBenchmarkSummary:
        """Generate summary statistics from results.
        
        Args:
            results: List of results (uses self.results if None).
            
        Returns:
            Summary of benchmark results.
        """
        if results is None:
            results = self.results
        
        if not results:
            return KaggleBenchmarkSummary(timestamp=datetime.now().isoformat())
        
        total = len(results)
        
        # Calculate move accuracy (only for positions with expected moves)
        positions_with_expected = [r for r in results if r.expected_move]
        if positions_with_expected:
            matching_moves = sum(1 for r in positions_with_expected if r.move_matches)
            move_accuracy = matching_moves / len(positions_with_expected)
        else:
            move_accuracy = 0.0
        
        # Calculate average evaluation difference
        eval_diffs = [r.eval_diff for r in results if r.eval_diff is not None]
        avg_eval_diff = sum(eval_diffs) / len(eval_diffs) if eval_diffs else 0.0
        
        # Calculate averages
        avg_depth = sum(r.depth_reached for r in results) / total
        avg_nodes = sum(r.nodes_searched for r in results) / total
        avg_time_ms = sum(r.time_ms for r in results) / total
        total_time_ms = sum(r.time_ms for r in results)
        
        # Group by category
        results_by_category = self._group_by_field(results, "category")
        
        # Group by difficulty
        results_by_difficulty = self._group_by_field(results, "difficulty")
        
        return KaggleBenchmarkSummary(
            total_positions=total,
            move_accuracy=move_accuracy,
            avg_eval_diff=avg_eval_diff,
            avg_depth=avg_depth,
            avg_nodes=avg_nodes,
            avg_time_ms=avg_time_ms,
            total_time_ms=total_time_ms,
            results_by_category=results_by_category,
            results_by_difficulty=results_by_difficulty,
            timestamp=datetime.now().isoformat(),
        )
    
    def _group_by_field(
        self,
        results: list[KaggleBenchmarkResult],
        field: str
    ) -> dict[str, dict[str, Any]]:
        """Group results by a specific field.
        
        Args:
            results: List of results.
            field: Field name to group by.
            
        Returns:
            Dictionary of grouped statistics.
        """
        groups: dict[str, list[KaggleBenchmarkResult]] = {}
        
        for result in results:
            key = getattr(result, field)
            if key not in groups:
                groups[key] = []
            groups[key].append(result)
        
        grouped_stats = {}
        for key, group_results in groups.items():
            total = len(group_results)
            positions_with_expected = [r for r in group_results if r.expected_move]
            
            if positions_with_expected:
                matching = sum(1 for r in positions_with_expected if r.move_matches)
                accuracy = matching / len(positions_with_expected)
            else:
                accuracy = 0.0
            
            grouped_stats[key] = {
                "count": total,
                "move_accuracy": accuracy,
                "avg_time_ms": sum(r.time_ms for r in group_results) / total,
                "avg_nodes": sum(r.nodes_searched for r in group_results) / total,
            }
        
        return grouped_stats
    
    def save_results(
        self,
        output_dir: str | Path,
        results: list[KaggleBenchmarkResult] | None = None
    ) -> Path:
        """Save benchmark results to a directory.
        
        Args:
            output_dir: Output directory path.
            results: List of results (uses self.results if None).
            
        Returns:
            Path to the output directory.
        """
        if results is None:
            results = self.results
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate summary
        summary = self.generate_summary(results)
        
        # Save detailed results
        results_file = output_path / f"kaggle_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(
                {
                    "results": [r.to_dict() for r in results],
                    "summary": summary.to_dict()
                },
                f,
                indent=2
            )
        
        # Save summary only
        summary_file = output_path / f"kaggle_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
        print(f"  - Detailed results: {results_file.name}")
        print(f"  - Summary: {summary_file.name}")
        
        return output_path
    
    def print_summary(
        self,
        summary: KaggleBenchmarkSummary | None = None
    ) -> None:
        """Print benchmark summary to console.
        
        Args:
            summary: Summary to print (generates from self.results if None).
        """
        if summary is None:
            summary = self.generate_summary()
        
        print(f"\n{'='*60}")
        print("QRATUM-Chess Kaggle Benchmark Summary")
        print(f"{'='*60}")
        print(f"Total positions tested: {summary.total_positions}")
        print(f"Move accuracy: {summary.move_accuracy*100:.1f}%")
        
        if summary.avg_eval_diff > 0:
            print(f"Avg eval difference: {summary.avg_eval_diff:.2f}")
        
        print(f"Avg search depth: {summary.avg_depth:.1f}")
        print(f"Avg nodes searched: {summary.avg_nodes:.0f}")
        print(f"Avg time per position: {summary.avg_time_ms:.0f}ms")
        print(f"Total time: {summary.total_time_ms/1000:.1f}s")
        
        # Print category breakdown
        if summary.results_by_category:
            print(f"\nResults by Category:")
            for category, stats in summary.results_by_category.items():
                print(f"  {category}: {stats['count']} positions, "
                      f"{stats['move_accuracy']*100:.1f}% accuracy")
        
        # Print difficulty breakdown
        if summary.results_by_difficulty:
            print(f"\nResults by Difficulty:")
            for difficulty, stats in summary.results_by_difficulty.items():
                print(f"  {difficulty}: {stats['count']} positions, "
                      f"{stats['move_accuracy']*100:.1f}% accuracy")
        
        print(f"{'='*60}\n")
    
    def compare_with_leaderboard(
        self,
        leaderboard: KaggleLeaderboard,
        summary: KaggleBenchmarkSummary | None = None
    ) -> dict[str, Any]:
        """Compare QRATUM results with top leaderboard submissions.
        
        Args:
            leaderboard: Kaggle leaderboard data.
            summary: Summary to compare (generates from self.results if None).
            
        Returns:
            Comparison analysis.
        """
        if summary is None:
            summary = self.generate_summary()
        
        top_submissions = self.loader.get_top_submissions(n=5, leaderboard=leaderboard)
        
        comparison = {
            "qratum_score": summary.move_accuracy,
            "qratum_avg_time_ms": summary.avg_time_ms,
            "top_submissions": [
                {
                    "rank": sub.rank,
                    "team_name": sub.team_name,
                    "score": sub.score,
                }
                for sub in top_submissions
            ],
            "estimated_rank": self._estimate_rank(
                summary.move_accuracy,
                [sub.score for sub in leaderboard.submissions]
            ),
        }
        
        return comparison
    
    def _estimate_rank(self, qratum_score: float, all_scores: list[float]) -> int:
        """Estimate QRATUM's rank based on its score.
        
        Args:
            qratum_score: QRATUM's accuracy score.
            all_scores: All scores from the leaderboard.
            
        Returns:
            Estimated rank.
        """
        if not all_scores:
            return 1
        
        sorted_scores = sorted(all_scores, reverse=True)
        rank = 1
        
        for score in sorted_scores:
            if qratum_score >= score:
                break
            rank += 1
        
        return rank
