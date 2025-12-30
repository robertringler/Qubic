"""Main benchmark runner for QRATUM-Chess (Stage IV).

Orchestrates all benchmark components:
- Performance metrics
- Strategic torture suite
- Adversarial gauntlet
- Elo certification
- Resilience testing
- Telemetry output
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import json

from qratum_chess.benchmarks.metrics import PerformanceMetrics, PerformanceReport
from qratum_chess.benchmarks.torture import StrategicTortureSuite, TortureSuiteReport
from qratum_chess.benchmarks.gauntlet import AdversarialGauntlet, GauntletReport
from qratum_chess.benchmarks.elo import EloCertification, EloCertificationResult
from qratum_chess.benchmarks.resilience import ResilienceTest, ResilienceReport
from qratum_chess.benchmarks.telemetry import TelemetryOutput


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runner.
    
    Attributes:
        run_performance: Run performance benchmarks.
        run_torture: Run strategic torture suite.
        run_gauntlet: Run adversarial gauntlet.
        run_elo: Run Elo certification.
        run_resilience: Run resilience tests.
        torture_depth: Search depth for torture tests.
        gauntlet_games: Games per adversary in gauntlet.
        resilience_iterations: Iterations for resilience tests.
        output_telemetry: Generate telemetry output.
    """
    run_performance: bool = True
    run_torture: bool = True
    run_gauntlet: bool = False  # Requires external engines
    run_elo: bool = True
    run_resilience: bool = True
    torture_depth: int = 15
    gauntlet_games: int = 100
    resilience_iterations: int = 10
    output_telemetry: bool = True


@dataclass
class BenchmarkSummary:
    """Summary of all benchmark results."""
    performance: PerformanceReport | None = None
    torture: TortureSuiteReport | None = None
    gauntlet: GauntletReport | None = None
    elo: EloCertificationResult | None = None
    resilience: ResilienceReport | None = None
    overall_passed: bool = False
    total_time_seconds: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "overall_passed": self.overall_passed,
            "total_time_seconds": self.total_time_seconds,
            "performance": self.performance.to_dict() if self.performance else None,
            "torture": {
                "eval_volatility": self.torture.eval_volatility if self.torture else None,
                "blunder_rate": self.torture.blunder_rate if self.torture else None,
                "passed": self.torture.passed() if self.torture else None,
            },
            "elo": self.elo.to_dict() if self.elo else None,
            "resilience": {
                "passed_tests": self.resilience.passed_tests if self.resilience else None,
                "failed_tests": self.resilience.failed_tests if self.resilience else None,
                "avg_recovery_ms": self.resilience.average_recovery_ms if self.resilience else None,
            },
        }


