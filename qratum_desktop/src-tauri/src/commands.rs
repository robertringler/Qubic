use crate::backend::{health, kernel, LogEntry, HealthResponse};
use crate::codegen::{CodeGenerator, ast::IntentSpec};
use crate::qr_os_supreme::{OSSupreme, OSSupremeStats};
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
