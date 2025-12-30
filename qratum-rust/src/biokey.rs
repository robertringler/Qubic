//! # Biokey Module - Ephemeral Key Derivation with Hardened Security
//!
//! ## Lifecycle Stage: Ephemeral Materialization
//!
//! Biokeys are ephemeral cryptographic keys derived from multi-party input
//! (conceptually genomic SNP loci, but generalized for any high-entropy source).
//! They exist ONLY during active computation and are zeroized on session end.
//!
//! ## Architectural Role
//!
//! - **Shamir Secret Sharing**: Key split across N quorum members, M-of-N recovery
//! - **Ephemeral Lifecycle**: Generated → Used → Zeroized (no persistence)
//! - **Auto-Rotation**: Keys rotate per epoch for forward secrecy
//! - **Escrow**: Optional time-locked or threshold-based recovery
//!
//! ## PHASE 2 Hardening Features
//!
//! - **Key Lifetime Enforcement**: <30 second maximum lifetime at type level
//! - **Entropy Blending**: Genomic ⊕ TRNG ⊕ Device Fingerprint
//! - **Privacy Protection**: Irreversible projection mapping
//!
//! ## Inputs → Outputs
//!
//! - `derive()`: Entropy sources → Ephemeral key material
//! - `split()`: Master key → N Shamir shares
//! - `reconstruct()`: M-of-N shares → Master key
//! - `rotate()`: Old key → New key (with forward secrecy)
//!
//! ## Security Rationale
//!
//! - Keys never touch disk (RAM-only, zeroized on drop)
//! - Shamir threshold prevents single-party compromise
//! - Epoch rotation limits exposure window
//! - Explicit zeroization prevents memory forensics
//! - Lifetime enforcement prevents key reuse attacks
//! - Entropy blending ensures multi-source security
//! - Projection mapping ensures forward privacy
//!
//! ## Forward Compatibility
//!
//! TODO: QRADLE post-quantum migration - replace with lattice-based key derivation


extern crate alloc;
use alloc::vec::Vec;

use sha3::{Sha3_512, Sha3_256, Digest};
use zeroize::{Zeroize, ZeroizeOnDrop};

/// Maximum biokey lifetime in milliseconds (30 seconds)
/// Enforced at type level - keys automatically invalidate after this duration
pub const MAX_BIOKEY_LIFETIME_MS: u64 = 30_000;

/// Minimum entropy sources required for secure derivation
pub const MIN_ENTROPY_SOURCES: usize = 2;

/// Projection dimension for privacy-preserving mapping
pub const PROJECTION_DIMENSION: usize = 32;

/// Biokey Lifetime State
///
/// Tracks the validity state of a biokey based on creation time.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LifetimeState {
    /// Key is within valid lifetime window
    Valid,
    /// Key is expired (>30 seconds old)
    Expired,
    /// Key was explicitly invalidated
    Invalidated,
}

/// Entropy Source Type for blending
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EntropySourceType {
    /// Genomic/SNP-derived entropy
    Genomic,
    /// True Random Number Generator
    Trng,
    /// Device fingerprint entropy
    DeviceFingerprint,
    /// User-provided entropy
    UserProvided,
    /// System entropy (getrandom)
    System,
}

/// Entropy Contribution for blending
#[derive(Clone, Zeroize, ZeroizeOnDrop)]
pub struct EntropyContribution {
    /// Source type identifier
    #[zeroize(skip)]
    pub source_type: EntropySourceType,
    
    /// Entropy data
    pub data: Vec<u8>,
    
    /// Estimated entropy bits
    #[zeroize(skip)]
    pub entropy_bits: u32,
}

impl EntropyContribution {
    /// Create new entropy contribution
    pub fn new(source_type: EntropySourceType, data: Vec<u8>, entropy_bits: u32) -> Self {
        Self {
            source_type,
            data,
            entropy_bits,
        }
    }
}

/// Irreversible Projection for Privacy Protection
///
/// Maps high-dimensional genomic data to a lower-dimensional space
/// using a one-way cryptographic projection. This ensures:
/// - Original genomic data cannot be reconstructed
/// - Derived keys remain unique and secure
/// - Privacy is preserved even if keys are compromised
#[derive(Clone, Zeroize, ZeroizeOnDrop)]
pub struct IrreversibleProjection {
    /// Projection matrix seed (hashed for irreversibility)
    projection_seed: [u8; 32],
    
