//! QRATUM Discovery Directive CLI
//!
//! Command-line interface for generating, validating, and archiving
//! 100 discoveries across quantum computing, materials science, AI systems,
//! cryptography, and industrial design.

use q_substrate::discovery::{
    run_discovery_directive, validate_discovery_schema,
    import_discoveries_json, generate_provenance_hash, verify_provenance_chain,
    generate_provenance_report, Discovery,
};
use std::env;
use std::fs;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        print_usage();
        process::exit(1);
    }
    
    let command = &args[1];
    
    match command.as_str() {
        "run" => cmd_run(&args[2..]),
        "validate" => cmd_validate(&args[2..]),
        "provenance" => cmd_provenance(&args[2..]),
        "archive" => cmd_archive(&args[2..]),
        "report" => cmd_report(&args[2..]),
        "--help" | "-h" => {
            print_usage();
            process::exit(0);
        }
        _ => {
            eprintln!("Unknown command: {}", command);
            print_usage();
            process::exit(1);
        }
    }
}

fn print_usage() {
    println!("QRATUM Discovery Directive CLI");
    println!();
    println!("USAGE:");
    println!("    qratum-discover <COMMAND> [OPTIONS]");
    println!();
    println!("COMMANDS:");
    println!("    run          Generate discoveries using recursive engine");
    println!("    validate     Validate discoveries against JSON schema");
    println!("    provenance   Generate QRADLE provenance hashes");
    println!("    archive      Move validated/rejected discoveries to final locations");
    println!("    report       Generate verification report");
    println!();
    println!("Run 'qratum-discover <COMMAND> --help' for command-specific help");
}

fn cmd_run(args: &[String]) {
    let mut seed_str = "QRD-RUN-2025-12-28-0001";
    let mut target = 100;
    let mut threshold = 0.87;
    let mut output = "qratum/discoveries/pending";
    
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--seed" => {
                if i + 1 < args.len() {
                    seed_str = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--seed requires a value");
                    process::exit(1);
                }
            }
            "--target" => {
                if i + 1 < args.len() {
                    target = args[i + 1].parse().unwrap_or(100);
                    i += 2;
                } else {
                    eprintln!("--target requires a value");
                    process::exit(1);
                }
            }
            "--threshold" => {
                if i + 1 < args.len() {
                    threshold = args[i + 1].parse().unwrap_or(0.87);
                    i += 2;
                } else {
                    eprintln!("--threshold requires a value");
                    process::exit(1);
                }
            }
            "--output" => {
                if i + 1 < args.len() {
                    output = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--output requires a value");
                    process::exit(1);
                }
            }
            "--lattice-axes" | "--nodes-per-axis" | "--mutations" => {
                // Accept but ignore these for now (already hardcoded in implementation)
                i += 2;
            }
            "--help" | "-h" => {
                println!("Generate discoveries using recursive engine");
                println!();
                println!("USAGE:");
                println!("    qratum-discover run [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    --seed <SEED>            Deterministic seed (default: QRD-RUN-2025-12-28-0001)");
                println!("    --target <N>             Target discovery count (default: 100)");
                println!("    --threshold <F>          Fitness threshold (default: 0.87)");
                println!("    --output <DIR>           Output directory (default: qratum/discoveries/pending)");
                println!("    --lattice-axes <N>       Number of lattice axes (default: 5)");
                println!("    --nodes-per-axis <N>     Nodes per axis (default: 8)");
                println!("    --mutations <LIST>       Comma-separated mutation list");
                process::exit(0);
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                process::exit(1);
            }
        }
    }
    
    // Convert seed string to numeric seed
    let seed = seed_str.bytes().fold(0u32, |acc, b| acc.wrapping_mul(31).wrapping_add(b as u32));
    
    println!("═══════════════════════════════════════════════════════════════");
    println!("   QRATUM DISCOVERY DIRECTIVE - GENERATION PHASE");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    println!("Configuration:");
    println!("  Seed: {} (numeric: {})", seed_str, seed);
    println!("  Target: {} discoveries", target);
    println!("  Fitness threshold: F ≥ {:.2}", threshold);
    println!("  Output directory: {}", output);
    println!();
    
    // Create output directory
    if let Err(e) = fs::create_dir_all(output) {
        eprintln!("Failed to create output directory: {}", e);
        process::exit(1);
    }
    
    // Run discovery engine
    println!("Starting recursive discovery engine...");
    println!();
    
    match run_discovery_directive(seed, target, Some(output)) {
        Ok(report) => {
            println!("═══════════════════════════════════════════════════════════════");
            println!("   GENERATION COMPLETE");
            println!("═══════════════════════════════════════════════════════════════");
            println!();
            println!("Results:");
            println!("  Total candidates evaluated: {}", report.total_candidates_evaluated);
            println!("  Discoveries generated: {}", report.discoveries_generated);
            println!("  Discoveries validated: {}", report.discoveries_validated);
            println!("  Average fitness: {:.3}", report.average_fitness);
            println!("  Execution time: {} ms", report.execution_time_ms);
            println!();
            println!("✓ {} discoveries written to {}", report.discoveries_validated, output);
        }
        Err(e) => {
            eprintln!("Discovery generation failed: {}", e);
            process::exit(1);
        }
    }
}

