use crate::backend::{health, kernel, LogEntry, HealthResponse};
use crate::codegen::{CodeGenerator, ast::IntentSpec};
use crate::AppState;
use tauri::State;

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