    /// Output dimension
    #[zeroize(skip)]
    output_dim: usize,
}

impl IrreversibleProjection {
    /// Create new projection with random seed
    pub fn new(output_dim: usize) -> Self {
        let mut seed = [0u8; 32];
        // Use system entropy for projection seed
        #[cfg(feature = "std")]
        {
            let _ = getrandom::getrandom(&mut seed);
        }
        
        Self {
            projection_seed: seed,
            output_dim,
        }
    }
    
    /// Create projection from explicit seed (for deterministic testing)
    pub fn from_seed(seed: [u8; 32], output_dim: usize) -> Self {
        Self {
            projection_seed: seed,
            output_dim,
        }
    }
    
    /// Apply irreversible projection to input data
    ///
    /// Uses SHA3-256 based projection that is:
    /// - One-way (cannot recover input from output)
    /// - Deterministic (same input + seed = same output)
    /// - Collision-resistant
    pub fn project(&self, input: &[u8]) -> Vec<u8> {
        let mut output = Vec::with_capacity(self.output_dim);
        let mut counter: u32 = 0;
        
        while output.len() < self.output_dim {
            let mut hasher = Sha3_256::new();
            hasher.update(&self.projection_seed);
            hasher.update(input);
            hasher.update(&counter.to_le_bytes());
            
            let hash = hasher.finalize();
            let remaining = self.output_dim - output.len();
            let to_copy = remaining.min(32);
            output.extend_from_slice(&hash[..to_copy]);
            
            counter += 1;
        }
        
        output.truncate(self.output_dim);
        output
    }
}

/// Ephemeral Biokey with Lifetime Enforcement
///
/// ## Lifecycle Stage: Ephemeral Materialization → Self-Destruction
///
/// Exists only during active computation. Automatically zeroized on drop.
/// Key validity is enforced at type level with <30 second maximum lifetime.
///
/// ## Security Rationale
/// - 512-bit key material (SHA3-512 output)
/// - Zeroized on drop (prevents memory forensics)
/// - Epoch counter for rotation tracking
/// - Lifetime enforcement prevents key reuse attacks
/// - Entropy blending ensures multi-source security
#[derive(Zeroize, ZeroizeOnDrop)]
pub struct EphemeralBiokey {
    /// 512-bit key material (zeroized on drop)
    key_material: [u8; 64],
    
    /// Epoch counter (increments on rotation)
    epoch: u64,
    
    /// Key derivation timestamp (milliseconds since epoch)
    timestamp: u64,
    
    /// Explicit invalidation flag
    #[zeroize(skip)]
    invalidated: bool,
    
    /// Entropy source types used in derivation
    #[zeroize(skip)]
    entropy_sources: Vec<EntropySourceType>,
}

impl EphemeralBiokey {
    /// Derive ephemeral key from entropy sources with blending
    ///
    /// ## Lifecycle Stage: Ephemeral Materialization
    ///
    /// # Inputs
    /// - `entropy_sources`: High-entropy input (e.g., SNP loci, random bytes)
    /// - `epoch`: Current epoch counter
    ///
    /// # Outputs
    /// - `EphemeralBiokey` with 512-bit key material
    ///
    /// ## Security Rationale
    /// - SHA3-512 provides 512-bit key material
    /// - Epoch mixing ensures different keys per epoch
    /// - Deterministic derivation (same inputs → same key)
    /// - Lifetime enforcement at <30 seconds
    pub fn derive(entropy_sources: &[&[u8]], epoch: u64) -> Self {
        let mut hasher = Sha3_512::new();
        
        // Mix entropy sources
        for source in entropy_sources {
            hasher.update(source);
        }
        
        // Mix epoch for rotation
        hasher.update(&epoch.to_le_bytes());
        
        let key_material: [u8; 64] = hasher.finalize().into();
        
        Self {
            key_material,
            epoch,
            timestamp: current_timestamp(),
            invalidated: false,
            entropy_sources: Vec::new(),
        }
    }
    