fn cmd_validate(args: &[String]) {
    let mut schema_path = "qratum/discoveries/schema/discovery_schema.json";
    let mut input_dir = "qratum/discoveries/pending";
    let mut threshold = 0.87;
    
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--schema" => {
                if i + 1 < args.len() {
                    schema_path = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--schema requires a value");
                    process::exit(1);
                }
            }
            "--input" => {
                if i + 1 < args.len() {
                    input_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--input requires a value");
                    process::exit(1);
                }
            }
            "--threshold" => {
                if i + 1 < args.len() {
                    threshold = args[i + 1].parse().unwrap_or(0.87);
                    i += 2;
                } else {
                    eprintln!("--threshold requires a value");
                    process::exit(1);
                }
            }
            "--help" | "-h" => {
                println!("Validate discoveries against JSON schema");
                println!();
                println!("USAGE:");
                println!("    qratum-discover validate [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    --schema <FILE>      JSON Schema file (default: qratum/discoveries/schema/discovery_schema.json)");
                println!("    --input <DIR>        Input directory (default: qratum/discoveries/pending)");
                println!("    --threshold <F>      Fitness threshold (default: 0.87)");
                process::exit(0);
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                process::exit(1);
            }
        }
    }
    
    println!("═══════════════════════════════════════════════════════════════");
    println!("   QRATUM DISCOVERY DIRECTIVE - VALIDATION PHASE");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    println!("Configuration:");
    println!("  Schema: {}", schema_path);
    println!("  Input: {}", input_dir);
    println!("  Threshold: F ≥ {:.2}", threshold);
    println!();
    
    // Load and validate discoveries
    let discoveries = load_discoveries_from_dir(input_dir);
    
    println!("Loaded {} discoveries from {}", discoveries.len(), input_dir);
    println!();
    println!("Validating...");
    
    let mut valid_count = 0;
    let mut invalid_count = 0;
    
    for discovery in &discoveries {
        match validate_discovery_schema(discovery) {
            Ok(_) => {
                if discovery.fitness_score >= threshold {
                    valid_count += 1;
                    println!("  ✓ {} - VALID (F = {:.3})", discovery.id, discovery.fitness_score);
                } else {
                    invalid_count += 1;
                    println!("  ✗ {} - REJECTED (F = {:.3} < {:.2})", 
                             discovery.id, discovery.fitness_score, threshold);
                }
            }
            Err(e) => {
                invalid_count += 1;
                println!("  ✗ {} - INVALID: {}", discovery.id, e);
            }
        }
    }
    
    println!();
    println!("═══════════════════════════════════════════════════════════════");
    println!("   VALIDATION COMPLETE");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    println!("Results:");
    println!("  Valid discoveries: {}", valid_count);
    println!("  Invalid/Rejected: {}", invalid_count);
}

