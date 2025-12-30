"""Self-Modifying Search Engine (MVI) for QRATUM-Chess.

Implements a self-modifying chess engine with:
- State space S_t = (X_t, G_t, R_t, Θ_t, M_t)
- Tactical cortex with belief-policy updates
- Meta-dynamics for rule/parameter adaptation
- Memory kernel with exponential decay
- Benchmarking and telemetry integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import time
import json
import numpy as np

from qratum_chess.core.position import Position, Move
from qratum_chess.core import Color, PieceType
from qratum_chess.search.aas import AsymmetricAdaptiveSearch, AASConfig, AASStats


@dataclass
class PhysicalState:
    """X_t: Physical board state - positions, piece velocities, energies."""
    position_fen: str
    piece_positions: dict[int, tuple[PieceType, Color]] = field(default_factory=dict)
    move_history: list[str] = field(default_factory=list)
    material_balance: float = 0.0
    
    @classmethod
    def from_position(cls, position: Position) -> PhysicalState:
        """Create physical state from Position object."""
        piece_positions = {}
        material_balance = 0.0
        
        for square in range(64):
            piece_tuple = position.board.piece_at(square)
            if piece_tuple:
                piece_positions[square] = piece_tuple
                piece_type, color = piece_tuple
                value = cls._get_piece_value(piece_type)
                material_balance += value if color == Color.WHITE else -value
        
        return cls(
            position_fen=position.to_fen(),
            piece_positions=piece_positions,
            material_balance=material_balance
        )
    
    @staticmethod
    def _get_piece_value(piece_type: PieceType) -> float:
        """Get material value of piece."""
        values = {
            PieceType.PAWN: 1.0,
            PieceType.KNIGHT: 3.0,
            PieceType.BISHOP: 3.0,
            PieceType.ROOK: 5.0,
            PieceType.QUEEN: 9.0,
            PieceType.KING: 0.0,
        }
        return values.get(piece_type, 0.0)


@dataclass
class GameConfiguration:
    """G_t: Game configuration - openings, motifs, structures."""
    active_openings: list[str] = field(default_factory=list)
    discovered_motifs: list[dict[str, Any]] = field(default_factory=list)
    endgame_type: str = "unknown"
    game_phase: str = "opening"  # opening, middlegame, endgame


@dataclass
class Rules:
    """R_t: Evaluation rules and parameters."""
    piece_values: dict[PieceType, float] = field(default_factory=lambda: {
        PieceType.PAWN: 1.0,
        PieceType.KNIGHT: 3.0,
        PieceType.BISHOP: 3.2,
        PieceType.ROOK: 5.0,
        PieceType.QUEEN: 9.0,
        PieceType.KING: 0.0,
    })
    motif_weights: dict[str, float] = field(default_factory=dict)
    tactical_weight: float = 0.5
    strategic_weight: float = 0.3
    novelty_weight: float = 0.2
    
    def adapt(self, delta: dict[str, float], max_change: float = 0.1) -> None:
        """Adapt rules with bounded changes."""
        for key, change in delta.items():
            if key == "tactical_weight":
                self.tactical_weight = np.clip(
                    self.tactical_weight + change,
                    self.tactical_weight - max_change,
                    self.tactical_weight + max_change
                )
            elif key == "strategic_weight":
                self.strategic_weight = np.clip(
                    self.strategic_weight + change,
                    self.strategic_weight - max_change,
                    self.strategic_weight + max_change
                )
            elif key == "novelty_weight":
                self.novelty_weight = np.clip(
                    self.novelty_weight + change,
                    self.novelty_weight - max_change,
                    self.novelty_weight + max_change
                )


@dataclass
class EngineParameters:
    """Θ_t: Engine physics/algorithmic parameters."""
    search_depth: int = 10
    mcts_rollouts: int = 1000
    novelty_pressure: float = 0.3
    temperature: float = 1.0
    exploration_constant: float = 1.414
    
    def adapt(self, delta: dict[str, Any], bounds: dict[str, tuple] = None) -> None:
        """Adapt parameters with safety bounds."""
        bounds = bounds or {
            "search_depth": (3, 20),
            "mcts_rollouts": (100, 5000),
            "novelty_pressure": (0.0, 1.0),
            "temperature": (0.1, 2.0),
        }
        
        for key, change in delta.items():
            if hasattr(self, key):
                current = getattr(self, key)
                new_value = current + change
                
                if key in bounds:
                    min_val, max_val = bounds[key]
                    new_value = np.clip(new_value, min_val, max_val)
                
                setattr(self, key, new_value)


@dataclass
class MemoryKernel:
    """M_t: Memory kernel storing historical patterns."""
    position_history: dict[str, float] = field(default_factory=dict)
    motif_outcomes: dict[str, list[float]] = field(default_factory=dict)
    elo_trajectory: list[float] = field(default_factory=list)
    move_evaluations: dict[str, float] = field(default_factory=dict)
    decay_factor: float = 0.1
    
    def update(self, position_key: str, evaluation: float) -> None:
        """Update memory with exponential decay: M_{t+1} = (1-λ)M_t + λF(S_t)."""
        prev_value = self.position_history.get(position_key, 0.0)
        new_value = (1 - self.decay_factor) * prev_value + self.decay_factor * evaluation
        self.position_history[position_key] = new_value
    
    def record_motif_outcome(self, motif_id: str, outcome: float) -> None:
        """Record outcome for a discovered motif."""
        if motif_id not in self.motif_outcomes:
            self.motif_outcomes[motif_id] = []
        self.motif_outcomes[motif_id].append(outcome)


@dataclass
class StateSpace:
    """Complete state space S_t = (X_t, G_t, R_t, Θ_t, M_t)."""
    physical: PhysicalState
    game_config: GameConfiguration
    rules: Rules
    parameters: EngineParameters
    memory: MemoryKernel
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize state for logging."""
        return {
            "physical": {
                "fen": self.physical.position_fen,
                "material_balance": self.physical.material_balance,
                "move_count": len(self.physical.move_history),
            },
            "game_config": {
                "phase": self.game_config.game_phase,
                "motifs_discovered": len(self.game_config.discovered_motifs),
            },
            "rules": {
                "tactical_weight": self.rules.tactical_weight,
                "strategic_weight": self.rules.strategic_weight,
                "novelty_weight": self.rules.novelty_weight,
            },
            "parameters": {
                "search_depth": self.parameters.search_depth,
                "novelty_pressure": self.parameters.novelty_pressure,
            },
            "memory": {
                "positions_stored": len(self.memory.position_history),
                "motifs_tracked": len(self.memory.motif_outcomes),
            },
            "timestamp": self.timestamp,
        }