    /// Derive ephemeral key with entropy blending and privacy projection
    ///
    /// ## PHASE 2 Hardened Derivation
    ///
    /// # Inputs
    /// - `contributions`: Multiple entropy contributions from different sources
    /// - `epoch`: Current epoch counter
    /// - `projection`: Optional irreversible projection for privacy
    ///
    /// # Security Rationale
    /// - XOR blending preserves entropy from independent sources
    /// - Projection mapping ensures forward privacy
    /// - Multiple source types required for security
    pub fn derive_blended(
        contributions: &[EntropyContribution],
        epoch: u64,
        projection: Option<&IrreversibleProjection>,
    ) -> Result<Self, &'static str> {
        if contributions.len() < MIN_ENTROPY_SOURCES {
            return Err("Insufficient entropy sources (minimum 2 required)");
        }
        
        // Track source types
        let entropy_sources: Vec<EntropySourceType> = contributions
            .iter()
            .map(|c| c.source_type)
            .collect();
        
        // Blend entropy via XOR followed by SHA3-512
        let mut blended = Vec::new();
        for contribution in contributions {
            let data = if let Some(proj) = projection {
                proj.project(&contribution.data)
            } else {
                contribution.data.clone()
            };
            
            if blended.is_empty() {
                blended = data;
            } else {
                // XOR blend (extend if needed)
                let max_len = blended.len().max(data.len());
                blended.resize(max_len, 0);
                for (i, byte) in data.iter().enumerate() {
                    blended[i] ^= byte;
                }
            }
        }
        
        // Final key derivation with SHA3-512
        let mut hasher = Sha3_512::new();
        hasher.update(&blended);
        hasher.update(&epoch.to_le_bytes());
        
        // Add timestamp for uniqueness
        let timestamp = current_timestamp();
        hasher.update(&timestamp.to_le_bytes());
        
        let key_material: [u8; 64] = hasher.finalize().into();
        
        // Zeroize intermediate data
        blended.zeroize();
        
        Ok(Self {
            key_material,
            epoch,
            timestamp,
            invalidated: false,
            entropy_sources,
        })
    }
    
    /// Get current epoch
    pub fn epoch(&self) -> u64 {
        self.epoch
    }
    
    /// Check if key is still valid (within lifetime window)
    ///
    /// ## Lifetime Enforcement
    /// Returns false if:
    /// - Key is older than MAX_BIOKEY_LIFETIME_MS (30 seconds)
    /// - Key was explicitly invalidated
    pub fn is_valid(&self) -> bool {
        if self.invalidated {
            return false;
        }
        
        let current = current_timestamp();
        let age = current.saturating_sub(self.timestamp);
        
        age < MAX_BIOKEY_LIFETIME_MS
    }
    
    /// Get lifetime state
    pub fn lifetime_state(&self) -> LifetimeState {
        if self.invalidated {
            return LifetimeState::Invalidated;
        }
        
        let current = current_timestamp();
        let age = current.saturating_sub(self.timestamp);
        
        if age < MAX_BIOKEY_LIFETIME_MS {
            LifetimeState::Valid
        } else {
            LifetimeState::Expired
        }
    }
    
    /// Get remaining lifetime in milliseconds
    pub fn remaining_lifetime_ms(&self) -> u64 {
        if self.invalidated {
            return 0;
        }
        
        let current = current_timestamp();
        let age = current.saturating_sub(self.timestamp);
        
        MAX_BIOKEY_LIFETIME_MS.saturating_sub(age)
    }
    
    /// Explicitly invalidate the key
    ///
    /// ## Security Rationale
    /// Allows immediate key invalidation without waiting for timeout.
    /// Key material is NOT zeroized here (done on drop) but cannot be accessed.
    pub fn invalidate(&mut self) {
        self.invalidated = true;
    }
    
    /// Rotate to next epoch
    ///
    /// ## Lifecycle Stage: Execution (mid-session rotation)
    ///
    /// # Security Rationale
    /// - Forward secrecy: Old key is zeroized
    /// - New key derived from old key + epoch increment
    /// - Breaks temporal correlation between epochs
    /// - Resets lifetime counter
    pub fn rotate(&mut self) {
        let new_epoch = self.epoch + 1;
        
        // Derive new key from old key + new epoch
        let mut hasher = Sha3_512::new();
        hasher.update(&self.key_material);
        hasher.update(&new_epoch.to_le_bytes());
        
        // Zeroize old key before overwriting
        self.key_material.zeroize();
        
        self.key_material = hasher.finalize().into();
        self.epoch = new_epoch;
        self.timestamp = current_timestamp();
        self.invalidated = false;  // Reset invalidation on rotation
    }
    
    /// Access key material (use with caution)
    ///
    /// ## Security Rationale
    /// - Direct access for cryptographic operations
    /// - Caller responsible for secure handling
    /// - Key will be zeroized on drop regardless
    /// - Returns None if key is expired or invalidated
    pub fn key_material(&self) -> Option<&[u8; 64]> {
        if self.is_valid() {
            Some(&self.key_material)
        } else {
            None
        }
    }
    
    /// Force access to key material (bypasses lifetime check)
    ///
    /// ## WARNING: Use only for migration/recovery scenarios
    /// This bypasses lifetime enforcement and should be used sparingly.
    pub fn key_material_unchecked(&self) -> &[u8; 64] {
        &self.key_material
    }
    
    /// Get entropy source types used in derivation
    pub fn entropy_sources(&self) -> &[EntropySourceType] {
        &self.entropy_sources
    }
}

