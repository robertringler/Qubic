use crate::backend::{health, kernel, LogEntry, HealthResponse};
use crate::codegen::{CodeGenerator, ast::IntentSpec};
use crate::qr_os_supreme::{
    OSSupreme, OSSupremeStats, QuantumStateVisualization,
    WasmPod, PodType, PodStatus, DCGEBenchmark, Phase4ModuleOutput
};
use crate::AppState;
use tauri::State;
use serde::{Serialize, Deserialize};

#[tauri::command]
pub async fn get_health() -> Result<HealthResponse, String> {
    Ok(health::get_health())
}

#[tauri::command]
pub async fn execute_kernel(request: kernel::KernelRequest) -> Result<kernel::KernelResponse, String> {
    kernel::execute_kernel(request).await
}

#[tauri::command]
pub fn get_logs(state: State<AppState>, limit: Option<usize>) -> Vec<LogEntry> {
    let logs = state.logs.lock().unwrap();
    let limit = limit.unwrap_or(100).min(logs.len());
    logs.iter().rev().take(limit).cloned().collect()
}

#[tauri::command]
pub async fn generate_code(intent: IntentSpec) -> Result<String, String> {
    let generator = CodeGenerator::new(intent.language.clone());
    let result = generator.generate(intent)?;
    
    if !result.validation.success {
        return Err(format!("Code generation failed: {:?}", result.validation.errors));
    }
    
    Ok(result.source)
}

#[tauri::command]
pub async fn validate_code(language: String, source: String) -> Result<bool, String> {
    use crate::codegen::validator::CompilerValidator;
    use crate::codegen::ast::AstNode;
    use crate::codegen::ir::TypedIR;
    
    let validator = CompilerValidator::new(language);
    let ast = AstNode::Block { statements: vec![] }; // Placeholder
    let ir = TypedIR::new();
    
    let result = validator.validate(&source, &ast, &ir);
    Ok(result.success)
}

// OS Supreme quantum + AI commands
#[derive(Serialize, Deserialize)]
pub struct QuantumResult {
    pub p00: f32,
    pub p11: f32,
}

#[tauri::command]
pub async fn run_bell_state() -> Result<QuantumResult, String> {
    let mut os = OSSupreme::new();
    let (p00, p11) = os.run_bell_state();
    Ok(QuantumResult { p00, p11 })
}

#[tauri::command]
pub async fn run_quantum_teleportation() -> Result<f32, String> {
    let mut os = OSSupreme::new();
    let entropy = os.run_teleportation();
    Ok(entropy)
}

#[tauri::command]
pub async fn run_ai_inference(input: Vec<u8>) -> Result<u8, String> {
    let mut os = OSSupreme::new();
    let result = os.run_ai(&input);
    Ok(result)
}

#[tauri::command]
pub async fn run_supremacy_test(input: Vec<u8>) -> Result<(f32, u8), String> {
    let mut os = OSSupreme::new();
    let (q_result, ai_result) = os.supremacy_test(&input);
    Ok((q_result, ai_result))
}

#[tauri::command]
pub async fn get_os_supreme_stats() -> Result<OSSupremeStats, String> {
    let os = OSSupreme::new();
    Ok(os.get_stats())
}

// =================================================================
// Phase 4 Commands: Advanced Quantum Gates
// =================================================================

/// Apply a quantum gate to the circuit
#[derive(Serialize, Deserialize)]
pub struct GateOperation {
    pub gate_type: String,  // "H", "X", "Y", "Z", "S", "T", "CNOT", "Toffoli"
    /// Qubit indices: single-qubit gates use qubits[0]; two-qubit gates (e.g. CNOT) use [control, target]; three-qubit gates (e.g. Toffoli) use [control1, control2, target].
    pub qubits: Vec<usize>,
}

/// Result of applying gates, includes visualization data
#[derive(Serialize, Deserialize)]
pub struct GateApplicationResult {
    pub success: bool,
    pub visualization: QuantumStateVisualization,
    pub message: String,
}

/// Helper function to apply a single gate to the quantum state
/// Returns true if gate was successfully applied
fn apply_gate_to_os(os: &mut OSSupreme, gate_op: &GateOperation) -> bool {
    match gate_op.gate_type.to_uppercase().as_str() {
        "H" | "HADAMARD" => {
            gate_op.qubits.first().map(|&q| os.apply_hadamard(q)).unwrap_or(false)
        }
        "X" | "PAULI_X" => {
            gate_op.qubits.first().map(|&q| os.apply_pauli_x(q)).unwrap_or(false)
        }
        "Y" | "PAULI_Y" => {
            gate_op.qubits.first().map(|&q| os.apply_pauli_y(q)).unwrap_or(false)
        }
        "Z" | "PAULI_Z" => {
            gate_op.qubits.first().map(|&q| os.apply_pauli_z(q)).unwrap_or(false)
        }
        "S" | "PHASE" => {
            gate_op.qubits.first().map(|&q| os.apply_phase_gate(q)).unwrap_or(false)
        }
        "T" => {
            gate_op.qubits.first().map(|&q| os.apply_t_gate(q)).unwrap_or(false)
        }
        "CNOT" | "CX" => {
            if gate_op.qubits.len() >= 2 {
                os.apply_cnot(gate_op.qubits[0], gate_op.qubits[1])
            } else {
                false
            }
        }
        "TOFFOLI" | "CCNOT" | "CCX" => {
            if gate_op.qubits.len() >= 3 {
                os.apply_toffoli(gate_op.qubits[0], gate_op.qubits[1], gate_op.qubits[2])
            } else {
                false
            }
        }
        _ => false,
    }
}

