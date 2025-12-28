//! Fitness Evaluation Module
//!
//! Computes fitness scores for discovery candidates:
//! F = αI_novelty + βI_feasibility + γI_scalability + δI_strategic_leverage
//!
//! Default weights: α=0.30, β=0.25, γ=0.25, δ=0.20

extern crate alloc;

use alloc::string::String;
use alloc::vec::Vec;
use serde::{Deserialize, Serialize};

use super::lattice::MutatedNode;

/// Mutation bonus for breakthrough discoveries
const BREAKTHROUGH_BONUS: f64 = 0.15;

/// Mutation bonus for innovative discoveries
const INNOVATIVE_BONUS: f64 = 0.10;

/// Mutation bonus for standard mutations
const STANDARD_BONUS: f64 = 0.05;

/// Known architecture for novelty comparison
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnownArchitecture {
    pub name: String,
    pub features: Vec<String>,
    pub domain: String,
}

/// Market context for strategic leverage assessment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketContext {
    pub target_sectors: Vec<String>,
    pub competition_level: f64,
    pub growth_rate: f64,
    pub entry_barriers: f64,
}

impl Default for MarketContext {
    fn default() -> Self {
        MarketContext {
            target_sectors: Vec::new(),
            competition_level: 0.5,
            growth_rate: 0.15,
            entry_barriers: 0.6,
        }
    }
}

/// Fitness function weights
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FitnessWeights {
    /// Novelty weight
    pub alpha: f64,
    /// Feasibility weight
    pub beta: f64,
    /// Scalability weight
    pub gamma: f64,
    /// Strategic leverage weight
    pub delta: f64,
}

impl Default for FitnessWeights {
    fn default() -> Self {
        FitnessWeights {
            alpha: 0.30,
            beta: 0.25,
            gamma: 0.25,
            delta: 0.20,
        }
    }
}

impl FitnessWeights {
    /// Verify weights sum to 1.0
    pub fn is_valid(&self) -> bool {
        let sum = self.alpha + self.beta + self.gamma + self.delta;
        (sum - 1.0).abs() < 1e-6
    }

    /// Normalize weights to sum to 1.0
    pub fn normalize(&mut self) {
        let sum = self.alpha + self.beta + self.gamma + self.delta;
        if sum > 0.0 {
            self.alpha /= sum;
            self.beta /= sum;
            self.gamma /= sum;
            self.delta /= sum;
        }
    }
}

/// Compute novelty indicator - measures deviation from known architectures
///
/// Returns value in [0.0, 1.0] where higher means more novel
pub fn compute_novelty(node: &MutatedNode, known_architectures: &[KnownArchitecture]) -> f64 {
    // Simple hash-based novelty: check if mutation form appears in known architectures
    let mutation_lower = node.mutated_form.to_lowercase();
    
    let mut similarity_scores = Vec::new();
    
    for known in known_architectures {
        let known_lower = known.name.to_lowercase();
        
        // Simple substring matching for similarity
        let matches = mutation_lower.contains(&known_lower) || known_lower.contains(&mutation_lower);
        
        if matches {
            similarity_scores.push(0.3); // High similarity, low novelty
        } else {
            // Check feature overlap
            let mut feature_overlap = 0;
            for feature in &known.features {
                if mutation_lower.contains(&feature.to_lowercase()) {
                    feature_overlap += 1;
                }
            }
            
            let overlap_ratio = if known.features.is_empty() {
                0.0
            } else {
                feature_overlap as f64 / known.features.len() as f64
            };
            
            similarity_scores.push(1.0 - overlap_ratio);
        }
    }
    
    // If no known architectures, assume high novelty
    if similarity_scores.is_empty() {
        return 0.85;
    }
    
    // Average novelty across all known architectures
    let avg_novelty = similarity_scores.iter().sum::<f64>() / similarity_scores.len() as f64;
    
    // Boost novelty based on mutation type
    let mutation_bonus = if node.mutation_type.contains("breakthrough") {
        BREAKTHROUGH_BONUS
    } else if node.mutation_type.contains("innovative") {
        INNOVATIVE_BONUS
    } else {
        STANDARD_BONUS
    };
    
    (avg_novelty + mutation_bonus).min(1.0)
}