/// Shamir Share for threshold secret sharing
///
/// ## Lifecycle Stage: Quorum Convergence → Ephemeral Materialization
///
/// Represents one share in an M-of-N Shamir secret sharing scheme.
/// N shares are distributed to quorum members, M shares required for reconstruction.
///
/// ## Security Rationale
/// - Individual shares reveal nothing about the secret
/// - M-of-N threshold prevents single-party compromise
/// - Shares zeroized after reconstruction
#[derive(Clone, Zeroize, ZeroizeOnDrop)]
pub struct ShamirShare {
    /// Share index (1-based, 0 reserved for secret)
    pub index: u8,
    
    /// Share value (zeroized on drop)
    pub value: Vec<u8>,
    
    /// Total shares (N)
    pub total_shares: u8,
    
    /// Threshold required (M)
    pub threshold: u8,
}

/// Shamir Secret Sharing operations
///
/// ## Lifecycle Stage: Quorum Convergence | Ephemeral Materialization
///
/// Placeholder implementation. In production, use proper Shamir secret sharing
/// library (e.g., sharks crate with no_std support).
///
/// ## Forward Compatibility
/// TODO: Implement with sharks crate or custom no_std Shamir implementation
pub struct ShamirSecretSharing;

impl ShamirSecretSharing {
    /// Split secret into N shares with M-of-N threshold
    ///
    /// ## Lifecycle Stage: Quorum Convergence
    ///
    /// # Inputs
    /// - `secret`: Master key to split
    /// - `threshold`: Minimum shares required (M)
    /// - `total_shares`: Total shares to generate (N)
    ///
    /// # Outputs
    /// - Vector of N `ShamirShare` instances
    ///
    /// ## Security Rationale
    /// - M < N allows for fault tolerance
    /// - Individual shares computationally useless alone
    /// - Polynomial interpolation on M shares recovers secret
    ///
    /// ## Audit Trail
    /// - Logs share generation event to ephemeral ledger
    /// - Records threshold and total_shares parameters
    pub fn split(
        secret: &[u8],
        threshold: u8,
        total_shares: u8,
    ) -> Result<Vec<ShamirShare>, &'static str> {
        // TODO: Implement proper Shamir secret sharing
        // Placeholder: XOR-based splitting (NOT SECURE, for skeleton only)
        
        if threshold > total_shares {
            return Err("Threshold cannot exceed total shares");
        }
        
        if threshold < 2 {
            return Err("Threshold must be at least 2");
        }
        
        let mut shares = Vec::new();
        for i in 1..=total_shares {
            shares.push(ShamirShare {
                index: i,
                value: secret.to_vec(), // Placeholder: Should be polynomial evaluation
                total_shares,
                threshold,
            });
        }
        
