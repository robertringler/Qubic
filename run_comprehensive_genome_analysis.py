#!/usr/bin/env python3
"""Run comprehensive QRANTUM/QRADLES whole-genome sequencing analysis.

This script executes all 8 mandatory analytical phases for exhaustive genome analysis.
"""

import sys
from pathlib import Path

# Add xenon to path
sys.path.insert(0, str(Path(__file__).parent))

# Import comprehensive analyzer
from xenon.bioinformatics import comprehensive_genome_analysis

if __name__ == "__main__":
    comprehensive_genome_analysis.main()
