/**
 * QuASIM C++ SDK - High-level client library for QuASIM API
 * 
 * This SDK provides:
 * - Thin gRPC client for high-performance communication
 * - CMake integration via find_package(QuASIM)
 * - Exception-safe RAII wrappers
 * - Async operation support
 * 
 * Example:
 *   #include <quasim_client.hpp>
 *   
 *   quasim::Client client("localhost:50051");
 *   auto job = client.submit_cfd("wing.msh", config);
 *   auto result = client.wait_for_completion(job.id);
 */

#ifndef QUASIM_CLIENT_HPP
#define QUASIM_CLIENT_HPP

#include <memory>
#include <string>
#include <map>
#include <chrono>
#include <functional>

namespace quasim {

// Forward declarations
class ClientImpl;

/**
 * Job execution status
 */
enum class JobStatus {
    QUEUED,
    RUNNING,
    COMPLETED,
    FAILED,
    CANCELLED
};

/**
 * Job type enumeration
 */
enum class JobType {
    CFD,
    FEA,
    ORBITAL_MC,
    QUANTUM_CIRCUIT,
    DIGITAL_TWIN
};

/**
 * Job configuration
 */
struct JobConfig {
    std::map<std::string, std::string> params;
    int priority = 5;
    int timeout_seconds = 3600;
};

/**
 * Job representation
 */
struct Job {
    std::string id;
    JobStatus status;
    JobType type;
    std::string submitted_at;
    float progress = 0.0f;
};

/**
 * Client configuration
 */
struct ClientConfig {
    std::string api_url = "localhost:50051";
    std::string api_key;
    int timeout_seconds = 30;
    int max_retries = 3;
    bool use_tls = false;
};

/**
 * QuASIM API Client
 * 
 * High-level client for interacting with QuASIM service.
 * Thread-safe and exception-safe.
 */
class Client {
public:
    /**
     * Construct client with default configuration
     */
    Client();
    
    /**
     * Construct client with custom configuration
     * 
     * @param config Client configuration
     */
    explicit Client(const ClientConfig& config);
    
    /**
     * Destructor
     */
    ~Client();
    
    // Disable copy, allow move
    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;
    Client(Client&&) noexcept;
    Client& operator=(Client&&) noexcept;
    
    /**
     * Submit a generic job
     * 
     * @param type Job type
     * @param config Job configuration
     * @return Job object
     */
    Job submit_job(JobType type, const JobConfig& config);
    
    /**
     * Submit a CFD simulation job
     * 
     * @param mesh_file Path to mesh file
     * @param config CFD configuration
     * @return Job object
     */
    Job submit_cfd(
        const std::string& mesh_file,
        const std::map<std::string, std::string>& config
    );
    
    /**
     * Submit an FEA simulation job
     * 
     * @param mesh_file Path to mesh file
     * @param material Material properties
     * @param loads Load case definitions
     * @return Job object
     */
    Job submit_fea(
        const std::string& mesh_file,
        const std::map<std::string, std::string>& material,
        const std::map<std::string, std::string>& loads
    );
    
    /**
     * Submit an orbital Monte Carlo simulation
     * 
     * @param num_trajectories Number of trajectories
     * @param initial_conditions Initial orbital parameters
     * @return Job object
     */
    Job submit_orbital_mc(
        int num_trajectories,
        const std::map<std::string, std::string>& initial_conditions
    );
    
    /**
     * Get job status
     * 
     * @param job_id Job identifier
     * @return Job object with current status
     */
    Job get_status(const std::string& job_id);
    
    /**
     * Cancel a running job
     * 
     * @param job_id Job identifier
     * @return true if cancelled successfully
     */
    bool cancel_job(const std::string& job_id);
    
    /**
     * Wait for job to complete
     * 
     * @param job_id Job identifier
     * @param poll_interval Polling interval
     * @param timeout Maximum wait time
     * @return Completed job object
     */
    Job wait_for_completion(
        const std::string& job_id,
        std::chrono::seconds poll_interval = std::chrono::seconds(5),
        std::chrono::seconds timeout = std::chrono::hours(1)
    );
    
    /**
     * Download job artifact
     * 
     * @param artifact_id Artifact identifier
     * @param output_path Path to save artifact
     * @return true if downloaded successfully
     */
    bool download_artifact(
        const std::string& artifact_id,
        const std::string& output_path
    );
    
    /**
     * Check API health
     * 
     * @return true if API is healthy
     */
    bool health_check();
    
    /**
     * Set progress callback for long-running operations
     * 
     * @param callback Progress callback function
     */
    void set_progress_callback(
        std::function<void(const std::string&, float)> callback
    );

private:
    std::unique_ptr<ClientImpl> impl_;
};

/**
 * Exception thrown by QuASIM client
 */
class ClientException : public std::runtime_error {
public:
    explicit ClientException(const std::string& message)
        : std::runtime_error(message) {}
};

} // namespace quasim

#endif // QUASIM_CLIENT_HPP