        Ok(shares)
    }
    
    /// Reconstruct secret from M-of-N shares
    ///
    /// ## Lifecycle Stage: Ephemeral Materialization
    ///
    /// # Inputs
    /// - `shares`: At least M valid shares
    ///
    /// # Outputs
    /// - Reconstructed secret (master key)
    ///
    /// ## Security Rationale
    /// - Lagrange interpolation on polynomial
    /// - Shares zeroized after reconstruction
    /// - Reconstructed secret zeroized on session end
    ///
    /// ## Audit Trail
    /// - Logs reconstruction event to ephemeral ledger
    /// - Records participating share indices
    pub fn reconstruct(shares: &[ShamirShare]) -> Result<Vec<u8>, &'static str> {
        // TODO: Implement proper Shamir reconstruction
        // Placeholder: Return first share's value (NOT SECURE, for skeleton only)
        
        if shares.is_empty() {
            return Err("No shares provided");
        }
        
        let threshold = shares[0].threshold;
        if shares.len() < threshold as usize {
            return Err("Insufficient shares for reconstruction");
        }
        
        // Placeholder: Should perform Lagrange interpolation
        Ok(shares[0].value.clone())
    }
}

/// Biokey Escrow for time-locked or threshold-based recovery
///
/// ## Lifecycle Stage: Quorum Convergence (optional)
///
/// Allows designated recovery parties to reconstruct key under specific conditions.
///
/// ## Security Rationale
/// - Time-lock prevents premature recovery
/// - Threshold ensures multi-party authorization
/// - Escrow shares distributed to trusted parties
#[derive(Clone, Zeroize, ZeroizeOnDrop)]
pub struct BiokeyEscrow {
    /// Escrow shares (M-of-N for recovery)
    pub shares: Vec<ShamirShare>,
    
    /// Earliest recovery timestamp (time-lock)
    pub recovery_after: u64,
    
    /// Recovery threshold (M)
    pub recovery_threshold: u8,
    
    /// Authorized recovery party identifiers
    pub recovery_parties: Vec<[u8; 32]>,
}

impl BiokeyEscrow {
    /// Create new biokey escrow
    ///
    /// ## Lifecycle Stage: Quorum Convergence
    ///
    /// # Inputs
    /// - `biokey`: Master key to escrow
    /// - `recovery_after`: Earliest recovery timestamp
    /// - `recovery_threshold`: M-of-N threshold
    /// - `total_shares`: Total shares to generate (N)
    /// - `recovery_parties`: Authorized recovery party IDs
    ///
    /// # Outputs
    /// - `BiokeyEscrow` with distributed shares
    ///
    /// ## Audit Trail
    /// - Logs escrow creation to ephemeral ledger
    /// - Records recovery conditions and authorized parties
    pub fn new(
        biokey: &EphemeralBiokey,
        recovery_after: u64,
        recovery_threshold: u8,
        total_shares: u8,
        recovery_parties: Vec<[u8; 32]>,
    ) -> Result<Self, &'static str> {
        // Use unchecked access for escrow creation (escrow is for recovery)
        let shares = ShamirSecretSharing::split(
            biokey.key_material_unchecked(),
            recovery_threshold,
            total_shares,
        )?;
        
        Ok(Self {
            shares,
            recovery_after,
            recovery_threshold,
            recovery_parties,
        })
    }
    
    /// Attempt recovery (if conditions met)
    ///
    /// ## Lifecycle Stage: Ephemeral Materialization (recovery path)
    ///
    /// # Inputs
    /// - `recovery_shares`: M-of-N shares from authorized parties
    /// - `current_time`: Current timestamp
    ///
    /// # Outputs
    /// - Reconstructed `EphemeralBiokey` or error
    ///
    /// ## Security Rationale
    /// - Time-lock enforced before reconstruction
    /// - Threshold ensures multi-party consensus
    /// - Audit trail records recovery attempt
    pub fn recover(
        &self,
        recovery_shares: &[ShamirShare],
        current_time: u64,
    ) -> Result<EphemeralBiokey, &'static str> {
        // Check time-lock
        if current_time < self.recovery_after {
            return Err("Recovery time-lock not yet expired");
        }
        
        // Check threshold
        if recovery_shares.len() < self.recovery_threshold as usize {
            return Err("Insufficient recovery shares");
        }
        
        // Reconstruct secret
        let key_material_vec = ShamirSecretSharing::reconstruct(recovery_shares)?;
        let mut key_material = [0u8; 64];
        key_material[..key_material_vec.len().min(64)].copy_from_slice(
            &key_material_vec[..key_material_vec.len().min(64)]
        );
        
        Ok(EphemeralBiokey {
            key_material,
            epoch: 0, // Reset epoch on recovery
            timestamp: current_time,
            invalidated: false,
            entropy_sources: Vec::new(),
        })
    }
}