/// Compute feasibility indicator - engineering realizability score
///
/// Returns value in [0.0, 1.0] where higher means more feasible
pub fn compute_feasibility(node: &MutatedNode) -> f64 {
    let mutation_lower = node.mutated_form.to_lowercase();
    
    // Check for feasibility indicators
    let mut feasibility_score: f64 = 0.5; // Start at neutral
    
    // Positive indicators
    if mutation_lower.contains("deterministic") {
        feasibility_score += 0.1;
    }
    if mutation_lower.contains("scalable") || mutation_lower.contains("modular") {
        feasibility_score += 0.1;
    }
    if mutation_lower.contains("proven") || mutation_lower.contains("established") {
        feasibility_score += 0.15;
    }
    if mutation_lower.contains("practical") || mutation_lower.contains("implementable") {
        feasibility_score += 0.1;
    }
    
    // Negative indicators
    if mutation_lower.contains("theoretical") && !mutation_lower.contains("proven") {
        feasibility_score -= 0.1;
    }
    if mutation_lower.contains("speculative") {
        feasibility_score -= 0.2;
    }
    if mutation_lower.contains("exotic") || mutation_lower.contains("untested") {
        feasibility_score -= 0.15;
    }
    
    // Clamp to [0.0, 1.0]
    feasibility_score.max(0.0).min(1.0)
}

/// Compute scalability indicator - growth potential assessment
///
/// Returns value in [0.0, 1.0] where higher means more scalable
pub fn compute_scalability(node: &MutatedNode) -> f64 {
    let mutation_lower = node.mutated_form.to_lowercase();
    
    let mut scalability_score: f64 = 0.5;
    
    // Positive scalability indicators
    if mutation_lower.contains("distributed") || mutation_lower.contains("parallel") {
        scalability_score += 0.15;
    }
    if mutation_lower.contains("modular") || mutation_lower.contains("composable") {
        scalability_score += 0.12;
    }
    if mutation_lower.contains("cloud") || mutation_lower.contains("edge") {
        scalability_score += 0.1;
    }
    if mutation_lower.contains("efficient") || mutation_lower.contains("optimized") {
        scalability_score += 0.08;
    }
    
    // Negative scalability indicators
    if mutation_lower.contains("centralized") {
        scalability_score -= 0.1;
    }
    if mutation_lower.contains("monolithic") {
        scalability_score -= 0.15;
    }
    if mutation_lower.contains("bottleneck") {
        scalability_score -= 0.2;
    }
    
    // Dimensionality bonus (more dimensions = more integration = better scaling)
    let dim_bonus = (node.original.dimensionality as f64 * 0.05).min(0.15);
    scalability_score += dim_bonus;
    
    scalability_score.max(0.0).min(1.0)
}

/// Compute strategic leverage indicator - competitive advantage measure
///
/// Returns value in [0.0, 1.0] where higher means better strategic position
pub fn compute_strategic_leverage(node: &MutatedNode, market_context: &MarketContext) -> f64 {
    let mutation_lower = node.mutated_form.to_lowercase();
    
    let mut leverage_score: f64 = 0.4;
    
    // Strategic advantage indicators
    if mutation_lower.contains("moat") || mutation_lower.contains("barrier") {
        leverage_score += 0.15;
    }
    if mutation_lower.contains("proprietary") || mutation_lower.contains("unique") {
        leverage_score += 0.12;
    }
    if mutation_lower.contains("patent") || mutation_lower.contains("ip") {
        leverage_score += 0.1;
    }
    if mutation_lower.contains("network effect") {
        leverage_score += 0.18;
    }
    if mutation_lower.contains("first-mover") || mutation_lower.contains("pioneering") {
        leverage_score += 0.1;
    }
    
    // Market context adjustments
    leverage_score += (1.0 - market_context.competition_level) * 0.1;
    leverage_score += market_context.growth_rate * 0.2;
    leverage_score += market_context.entry_barriers * 0.15;
    
    leverage_score.max(0.0).min(1.0)
}