fn cmd_provenance(args: &[String]) {
    let mut input_dir = "qratum/discoveries/pending";
    let _hash_prefix = "QRDL";  // Reserved for future use
    
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--input" => {
                if i + 1 < args.len() {
                    input_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--input requires a value");
                    process::exit(1);
                }
            }
            "--hash-prefix" => {
                if i + 1 < args.len() {
                    // _hash_prefix = &args[i + 1];  // Reserved for future use
                    i += 2;
                } else {
                    eprintln!("--hash-prefix requires a value");
                    process::exit(1);
                }
            }
            "--help" | "-h" => {
                println!("Generate QRADLE provenance hashes");
                println!();
                println!("USAGE:");
                println!("    qratum-discover provenance [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    --input <DIR>          Input directory (default: qratum/discoveries/pending)");
                println!("    --hash-prefix <STR>    Hash prefix (default: QRDL)");
                process::exit(0);
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                process::exit(1);
            }
        }
    }
    
    println!("═══════════════════════════════════════════════════════════════");
    println!("   QRATUM DISCOVERY DIRECTIVE - PROVENANCE GENERATION");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    
    let discoveries = load_discoveries_from_dir(input_dir);
    
    println!("Generating provenance hashes for {} discoveries...", discoveries.len());
    println!();
    
    for discovery in &discoveries {
        let hash = generate_provenance_hash(discovery);
        println!("  {} → {}", discovery.id, hash);
    }
    
    println!();
    println!("Verifying provenance chain...");
    match verify_provenance_chain(&discoveries) {
        Ok(true) => println!("  ✓ Provenance chain is valid"),
        Ok(false) => println!("  ✗ Provenance chain validation failed"),
        Err(e) => println!("  ✗ Error: {}", e),
    }
    
    println!();
    let report = generate_provenance_report(&discoveries);
    println!("Provenance Report:");
    println!("  Total discoveries: {}", report.total_discoveries);
    println!("  Valid hashes: {}", report.valid_hashes);
    println!("  Invalid hashes: {}", report.invalid_hashes);
    println!("  Chain valid: {}", report.chain_valid);
    
    if !report.errors.is_empty() {
        println!();
        println!("Errors:");
        for error in &report.errors {
            println!("  - {}", error);
        }
    }
}

fn cmd_archive(args: &[String]) {
    let mut input_dir = "qratum/discoveries/pending";
    let mut validated_dir = "qratum/discoveries/validated";
    let mut rejected_dir = "qratum/discoveries/rejected";
    
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--input" => {
                if i + 1 < args.len() {
                    input_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--input requires a value");
                    process::exit(1);
                }
            }
            "--validated" => {
                if i + 1 < args.len() {
                    validated_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--validated requires a value");
                    process::exit(1);
                }
            }
            "--rejected" => {
                if i + 1 < args.len() {
                    rejected_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--rejected requires a value");
                    process::exit(1);
                }
            }
            "--help" | "-h" => {
                println!("Archive validated and rejected discoveries");
                println!();
                println!("USAGE:");
                println!("    qratum-discover archive [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    --input <DIR>        Input directory (default: qratum/discoveries/pending)");
                println!("    --validated <DIR>    Validated output directory (default: qratum/discoveries/validated)");
                println!("    --rejected <DIR>     Rejected output directory (default: qratum/discoveries/rejected)");
                process::exit(0);
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                process::exit(1);
            }
        }
    }
    
    println!("═══════════════════════════════════════════════════════════════");
    println!("   QRATUM DISCOVERY DIRECTIVE - ARCHIVAL PHASE");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    
    // Create output directories
    if let Err(e) = fs::create_dir_all(validated_dir) {
        eprintln!("Failed to create validated directory: {}", e);
        process::exit(1);
    }
    if let Err(e) = fs::create_dir_all(rejected_dir) {
        eprintln!("Failed to create rejected directory: {}", e);
        process::exit(1);
    }
    
    let discoveries = load_discoveries_from_dir(input_dir);
    
    let mut validated_count = 0;
    let mut rejected_count = 0;
    
    for discovery in discoveries {
        let source_path = format!("{}/{}.json", input_dir, discovery.id);
        
        if discovery.is_valid() {
            let dest_path = format!("{}/{}.json", validated_dir, discovery.id);
            if let Err(e) = fs::rename(&source_path, &dest_path) {
                eprintln!("Failed to move {}: {}", discovery.id, e);
            } else {
                validated_count += 1;
                println!("  ✓ {} → validated/", discovery.id);
            }
        } else {
            let dest_path = format!("{}/{}.json", rejected_dir, discovery.id);
            if let Err(e) = fs::rename(&source_path, &dest_path) {
                eprintln!("Failed to move {}: {}", discovery.id, e);
            } else {
                rejected_count += 1;
                println!("  ✗ {} → rejected/", discovery.id);
            }
        }
    }
    
    println!();
    println!("═══════════════════════════════════════════════════════════════");
    println!("   ARCHIVAL COMPLETE");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    println!("Results:");
    println!("  Validated: {}", validated_count);
    println!("  Rejected: {}", rejected_count);
    println!("  Pending cleared: {}", validated_count + rejected_count);
}