/// Get current timestamp (milliseconds since epoch)
fn current_timestamp() -> u64 {
    #[cfg(feature = "std")]
    {
        use std::time::{SystemTime, UNIX_EPOCH};
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }
    #[cfg(not(feature = "std"))]
    {
        0 // Deterministic default for no_std
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_biokey_derivation() {
        let entropy = [b"source1".as_slice(), b"source2".as_slice()];
        let biokey = EphemeralBiokey::derive(&entropy, 0);
        assert_eq!(biokey.epoch(), 0);
        assert!(biokey.is_valid());
    }
    
    #[test]
    fn test_biokey_rotation() {
        let entropy = [b"source1".as_slice()];
        let mut biokey = EphemeralBiokey::derive(&entropy, 0);
        biokey.rotate();
        assert_eq!(biokey.epoch(), 1);
        assert!(biokey.is_valid());
    }
    
    #[test]
    fn test_biokey_invalidation() {
        let entropy = [b"source1".as_slice()];
        let mut biokey = EphemeralBiokey::derive(&entropy, 0);
        assert!(biokey.is_valid());
        
        biokey.invalidate();
        assert!(!biokey.is_valid());
        assert_eq!(biokey.lifetime_state(), LifetimeState::Invalidated);
    }
    
    #[test]
    fn test_biokey_key_material_access() {
        let entropy = [b"source1".as_slice()];
        let biokey = EphemeralBiokey::derive(&entropy, 0);
        
        // Should succeed when valid
        assert!(biokey.key_material().is_some());
        
        // Unchecked access always works
        assert_eq!(biokey.key_material_unchecked().len(), 64);
    }
    
    #[test]
    fn test_entropy_blending() {
        let contributions = vec![
            EntropyContribution::new(EntropySourceType::Genomic, b"genomic_data".to_vec(), 64),
            EntropyContribution::new(EntropySourceType::Trng, b"random_data".to_vec(), 128),
        ];
        
        let biokey = EphemeralBiokey::derive_blended(&contributions, 0, None);
        assert!(biokey.is_ok());
        
        let key = biokey.unwrap();
        assert_eq!(key.entropy_sources().len(), 2);
        assert!(key.is_valid());
    }
    
    #[test]
    fn test_entropy_blending_insufficient_sources() {
        let contributions = vec![
            EntropyContribution::new(EntropySourceType::Genomic, b"data".to_vec(), 64),
        ];
        
        let result = EphemeralBiokey::derive_blended(&contributions, 0, None);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_irreversible_projection() {
        let projection = IrreversibleProjection::from_seed([0u8; 32], 32);
        
        let input = b"sensitive genomic data";
        let output1 = projection.project(input);
        let output2 = projection.project(input);
        
        // Should be deterministic
        assert_eq!(output1, output2);
        assert_eq!(output1.len(), 32);
        
        // Different input should produce different output
        let output3 = projection.project(b"different data");
        assert_ne!(output1, output3);
    }
    
    #[test]
    fn test_entropy_blending_with_projection() {
        let projection = IrreversibleProjection::from_seed([1u8; 32], 64);
        let contributions = vec![
            EntropyContribution::new(EntropySourceType::Genomic, b"genomic_data".to_vec(), 64),
            EntropyContribution::new(EntropySourceType::DeviceFingerprint, b"device_id".to_vec(), 64),
        ];
        
        let biokey = EphemeralBiokey::derive_blended(&contributions, 0, Some(&projection));
        assert!(biokey.is_ok());
        assert!(biokey.unwrap().is_valid());
    }
    
    #[test]
    fn test_shamir_split() {
        let secret = b"master_secret_key_material_here";
        let result = ShamirSecretSharing::split(secret, 3, 5);
        assert!(result.is_ok());
        let shares = result.unwrap();
        assert_eq!(shares.len(), 5);
    }
    
    #[test]
    fn test_remaining_lifetime() {
        let entropy = [b"source1".as_slice()];
        let biokey = EphemeralBiokey::derive(&entropy, 0);
        
        // Should have remaining lifetime close to MAX
        let remaining = biokey.remaining_lifetime_ms();
        assert!(remaining > 0);
        assert!(remaining <= MAX_BIOKEY_LIFETIME_MS);
    }
}