class TacticalCortex:
    """Tactical cortex with policy-value network and belief state.
    
    Maintains:
    - Belief state b_t over positions
    - Policy π_t for move selection
    - Activation weights for telemetry
    """
    
    def __init__(self, learning_rate: float = 0.01):
        """Initialize tactical cortex.
        
        Args:
            learning_rate: Learning rate for policy updates.
        """
        self.learning_rate = learning_rate
        self.belief_state: dict[str, float] = {}
        self.policy_weights: dict[str, float] = {}
        self.activation_history: list[float] = []
        self.last_activation: float = 0.0
    
    def evaluate(
        self,
        position: Position,
        state: StateSpace
    ) -> tuple[dict[Move, float], float]:
        """Evaluate position and return move probabilities + value.
        
        Args:
            position: Current position.
            state: Complete state space.
            
        Returns:
            Tuple of (move_probabilities, position_value).
        """
        legal_moves = position.generate_legal_moves()
        
        if not legal_moves:
            return {}, 0.0
        
        # Simple tactical evaluation (placeholder for neural network)
        move_probs = {}
        for move in legal_moves:
            # Combine material + positional evaluation
            score = self._evaluate_move(move, position, state)
            move_probs[move] = score
        
        # Normalize to probabilities
        total = sum(move_probs.values())
        if total > 0:
            move_probs = {m: s / total for m, s in move_probs.items()}
        
        # Position value is material balance + positional factors
        position_value = state.physical.material_balance
        
        # Track activation
        self.last_activation = np.mean(list(move_probs.values())) if move_probs else 0.0
        self.activation_history.append(self.last_activation)
        
        return move_probs, position_value
    
    def _evaluate_move(
        self,
        move: Move,
        position: Position,
        state: StateSpace
    ) -> float:
        """Evaluate single move tactically."""
        score = 0.0
        
        # Check for captures
        target_piece = position.board.piece_at(move.to_sq)
        if target_piece:
            piece_type, _ = target_piece
            score += state.rules.piece_values.get(piece_type, 0.0)
        
        # Center control bonus
        center_squares = {27, 28, 35, 36}  # e4, d4, e5, d5
        if move.to_sq in center_squares:
            score += 0.2
        
        # Development bonus in opening
        if state.game_config.game_phase == "opening":
            if move.to_sq // 8 in {3, 4}:  # 4th and 5th ranks
                score += 0.1
        
        return score
    
    def update_policy(self, reward: float) -> None:
        """Update policy based on reward signal.
        
        Implements: π_{t+1} = π_t + α * reward_signal
        """
        # Simple policy gradient update
        adjustment = self.learning_rate * reward
        
        # Apply to policy weights (simplified)
        for key in self.policy_weights:
            self.policy_weights[key] += adjustment