/// Combined fitness function
///
/// F = αI_novelty + βI_feasibility + γI_scalability + δI_strategic_leverage
pub fn compute_fitness(
    node: &MutatedNode,
    weights: &FitnessWeights,
    known_architectures: &[KnownArchitecture],
    market_context: &MarketContext,
) -> f64 {
    let novelty = compute_novelty(node, known_architectures);
    let feasibility = compute_feasibility(node);
    let scalability = compute_scalability(node);
    let leverage = compute_strategic_leverage(node, market_context);
    
    weights.alpha * novelty
        + weights.beta * feasibility
        + weights.gamma * scalability
        + weights.delta * leverage
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::discovery::lattice::{SymbolicRepresentation, CandidateNode, PhysicsNode, ComputationNode};

    fn create_test_node() -> MutatedNode {
        MutatedNode {
            original: SymbolicRepresentation {
                node: CandidateNode {
                    physics: Some(PhysicsNode::QuantumErrorSuppression),
                    computation: Some(ComputationNode::DeterministicASI),
                    materials: None,
                    systems: None,
                    economics: None,
                    interaction_id: "test".into(),
                },
                symbolic_form: "test".into(),
                dimensionality: 2,
            },
            mutation_type: "innovative".into(),
            mutated_form: "Novel deterministic quantum-AI hybrid system with distributed architecture".into(),
            novelty_score: 0.8,
        }
    }

    #[test]
    fn test_fitness_weights_default() {
        let weights = FitnessWeights::default();
        assert!(weights.is_valid());
        assert!((weights.alpha - 0.30).abs() < 1e-6);
    }

    #[test]
    fn test_fitness_weights_normalize() {
        let mut weights = FitnessWeights {
            alpha: 0.5,
            beta: 0.5,
            gamma: 0.5,
            delta: 0.5,
        };
        
        weights.normalize();
        assert!(weights.is_valid());
        assert!((weights.alpha - 0.25).abs() < 1e-6);
    }

    #[test]
    fn test_compute_novelty() {
        let node = create_test_node();
        let known = vec![
            KnownArchitecture {
                name: "Classical AI".into(),
                features: vec!["neural".into(), "gradient".into()],
                domain: "ML".into(),
            },
        ];
        
        let novelty = compute_novelty(&node, &known);
        assert!(novelty > 0.0 && novelty <= 1.0);
    }

    #[test]
    fn test_compute_feasibility() {
        let node = create_test_node();
        let feasibility = compute_feasibility(&node);
        
        assert!(feasibility > 0.5); // Should be high due to "deterministic"
        assert!(feasibility <= 1.0);
    }

    #[test]
    fn test_compute_scalability() {
        let node = create_test_node();
        let scalability = compute_scalability(&node);
        
        assert!(scalability > 0.5); // Should be high due to "distributed"
        assert!(scalability <= 1.0);
    }

    #[test]
    fn test_compute_strategic_leverage() {
        let node = create_test_node();
        let context = MarketContext::default();
        let leverage = compute_strategic_leverage(&node, &context);
        
        assert!(leverage >= 0.0 && leverage <= 1.0);
    }

    #[test]
    fn test_compute_fitness() {
        let node = create_test_node();
        let weights = FitnessWeights::default();
        let known = Vec::new();
        let context = MarketContext::default();
        
        let fitness = compute_fitness(&node, &weights, &known, &context);
        
        assert!(fitness >= 0.0 && fitness <= 1.0);
    }
}