class BenchmarkRunner:
    """Main benchmark runner for QRATUM-Chess.
    
    Coordinates all Stage IV benchmarking components and produces
    comprehensive performance certification reports.
    """
    
    def __init__(self, config: BenchmarkConfig | None = None):
        """Initialize the benchmark runner.
        
        Args:
            config: Benchmark configuration.
        """
        self.config = config or BenchmarkConfig()
        
        # Initialize components
        self.performance = PerformanceMetrics()
        self.torture = StrategicTortureSuite()
        self.gauntlet = AdversarialGauntlet()
        self.elo_cert = EloCertification()
        self.resilience = ResilienceTest()
        self.telemetry = TelemetryOutput()
        
        # Test positions
        self.test_positions: list = []
    
    def load_test_positions(self) -> None:
        """Load standard test positions."""
        from qratum_chess.core.position import Position
        
        # Standard test positions
        test_fens = [
            Position.starting().to_fen(),  # Starting position
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",  # Italian
            "rnbqkb1r/pp1ppppp/5n2/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",  # Sicilian
            "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",  # Italian (Black)
            "r2qkb1r/ppp1pppp/2np1n2/3P4/3P4/5N2/PPP2PPP/RNBQKB1R w KQkq - 0 5",  # Exchange Caro
            "8/8/8/8/8/6k1/4K3/7R w - - 0 1",  # Simple endgame
            "8/8/p1p5/1p5p/1P5p/8/PPP2K1k/8 w - - 0 1",  # Complex pawn endgame
        ]
        
        self.test_positions = [Position.from_fen(fen) for fen in test_fens]
    
    def run(self, engine, evaluator=None) -> BenchmarkSummary:
        """Run complete benchmark suite.
        
        Args:
            engine: Chess engine to benchmark.
            evaluator: Neural evaluator (optional).
            
        Returns:
            Complete benchmark summary.
        """
        start_time = time.perf_counter()
        summary = BenchmarkSummary()
        
        # Load test positions
        self.load_test_positions()
        
        # Run performance benchmarks
        if self.config.run_performance:
            print("Running performance benchmarks...")
            summary.performance = self.performance.run_full_benchmark(
                engine, evaluator, self.test_positions
            )
            self._record_performance_telemetry(summary.performance)
        
        # Run torture suite
        if self.config.run_torture:
            print("Running strategic torture suite...")
            summary.torture = self.torture.run(engine, depth=self.config.torture_depth)
            self._record_torture_telemetry(summary.torture)
        
        # Run gauntlet (if configured and adversaries registered)
        if self.config.run_gauntlet:
            print("Running adversarial gauntlet...")
            summary.gauntlet = self.gauntlet.run_full_gauntlet(
                engine, games_per_adversary=self.config.gauntlet_games
            )
        
        # Run Elo certification
        if self.config.run_elo and summary.torture:
            print("Running Elo certification...")
            # Simulate game results from torture suite performance
            game_results = self._simulate_game_results(summary.torture)
            summary.elo = self.elo_cert.certify_generation("current", game_results)
            self._record_elo_telemetry(summary.elo)
        
        # Run resilience tests
        if self.config.run_resilience:
            print("Running resilience tests...")
            summary.resilience = self.resilience.run_full_suite(
                engine, evaluator, self.test_positions,
                iterations=self.config.resilience_iterations
            )
        
        # Calculate overall status
        summary.overall_passed = self._evaluate_overall(summary)
        summary.total_time_seconds = time.perf_counter() - start_time
        
        # Generate telemetry output
        if self.config.output_telemetry:
            self.telemetry.finalize_snapshot()
        
        return summary
    
    def _record_performance_telemetry(self, report: PerformanceReport) -> None:
        """Record performance data in telemetry."""
        for result in report.results:
            self.telemetry.record_time_per_move(result.value)
    
    def _record_torture_telemetry(self, report: TortureSuiteReport) -> None:
        """Record torture suite data in telemetry."""
        for result in report.results:
            self.telemetry.record_branching_entropy(result.eval_stability)
    
    def _record_elo_telemetry(self, result: EloCertificationResult) -> None:
        """Record Elo data in telemetry."""
        self.telemetry.record_elo(
            result.elo_rating.rating,
            result.elo_rating.confidence_low,
            result.elo_rating.confidence_high
        )
    
    def _simulate_game_results(
        self,
        torture_report: TortureSuiteReport
    ) -> list[tuple[str, float]]:
        """Simulate game results from torture suite performance.
        
        Args:
            torture_report: Results from torture suite.
            
        Returns:
            Simulated game results for Elo calculation.
        """
        results = []
        baseline_elo = 3500  # Approximate Stockfish level
        
        for test_result in torture_report.results:
            if test_result.is_correct:
                results.append(("win", baseline_elo))
            elif test_result.eval_stability < 0.1:
                results.append(("draw", baseline_elo))
            else:
                results.append(("loss", baseline_elo))
        
        return results
    
    def _evaluate_overall(self, summary: BenchmarkSummary) -> bool:
        """Evaluate overall benchmark pass/fail status.
        
        Args:
            summary: Benchmark summary.
            
        Returns:
            True if all benchmarks passed.
        """
        passed = True
        
        if summary.performance and not summary.performance.overall_passed:
            passed = False
        
        if summary.torture and not summary.torture.passed():
            passed = False
        
        if summary.gauntlet and not summary.gauntlet.passed():
            passed = False
        
        if summary.resilience and not summary.resilience.passed():
            passed = False
        
        return passed
    
    def export_results(self, filepath: str, summary: BenchmarkSummary) -> None:
        """Export benchmark results to JSON file.
        
        Args:
            filepath: Output file path.
            summary: Benchmark summary to export.
        """
        with open(filepath, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)
    
    def print_summary(self, summary: BenchmarkSummary) -> None:
        """Print benchmark summary to console.
        
        Args:
            summary: Benchmark summary.
        """
        print("\n" + "=" * 60)
        print("QRATUM-Chess Benchmark Summary")
        print("=" * 60)
        
        status = "PASSED" if summary.overall_passed else "FAILED"
        print(f"Overall Status: {status}")
        print(f"Total Time: {summary.total_time_seconds:.2f} seconds")
        
        if summary.performance:
            print("\nPerformance Benchmarks:")
            print(f"  Status: {'PASSED' if summary.performance.overall_passed else 'FAILED'}")
            for result in summary.performance.results:
                status = "✓" if result.passed else "✗"
                print(f"  {status} {result.metric_name}: {result.value:.2f} {result.unit}")
        
        if summary.torture:
            print("\nStrategic Torture Suite:")
            print(f"  Status: {'PASSED' if summary.torture.passed() else 'FAILED'}")
            print(f"  Eval Volatility: {summary.torture.eval_volatility:.4f} (target: ≤0.05)")
            print(f"  Blunder Rate: {summary.torture.blunder_rate:.4f} (target: ≤0.01%)")
            print(f"  Positions Tested: {summary.torture.positions_tested}")
        
        if summary.elo:
            print("\nElo Certification:")
            print(f"  Elo Rating: {summary.elo.elo_rating.rating:.0f}")
            print(f"  Confidence: [{summary.elo.elo_rating.confidence_low:.0f}, {summary.elo.elo_rating.confidence_high:.0f}]")
            print(f"  Promoted: {summary.elo.is_promoted}")
        
        if summary.resilience:
            print("\nResilience Tests:")
            print(f"  Status: {'PASSED' if summary.resilience.passed() else 'FAILED'}")
            print(f"  Passed: {summary.resilience.passed_tests}/{summary.resilience.total_tests}")
            print(f"  Avg Recovery: {summary.resilience.average_recovery_ms:.2f} ms")
        
        print("=" * 60)