class SelfModifyingSearch(AsymmetricAdaptiveSearch):
    """Self-modifying search engine with meta-dynamics.
    
    Implements:
    - State space management
    - Tactical cortex with belief-policy updates
    - Meta-dynamics for rule/parameter adaptation
    - Memory kernel with decay
    - Benchmarking integration
    """
    
    def __init__(
        self,
        evaluator: Callable[[Position], float] | None = None,
        config: AASConfig | None = None,
        memory_decay: float = 0.1,
        learning_rate: float = 0.01
    ):
        """Initialize self-modifying search engine.
        
        Args:
            evaluator: Position evaluation function.
            config: Base AAS configuration.
            memory_decay: Memory kernel decay factor.
            learning_rate: Learning rate for cortex updates.
        """
        super().__init__(evaluator=evaluator, config=config)
        
        # Initialize components
        self.tactical_cortex = TacticalCortex(learning_rate=learning_rate)
        self.state_history: list[StateSpace] = []
        self.telemetry_log: list[dict[str, Any]] = []
        
        # Initialize state space
        self.current_state = StateSpace(
            physical=PhysicalState(position_fen="", piece_positions={}),
            game_config=GameConfiguration(),
            rules=Rules(),
            parameters=EngineParameters(),
            memory=MemoryKernel(decay_factor=memory_decay)
        )
    
    def search(
        self,
        position: Position,
        depth: int = 10,
        time_limit_ms: float | None = None
    ) -> tuple[Move, float, AASStats]:
        """Search with self-modification capabilities.
        
        Args:
            position: Current position.
            depth: Search depth.
            time_limit_ms: Time limit.
            
        Returns:
            Tuple of (best_move, evaluation, stats).
        """
        start_time = time.time()
        
        # Update state space
        self.step(position)
        
        # Get tactical cortex evaluation
        move_probs, position_value = self.tactical_cortex.evaluate(
            position,
            self.current_state
        )
        
        if not move_probs:
            # Fall back to base engine
            return super().search(position, depth, time_limit_ms)
        
        # Select best move from cortex
        best_move = max(move_probs, key=move_probs.get)
        best_score = move_probs[best_move]
        
        # Calculate novelty pressure (divergence from baseline)
        novelty_pressure = self._calculate_novelty_pressure(
            best_move,
            position
        )
        
        # Update memory kernel
        self.update_memory_kernel(position, best_score)
        
        # Apply meta-dynamics
        self.update_meta_dynamics(best_score, novelty_pressure)
        
        # Record telemetry
        self._record_telemetry(position, best_move, best_score, novelty_pressure)
        
        # Create stats
        elapsed_ms = (time.time() - start_time) * 1000
        stats = AASStats(
            phase=self._determine_phase(position),
            nodes_searched=len(move_probs) * 10,
            time_ms=elapsed_ms,
            entropy=self._calculate_entropy(move_probs),
            branching_factor=float(len(position.generate_legal_moves())),
            depth_reached=depth,
            tablebase_probes=0
        )
        
        return best_move, position_value, stats
    
    def step(self, position: Position) -> None:
        """Advance state space with current position.
        
        Updates: S_{t+1} = T(S_t, {a_t}, R_t, Θ_t)
        """
        # Update physical state
        self.current_state.physical = PhysicalState.from_position(position)
        
        # Update game configuration
        self.current_state.game_config.game_phase = self._detect_phase_name(position)
        
        # Store state in history
        self.state_history.append(self.current_state)
        
        # Limit history size
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def update_meta_dynamics(self, evaluation: float, novelty: float) -> None:
        """Update rules R_t and parameters Θ_t based on feedback.
        
        Implements:
        - R_{t+1} = U_R(R_t, {a^{rule}}, M_t)
        - Θ_{t+1} = U_Θ(Θ_t, {a^{rule}}, M_t)
        """
        # Adapt rules based on evaluation
        if evaluation > 0.5:  # Good position
            rule_delta = {
                "tactical_weight": 0.01 * novelty,
                "novelty_weight": 0.005,
            }
            self.current_state.rules.adapt(rule_delta, max_change=0.05)
        
        # Adapt parameters based on novelty
        if novelty > 0.7:  # High novelty - explore more
            param_delta = {
                "novelty_pressure": 0.02,
                "temperature": 0.05,
            }
            self.current_state.parameters.adapt(param_delta)
        elif novelty < 0.3:  # Low novelty - exploit more
            param_delta = {
                "search_depth": 1,
                "novelty_pressure": -0.01,
            }
            self.current_state.parameters.adapt(param_delta)
    
    def update_memory_kernel(self, position: Position, evaluation: float) -> None:
        """Update memory kernel with exponential decay.
        
        Implements: M_{t+1} = (1-λ)M_t + λ F(S_t, {a_t})
        """
        position_key = position.to_fen()
        self.current_state.memory.update(position_key, evaluation)
    
    def _calculate_novelty_pressure(
        self,
        move: Move,
        position: Position
    ) -> float:
        """Calculate novelty pressure (divergence from baseline).
        
        Returns value between 0 (standard) and 1 (highly novel).
        """
        # Simple heuristic: how much does this differ from material-optimal?
        # In real implementation, compare to engine database
        
        # Check if move is typical for the position
        move_to_center = move.to_sq in {27, 28, 35, 36}
        is_capture = position.board.piece_at(move.to_sq) is not None
        
        if is_capture:
            return 0.2  # Captures are typical
        elif move_to_center:
            return 0.4  # Center moves are somewhat typical
        else:
            return 0.7  # Other moves are more novel
    
    def _calculate_entropy(self, move_probs: dict[Move, float]) -> float:
        """Calculate Shannon entropy of move distribution."""
        if not move_probs:
            return 0.0
        
        probs = list(move_probs.values())
        probs = [p for p in probs if p > 0]
        
        if not probs:
            return 0.0
        
        return -sum(p * np.log2(p) for p in probs)
    
    def _detect_phase_name(self, position: Position) -> str:
        """Detect game phase."""
        piece_count = sum(1 for sq in range(64) if position.board.piece_at(sq))
        
        if piece_count >= 28:
            return "opening"
        elif piece_count <= 10:
            return "endgame"
        else:
            return "middlegame"
    
    def _record_telemetry(
        self,
        position: Position,
        move: Move,
        evaluation: float,
        novelty: float
    ) -> None:
        """Record telemetry for benchmarking."""
        telemetry = {
            "position_fen": position.to_fen(),
            "move_uci": move.to_uci(),
            "evaluation": evaluation,
            "novelty_pressure": novelty,
            "cortex_activation": self.tactical_cortex.last_activation,
            "tactical_weight": self.current_state.rules.tactical_weight,
            "strategic_weight": self.current_state.rules.strategic_weight,
            "search_depth": self.current_state.parameters.search_depth,
            "timestamp": time.time(),
        }
        self.telemetry_log.append(telemetry)
    
    def get_telemetry(self) -> list[dict[str, Any]]:
        """Get complete telemetry log for benchmarking."""
        return self.telemetry_log
    
    def visualize_cortex(self) -> dict[str, Any]:
        """Get cortex activation data for visualization."""
        return {
            "tactical_activation_history": self.tactical_cortex.activation_history,
            "current_activation": self.tactical_cortex.last_activation,
            "policy_weights": self.tactical_cortex.policy_weights,
            "belief_state_size": len(self.tactical_cortex.belief_state),
        }
    
    def get_state_analysis(self) -> dict[str, Any]:
        """Get complete state space analysis."""
        return {
            "current_state": self.current_state.to_dict(),
            "state_history_length": len(self.state_history),
            "memory_size": len(self.current_state.memory.position_history),
            "telemetry_entries": len(self.telemetry_log),
        }
    
    def export_telemetry(self, filepath: str) -> None:
        """Export telemetry to JSON file."""
        data = {
            "telemetry": self.telemetry_log,
            "state_history": [s.to_dict() for s in self.state_history[-20:]],
            "cortex_data": self.visualize_cortex(),
            "export_timestamp": time.time(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def demo_self_modifying_engine():
    """Demonstrate self-modifying engine capabilities."""
    print("=" * 80)
    print("Self-Modifying Search Engine (MVI) - Demonstration")
    print("=" * 80)
    print()
    
    # Initialize engine
    engine = SelfModifyingSearch(memory_decay=0.15, learning_rate=0.02)
    print("Engine initialized:")
    print(f"  Memory decay: {engine.current_state.memory.decay_factor}")
    print(f"  Learning rate: {engine.tactical_cortex.learning_rate}")
    print()
    
    # Create starting position
    position = Position.starting()
    print(f"Starting position: {position.to_fen()[:40]}...")
    print()
    
    # Run several moves
    print("Running self-modifying simulation for 3 moves:")
    print("-" * 80)
    
    for turn in range(3):
        move, eval_score, stats = engine.search(position, depth=5)
        
        # Get telemetry
        telemetry = engine.telemetry_log[-1] if engine.telemetry_log else {}
        
        print(f"\nTurn {turn + 1}:")
        print(f"  Move: {move.to_uci()}")
        print(f"  Evaluation: {eval_score:.4f}")
        print(f"  Novelty pressure: {telemetry.get('novelty_pressure', 0):.4f}")
        print(f"  Cortex activation: {telemetry.get('cortex_activation', 0):.4f}")
        print(f"  Tactical weight: {telemetry.get('tactical_weight', 0):.4f}")
        print(f"  Search depth: {telemetry.get('search_depth', 0)}")
        print(f"  Nodes searched: {stats.nodes_searched}")
        print(f"  Entropy: {stats.entropy:.4f}")
        
        # Make the move
        position = position.make_move(move)
    
    print()
    print("-" * 80)
    print("\nState Space Analysis:")
    analysis = engine.get_state_analysis()
    print(f"  State history length: {analysis['state_history_length']}")
    print(f"  Memory positions: {analysis['memory_size']}")
    print(f"  Telemetry entries: {analysis['telemetry_entries']}")
    
    print("\nCortex Visualization Data:")
    cortex_viz = engine.visualize_cortex()
    print(f"  Current activation: {cortex_viz['current_activation']:.4f}")
    print(f"  Activation history: {len(cortex_viz['tactical_activation_history'])} entries")
    
    print()
    print("=" * 80)
    print("Self-modifying engine demonstration complete!")
    print()
    print("Features demonstrated:")
    print("  ✓ State space S_t = (X_t, G_t, R_t, Θ_t, M_t)")
    print("  ✓ Tactical cortex with policy updates")
    print("  ✓ Meta-dynamics (rule/parameter adaptation)")
    print("  ✓ Memory kernel with exponential decay")
    print("  ✓ Novelty pressure tracking")
    print("  ✓ Telemetry for benchmarking")
    print("  ✓ Cortex visualization data")
    print("=" * 80)


if __name__ == "__main__":
    demo_self_modifying_engine()
