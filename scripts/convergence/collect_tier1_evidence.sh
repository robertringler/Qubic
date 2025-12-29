#!/usr/bin/env bash
set -euo pipefail

# Collect evidence for all Tier-1 PRs
TIER1_PRS=(370 387 378 197 149)

# Step V-1
./scripts/convergence/capture_ground_truth.sh

# Step V-2 for each Tier-1 PR
for pr in "${TIER1_PRS[@]}"; do
    ./scripts/convergence/capture_pr_evidence.sh "$pr"
done

# Step V-3
./scripts/convergence/validate_evidence.sh

echo "=== Tier-1 evidence collection complete ==="
