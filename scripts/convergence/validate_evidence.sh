#!/usr/bin/env bash
set -euo pipefail

# Step V-3: Evidence Artifact Validation
EVIDENCE_DIR="docs/convergence_evidence"

echo "=== Validating evidence artifacts ==="

# Validate JSON structure
for file in "$EVIDENCE_DIR"/pr_*_meta.json "$EVIDENCE_DIR"/pr_*_checks.json "$EVIDENCE_DIR"/open_pr_snapshot.json "$EVIDENCE_DIR"/open_issue_snapshot.json; do
    if [ -f "$file" ]; then
        jq empty "$file" 2>&1 || echo "INVALID JSON: $file"
    fi
done

# Validate SHAs
for file in "$EVIDENCE_DIR"/main_head_sha.txt "$EVIDENCE_DIR"/pr_*_head_sha.txt; do
    if [ -f "$file" ]; then
        if ! grep -Eq '^[0-9a-f]{40}$' "$file"; then
            echo "INVALID SHA: $file"
        fi
    fi
done

# Generate evidence manifest
cat > "$EVIDENCE_DIR/evidence_manifest.json" <<EOF
{
  "timestamp": "$(cat "$EVIDENCE_DIR/verification_timestamp.txt" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "main_head_sha": "$(cat "$EVIDENCE_DIR/main_head_sha.txt" 2>/dev/null || echo "MISSING")",
  "tier1_prs": {}
}
EOF

echo "Evidence validation complete. Manifest: $EVIDENCE_DIR/evidence_manifest.json"