/// Apply a single quantum gate to a fresh quantum state.
///
/// WARNING: This command is **stateless across calls**. Each invocation creates a
/// new `OSSupreme` instance initialized in the `|0⟩` state, applies the requested
/// gate once, and then discards the instance. Calling this repeatedly will **not**
/// build up a circuit or preserve quantum state between calls.
///
/// Use this primarily for applying and visualizing individual gates. For any
/// stateful operation or a sequence of gates that should act on the *same*
/// quantum state, use `run_quantum_circuit` instead.
#[tauri::command]
pub async fn apply_quantum_gate(gate_op: GateOperation) -> Result<GateApplicationResult, String> {
    let mut os = OSSupreme::new();
    
    let success = apply_gate_to_os(&mut os, &gate_op);
    
    let visualization = os.get_quantum_state_visualization();
    let message = if success {
        format!("Applied {} gate successfully", gate_op.gate_type)
    } else {
        format!("Failed to apply {} gate", gate_op.gate_type)
    };
    
    Ok(GateApplicationResult {
        success,
        visualization,
        message,
    })
}

/// Run a quantum circuit (sequence of gates)
#[derive(Serialize, Deserialize)]
pub struct QuantumCircuit {
    pub gates: Vec<GateOperation>,
}

/// Execute a quantum circuit - sequence of gates applied to the same quantum state.
///
/// This function implements **rollback semantics**: if any gate fails to apply (e.g., 
/// invalid qubit index), execution stops immediately and returns the state before
/// the circuit was executed (fresh |0⟩ state). This ensures the returned visualization
/// is always consistent - either the complete circuit succeeded, or nothing was applied.
///
/// For partial execution or to identify which gate failed, consider validating gate
/// parameters individually using `apply_quantum_gate` before submitting a circuit.
#[tauri::command]
pub async fn run_quantum_circuit(circuit: QuantumCircuit) -> Result<GateApplicationResult, String> {
    // Create a fresh quantum state
    let mut os = OSSupreme::new();
    
    // Track which gate we're on for error reporting
    for (idx, gate_op) in circuit.gates.iter().enumerate() {
        if !apply_gate_to_os(&mut os, gate_op) {
            // Rollback: return a fresh state (equivalent to not executing anything)
            let fresh_os = OSSupreme::new();
            let visualization = fresh_os.get_quantum_state_visualization();
            return Ok(GateApplicationResult {
                success: false,
                visualization,
                message: format!(
                    "Circuit execution failed at gate {} ({}). Rolled back to initial |0⟩ state.",
                    idx + 1,
                    gate_op.gate_type
                ),
            });
        }
    }
    
    // All gates succeeded - return the final state
    let visualization = os.get_quantum_state_visualization();
    Ok(GateApplicationResult {
        success: true,
        visualization,
        message: format!("Circuit executed successfully ({} gates applied)", circuit.gates.len()),
    })
}

/// Get quantum state visualization
#[tauri::command]
pub async fn get_quantum_state() -> Result<QuantumStateVisualization, String> {
    let os = OSSupreme::new();
    Ok(os.get_quantum_state_visualization())
}

// =================================================================
// Phase 4 Commands: WASM Pod Isolation
// =================================================================

#[derive(Serialize, Deserialize)]
pub struct PodInfo {
    pub pod_id: u32,
    pub pod_type: String,
    pub status: String,
    pub memory_limit_kb: u32,
    pub exec_count: u32,
}

#[tauri::command]
pub async fn create_wasm_pod(pod_type: String, pod_id: u32, seed: u32) -> Result<PodInfo, String> {
    let pod = match pod_type.to_lowercase().as_str() {
        "os_supreme" | "ossupreme" => WasmPod::new_os_supreme(pod_id, seed),
        "mini_quasim" | "miniquasim" | "quasim" => WasmPod::new_mini_quasim(pod_id, seed),
        "minilm" | "mini_lm" => WasmPod::new_minilm(pod_id, seed),
        _ => return Err(format!("Unknown pod type: {}", pod_type)),
    };
    
    Ok(PodInfo {
        pod_id: pod.pod_id,
        pod_type: format!("{:?}", pod.pod_type),
        status: format!("{:?}", pod.status),
        memory_limit_kb: pod.memory_limit_kb,
        exec_count: pod.exec_count,
    })
}

// =================================================================
// Phase 4 Commands: Benchmark Metrics
// =================================================================

#[tauri::command]
pub async fn get_dcge_benchmark() -> Result<DCGEBenchmark, String> {
    Ok(DCGEBenchmark::default())
}

#[tauri::command]
pub async fn get_phase4_module_output() -> Result<Phase4ModuleOutput, String> {
    Ok(Phase4ModuleOutput::default())
}