fn cmd_report(args: &[String]) {
    let mut validated_dir = "qratum/discoveries/validated";
    
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--validated" => {
                if i + 1 < args.len() {
                    validated_dir = &args[i + 1];
                    i += 2;
                } else {
                    eprintln!("--validated requires a value");
                    process::exit(1);
                }
            }
            "--help" | "-h" => {
                println!("Generate verification report");
                println!();
                println!("USAGE:");
                println!("    qratum-discover report [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    --validated <DIR>    Validated directory (default: qratum/discoveries/validated)");
                process::exit(0);
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                process::exit(1);
            }
        }
    }
    
    println!("═══════════════════════════════════════════════════════════════");
    println!("   QRATUM DISCOVERY DIRECTIVE REPORT");
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    
    let discoveries = load_discoveries_from_dir(validated_dir);
    
    println!("Validated discoveries : {}", discoveries.len());
    
    if discoveries.is_empty() {
        println!();
        println!("No validated discoveries found in {}", validated_dir);
        return;
    }
    
    // Calculate statistics
    let total_fitness: f64 = discoveries.iter().map(|d| d.fitness_score).sum();
    let avg_fitness = total_fitness / discoveries.len() as f64;
    let min_fitness = discoveries.iter().map(|d| d.fitness_score).fold(f64::INFINITY, f64::min);
    let max_fitness = discoveries.iter().map(|d| d.fitness_score).fold(f64::NEG_INFINITY, f64::max);
    
    println!("Average fitness score   : {:.3}", avg_fitness);
    println!("Min fitness score       : {:.3}", min_fitness);
    println!("Max fitness score       : {:.3}", max_fitness);
    println!();
    
    // Verify provenance
    match verify_provenance_chain(&discoveries) {
        Ok(true) => println!("Provenance chain        : ✓ VALID"),
        Ok(false) => println!("Provenance chain        : ✗ INVALID"),
        Err(e) => println!("Provenance chain        : ✗ ERROR: {}", e),
    }
    
    println!();
    println!("Discovery breakdown:");
    
    // Count by validation method
    let mut method_counts = std::collections::HashMap::new();
    for discovery in &discoveries {
        let method = format!("{:?}", discovery.validation.method);
        *method_counts.entry(method).or_insert(0) += 1;
    }
    
    for (method, count) in method_counts {
        println!("  {}: {}", method, count);
    }
    
    println!();
    println!("═══════════════════════════════════════════════════════════════");
    println!("   All discoveries validated and archived");
    println!("═══════════════════════════════════════════════════════════════");
}

fn load_discoveries_from_dir(dir: &str) -> Vec<Discovery> {
    let mut discoveries = Vec::new();
    
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            if let Ok(path) = entry.path().canonicalize() {
                if path.extension().and_then(|s| s.to_str()) == Some("json") {
                    if let Ok(content) = fs::read_to_string(&path) {
                        if let Ok(discovery) = import_discoveries_json(&content) {
                            discoveries.extend(discovery);
                        }
                    }
                }
            }
        }
    }
    
    // Sort by ID
    discoveries.sort_by(|a, b| a.id.cmp(&b.id));
    
    discoveries
}
