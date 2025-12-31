"""Kaggle Chess Leaderboard Integration.

Loads and parses Kaggle leaderboard data, extracts benchmark positions,
and converts them to QRATUM Position objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import logging
import requests

from qratum_chess.core.position import Position
from qratum_chess.benchmarks.kaggle_config import KaggleConfig


# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class KaggleBenchmarkPosition:
    """A single benchmark position from Kaggle leaderboard.
    
    Attributes:
        position_id: Unique identifier for the position.
        fen: FEN string representation.
        description: Description or category of the position.
        expected_move: Expected best move (if available).
        difficulty: Difficulty rating (if available).
        position: QRATUM Position object.
    """
    position_id: str
    fen: str
    description: str = ""
    expected_move: str | None = None
    difficulty: float | None = None
    position: Position | None = None
    
    def __post_init__(self):
        """Initialize Position object from FEN."""
        if self.position is None and self.fen:
            try:
                self.position = Position.from_fen(self.fen)
            except Exception as e:
                logger.warning(f"Failed to parse FEN for position {self.position_id}: {e}")
                self.position = None


@dataclass
class KaggleLeaderboardData:
    """Kaggle leaderboard data.
    
    Attributes:
        positions: List of benchmark positions.
        leaderboard_entries: List of leaderboard entries.
        metadata: Additional metadata from the leaderboard.
    """
    positions: list[KaggleBenchmarkPosition]
    leaderboard_entries: list[dict[str, Any]]
    metadata: dict[str, Any]
    
    def get_position_by_id(self, position_id: str) -> KaggleBenchmarkPosition | None:
        """Get a position by its ID.
        
        Args:
            position_id: Position identifier.
            
        Returns:
            KaggleBenchmarkPosition or None if not found.
        """
        for pos in self.positions:
            if pos.position_id == position_id:
                return pos
        return None
    
    def get_top_engines(self, n: int = 10) -> list[dict[str, Any]]:
        """Get top N engines from leaderboard.
        
        Args:
            n: Number of top engines to return.
            
        Returns:
            List of leaderboard entries.
        """
        return sorted(
            self.leaderboard_entries,
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:n]


class KaggleIntegration:
    """Integration with Kaggle Chess Leaderboard API.
    
    Handles data loading, parsing, and position extraction from Kaggle.
    """
    
    def __init__(self, config: KaggleConfig | None = None):
        """Initialize Kaggle integration.
        
        Args:
            config: Kaggle configuration. If None, uses default config.
        """
        self.config = config
    
    def load_leaderboard_from_file(self, filepath: str) -> KaggleLeaderboardData:
        """Load leaderboard data from a local JSON file.
        
        Args:
            filepath: Path to JSON file.
            
        Returns:
            KaggleLeaderboardData instance.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If JSON is invalid.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return self._parse_leaderboard_data(data)
    
    def download_leaderboard_data(
        self,
        competition_id: str | None = None,
        save_path: str | None = None
    ) -> KaggleLeaderboardData:
        """Download leaderboard data from Kaggle API.
        
        Args:
            competition_id: Kaggle competition ID. Uses config default if None.
            save_path: Optional path to save the downloaded data.
            
        Returns:
            KaggleLeaderboardData instance.
            
        Raises:
            requests.RequestException: If API request fails.
        """
        if self.config is None:
            raise ValueError("Config required for API access")
        
        if competition_id is None:
            competition_id = self.config.competition.competition_id
        
        # Download leaderboard data
        url = f"https://www.kaggle.com/api/v1/competitions/{competition_id}/leaderboard"
        headers = self.config.get_auth_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Save to file if requested
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        return self._parse_leaderboard_data(data)
    
    def download_benchmark_positions(
        self,
        competition_id: str | None = None,
        save_path: str | None = None
    ) -> list[KaggleBenchmarkPosition]:
        """Download benchmark positions from Kaggle competition.
        
        Args:
            competition_id: Kaggle competition ID.
            save_path: Optional path to save the downloaded data.
            
        Returns:
            List of KaggleBenchmarkPosition instances.
        """
        if self.config is None:
            raise ValueError("Config required for API access")
        
        if competition_id is None:
            competition_id = self.config.competition.competition_id
        
        # Try to download test data
        url = f"https://www.kaggle.com/api/v1/competitions/{competition_id}/data/list"
        headers = self.config.get_auth_headers()
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save to file if requested
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            # Parse positions from data
            return self._extract_positions_from_data(data)
        else:
            # If API call fails, log warning and return empty list
            logger.warning(f"Could not download benchmark positions: {response.status_code}")
            return []
    
    def _parse_leaderboard_data(self, data: dict[str, Any]) -> KaggleLeaderboardData:
        """Parse leaderboard data from JSON.
        
        Args:
            data: Raw JSON data from Kaggle API.
            
        Returns:
            KaggleLeaderboardData instance.
        """
        # Extract positions from data
        positions = self._extract_positions_from_data(data)
        
        # Extract leaderboard entries
        leaderboard_entries = []
        if "submissions" in data:
            leaderboard_entries = data["submissions"]
        elif "leaderboard" in data:
            leaderboard_entries = data["leaderboard"]
        
        # Extract metadata
        metadata = {
            "competition_id": data.get("competition_id", "unknown"),
            "total_positions": len(positions),
            "total_entries": len(leaderboard_entries),
            "last_updated": data.get("last_updated", None),
        }
        
        return KaggleLeaderboardData(
            positions=positions,
            leaderboard_entries=leaderboard_entries,
            metadata=metadata
        )
    
    def _extract_positions_from_data(
        self,
        data: dict[str, Any]
    ) -> list[KaggleBenchmarkPosition]:
        """Extract benchmark positions from Kaggle data.
        
        Args:
            data: Raw data from Kaggle API.
            
        Returns:
            List of KaggleBenchmarkPosition instances.
        """
        positions = []
        
        # Try different data structures
        position_data = None
        if "positions" in data:
            position_data = data["positions"]
        elif "test_positions" in data:
            position_data = data["test_positions"]
        elif "benchmark_positions" in data:
            position_data = data["benchmark_positions"]
        elif "data" in data and isinstance(data["data"], list):
            position_data = data["data"]
        
        if position_data is None:
            # Try to find FEN strings in any field
            position_data = self._find_fen_strings(data)
        
        if position_data:
            for i, pos_entry in enumerate(position_data):
                if isinstance(pos_entry, dict):
                    position = self._parse_position_entry(pos_entry, i)
                elif isinstance(pos_entry, str):
                    # Assume it's a FEN string
                    position = KaggleBenchmarkPosition(
                        position_id=f"pos_{i}",
                        fen=pos_entry
                    )
                else:
                    continue
                
                if position:
                    positions.append(position)
        
        return positions
    
    def _parse_position_entry(
        self,
        entry: dict[str, Any],
        index: int
    ) -> KaggleBenchmarkPosition | None:
        """Parse a single position entry.
        
        Args:
            entry: Position entry dictionary.
            index: Position index.
            
        Returns:
            KaggleBenchmarkPosition or None if parsing fails.
        """
        # Try to find FEN field
        fen = None
        for field in ["fen", "FEN", "position", "Position", "board"]:
            if field in entry:
                fen = entry[field]
                break
        
        if not fen:
            return None
        
        # Extract other fields
        position_id = entry.get("id", entry.get("position_id", f"pos_{index}"))
        description = entry.get("description", entry.get("category", ""))
        expected_move = entry.get("expected_move", entry.get("best_move", None))
        difficulty = entry.get("difficulty", entry.get("rating", None))
        
        return KaggleBenchmarkPosition(
            position_id=str(position_id),
            fen=fen,
            description=description,
            expected_move=expected_move,
            difficulty=difficulty
        )
    
    def _find_fen_strings(self, data: dict[str, Any]) -> list[str]:
        """Recursively find FEN strings in data.
        
        Args:
            data: Data dictionary to search.
            
        Returns:
            List of FEN strings found.
        """
        fen_strings = []
        
        def search_dict(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    if isinstance(value, str) and self._looks_like_fen(value):
                        fen_strings.append(value)
                    elif isinstance(value, (dict, list)):
                        search_dict(value)
            elif isinstance(d, list):
                for item in d:
                    search_dict(item)
        
        search_dict(data)
        return fen_strings
    
    def _looks_like_fen(self, s: str) -> bool:
        """Check if a string looks like a FEN string.
        
        Args:
            s: String to check.
            
        Returns:
            True if string looks like FEN.
        """
        if not isinstance(s, str):
            return False
        
        parts = s.split()
        
        # FEN should have 6 parts
        if len(parts) != 6:
            return False
        
        # First part should be board position with 7 slashes
        if parts[0].count('/') != 7:
            return False
        
        # Second part should be w or b
        if parts[1] not in ['w', 'b']:
            return False
        
        return True
    
    def create_sample_positions(self) -> list[KaggleBenchmarkPosition]:
        """Create sample benchmark positions for testing.
        
        Returns:
            List of sample KaggleBenchmarkPosition instances.
        """
        sample_fens = [
            ("start", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "Starting position"),
            ("sicilian", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", "Sicilian Defense"),
            ("endgame", "8/8/8/8/8/6k1/4K3/7R w - - 0 1", "Rook endgame"),
            ("tactics", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "Tactical position"),
            ("complex", "r1bq1rk1/pp2ppbp/2np1np1/8/2BNP3/2N1BP2/PPPQ2PP/R3K2R w KQ - 2 10", "Complex middlegame"),
        ]
        
        positions = []
        for pos_id, fen, desc in sample_fens:
            positions.append(KaggleBenchmarkPosition(
                position_id=pos_id,
                fen=fen,
                description=desc
            ))
        
        return positions
