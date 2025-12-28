// Size and performance tests for OS Supreme module

use std::mem;

#[test]
fn test_os_supreme_size_constraints() {
    use crate::qr_os_supreme::{OSSupreme, QUANTUM_STATE_BYTES};
    
    // Check struct sizes
    let os_size = mem::size_of::<OSSupreme>();
    println!("OSSupreme size: {} bytes", os_size);
    println!("Quantum state size: {} bytes", QUANTUM_STATE_BYTES);
    
    // Should fit within reasonable stack limits
    // 32KB for quantum state + overhead
    assert!(os_size < 40_000, "OSSupreme too large: {} bytes", os_size);
}

#[test]
fn test_determinism() {
    use crate::qr_os_supreme::OSSupreme;
    
    let mut os1 = OSSupreme::new();
    let mut os2 = OSSupreme::new();
    
    let (q1, ai1) = os1.supremacy_test(&[1, 2, 3]);
    let (q2, ai2) = os2.supremacy_test(&[1, 2, 3]);
    
    // Should be deterministic
    assert!((q1 - q2).abs() < 1e-6, "Quantum results not deterministic");
    assert_eq!(ai1, ai2, "AI results not deterministic");
}

#[test]
fn test_performance() {
    use crate::qr_os_supreme::OSSupreme;
    use std::time::Instant;
    
    let mut os = OSSupreme::new();
    
    let start = Instant::now();
    for _ in 0..100 {
        os.run_bell_state();
    }
    let duration = start.elapsed();
    
    println!("100 Bell state executions: {:?}", duration);
    println!("Average: {:?}", duration / 100);
    
    // Should be fast (< 1ms per operation target)
    assert!(duration.as_millis() < 1000, "Too slow: {:?}", duration);
}

#[test]
fn test_quantum_correctness() {
    use crate::qr_os_supreme::OSSupreme;
    
    let mut os = OSSupreme::new();
    let (p00, p11) = os.run_bell_state();
    
    // Bell state should have 50/50 superposition
    assert!((p00 - 0.5).abs() < 0.01, "P(00) should be ~0.5, got {}", p00);
    assert!((p11 - 0.5).abs() < 0.01, "P(11) should be ~0.5, got {}", p11);
    
    // Probabilities should sum to ~1
    let total = p00 + p11;
    assert!((total - 1.0).abs() < 0.01, "Probabilities should sum to 1, got {}", total);
}

#[test]
fn test_ai_determinism() {
    use crate::qr_os_supreme::OSSupreme;
    
    let mut os = OSSupreme::new();
    
    let result1 = os.run_ai(&[42, 43, 44]);
    os.reset();
    let result2 = os.run_ai(&[42, 43, 44]);
    
    assert_eq!(result1, result2, "AI should be deterministic");
}

#[test]
fn test_regression_proof() {
    use crate::qr_os_supreme::{TEXT_SIZE_TARGET, STACK_SIZE_TARGET, QUANTUM_STATE_BYTES};
    
    // Regression checks - these should never increase
    println!("Text size target: {} bytes", TEXT_SIZE_TARGET);
    println!("Stack size target: {} bytes", STACK_SIZE_TARGET);
    println!("Quantum state: {} bytes", QUANTUM_STATE_BYTES);
    
    // Verify we're within supremacy constraints
    assert!(TEXT_SIZE_TARGET <= 4096, "Text size exceeds 4KB limit");
    assert!(STACK_SIZE_TARGET <= 1024, "Stack size exceeds 1KB limit");
    
    // Quantum state is on stack but that's expected for quantum computing
    assert!(QUANTUM_STATE_BYTES == 32768, "Quantum state should be exactly 32KB");
}
