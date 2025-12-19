/**
 * QuantumField - Advanced Particle System
 * 
 * Features:
 * - 50-particle quantum field simulation
 * - 60fps animation loop with requestAnimationFrame
 * - Responsive canvas with debounced resize handling
 * - Distance-based particle connections with opacity
 * - Memory leak prevention with proper cleanup
 * - Accessibility support for prefers-reduced-motion
 * 
 * @class QuantumField
 * @version 1.0.0
 * @author QRATUM Dashboard
 * @date 2025-12-19
 */

class QuantumField {
  /**
   * Initialize the QuantumField particle system
   * @param {HTMLCanvasElement} canvas - The canvas element to render on
   * @param {Object} options - Configuration options
   */
  constructor(canvas, options = {}) {
    // Canvas and context
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    
    // Configuration with defaults
    this.config = {
      particleCount: options.particleCount || 50,
      particleSize: options.particleSize || 2,
      particleSpeed: options.particleSpeed || 0.5,
      connectionDistance: options.connectionDistance || 150,
      particleColor: options.particleColor || 'rgba(100, 200, 255, 0.8)',
      connectionColor: options.connectionColor || 'rgba(100, 200, 255, 0.15)',
      fps: options.fps || 60,
      enableConnections: options.enableConnections !== false,
      ...options
    };
    
    // State management
    this.particles = [];
    this.animationId = null;
    this.lastFrameTime = 0;
    this.frameInterval = 1000 / this.config.fps;
    this.isAnimating = false;
    this.resizeTimeout = null;
    this.resizeDebounceDelay = 250;
    
    // Accessibility: Check for reduced motion preference
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Bind methods to preserve context
    this.animate = this.animate.bind(this);
    this.handleResize = this.handleResize.bind(this);
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    this.handleReducedMotionChange = this.handleReducedMotionChange.bind(this);
    
    // Initialize the system
    this.init();
  }
  
  /**
   * Initialize the particle system
   */
  init() {
    // Set canvas dimensions
    this.resizeCanvas();
    
    // Create particles
    this.createParticles();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Start animation if motion is allowed
    if (!this.prefersReducedMotion) {
      this.start();
    } else {
      // Draw static frame for reduced motion
      this.drawStaticFrame();
    }
  }
  
  /**
   * Set up event listeners for resize and visibility changes
   */
  setupEventListeners() {
    // Debounced resize handler
    window.addEventListener('resize', this.handleResize);
    
    // Pause animation when page is hidden
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
    
    // Listen for reduced motion preference changes
    const motionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motionMediaQuery.addEventListener) {
      motionMediaQuery.addEventListener('change', this.handleReducedMotionChange);
    } else {
      // Fallback for older browsers
      motionMediaQuery.addListener(this.handleReducedMotionChange);
    }
  }
  
  /**
   * Handle window resize with debouncing
   */
  handleResize() {
    clearTimeout(this.resizeTimeout);
    this.resizeTimeout = setTimeout(() => {
      this.resizeCanvas();
      this.repositionParticles();
    }, this.resizeDebounceDelay);
  }
  
  /**
   * Handle visibility change (pause when hidden)
   */
  handleVisibilityChange() {
    if (document.hidden) {
      this.pause();
    } else if (!this.prefersReducedMotion) {
      this.start();
    }
  }
  
  /**
   * Handle reduced motion preference changes
   */
  handleReducedMotionChange(e) {
    this.prefersReducedMotion = e.matches;
    if (this.prefersReducedMotion) {
      this.pause();
      this.drawStaticFrame();
    } else {
      this.start();
    }
  }
  
  /**
   * Resize canvas to fill container
   */
  resizeCanvas() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    
    this.ctx.scale(dpr, dpr);
    
    this.width = rect.width;
    this.height = rect.height;
  }
  
  /**
   * Create initial particle array
   */
  createParticles() {
    this.particles = [];
    for (let i = 0; i < this.config.particleCount; i++) {
      this.particles.push(this.createParticle());
    }
  }
  
  /**
   * Create a single particle with random properties
   * @returns {Object} Particle object
   */
  createParticle() {
    return {
      x: Math.random() * this.width,
      y: Math.random() * this.height,
      vx: (Math.random() - 0.5) * this.config.particleSpeed,
      vy: (Math.random() - 0.5) * this.config.particleSpeed,
      size: this.config.particleSize * (0.5 + Math.random() * 0.5),
      opacity: 0.3 + Math.random() * 0.7
    };
  }
  
  /**
   * Reposition particles after resize (maintain relative positions)
   */
  repositionParticles() {
    // Particles will naturally redistribute through their movement
    // No need to force repositioning, but ensure they're within bounds
    this.particles.forEach(particle => {
      particle.x = Math.min(particle.x, this.width);
      particle.y = Math.min(particle.y, this.height);
    });
  }
  
  /**
   * Start the animation loop
   */
  start() {
    if (!this.isAnimating && !this.prefersReducedMotion) {
      this.isAnimating = true;
      this.lastFrameTime = performance.now();
      this.animationId = requestAnimationFrame(this.animate);
    }
  }
  
  /**
   * Pause the animation loop
   */
  pause() {
    if (this.isAnimating) {
      this.isAnimating = false;
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }
  }
  
  /**
   * Main animation loop (60fps with frame limiting)
   * @param {number} currentTime - Current timestamp from requestAnimationFrame
   */
  animate(currentTime) {
    if (!this.isAnimating) return;
    
    // Request next frame
    this.animationId = requestAnimationFrame(this.animate);
    
    // Calculate elapsed time since last frame
    const elapsed = currentTime - this.lastFrameTime;
    
    // Limit to target FPS
    if (elapsed < this.frameInterval) return;
    
    // Update last frame time (with correction for frame interval)
    this.lastFrameTime = currentTime - (elapsed % this.frameInterval);
    
    // Update and render
    this.update();
    this.render();
  }
  
  /**
   * Update particle positions
   */
  update() {
    this.particles.forEach(particle => {
      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;
      
      // Bounce off edges
      if (particle.x < 0 || particle.x > this.width) {
        particle.vx *= -1;
        particle.x = Math.max(0, Math.min(this.width, particle.x));
      }
      if (particle.y < 0 || particle.y > this.height) {
        particle.vy *= -1;
        particle.y = Math.max(0, Math.min(this.height, particle.y));
      }
    });
  }
  
  /**
   * Render particles and connections
   */
  render() {
    // Clear canvas
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    // Draw connections first (behind particles)
    if (this.config.enableConnections) {
      this.drawConnections();
    }
    
    // Draw particles
    this.drawParticles();
  }
  
  /**
   * Draw all particles
   */
  drawParticles() {
    this.particles.forEach(particle => {
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fillStyle = this.config.particleColor;
      this.ctx.globalAlpha = particle.opacity;
      this.ctx.fill();
      this.ctx.globalAlpha = 1;
    });
  }
  
  /**
   * Draw connections between nearby particles with distance-based opacity
   */
  drawConnections() {
    const maxDistance = this.config.connectionDistance;
    
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const p1 = this.particles[i];
        const p2 = this.particles[j];
        
        // Calculate distance
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Draw connection if within range
        if (distance < maxDistance) {
          // Calculate opacity based on distance (closer = more opaque)
          const opacity = (1 - distance / maxDistance) * 0.5;
          
          this.ctx.beginPath();
          this.ctx.moveTo(p1.x, p1.y);
          this.ctx.lineTo(p2.x, p2.y);
          this.ctx.strokeStyle = this.config.connectionColor;
          this.ctx.globalAlpha = opacity;
          this.ctx.lineWidth = 1;
          this.ctx.stroke();
          this.ctx.globalAlpha = 1;
        }
      }
    }
  }
  
  /**
   * Draw a static frame (for reduced motion preference)
   */
  drawStaticFrame() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    // Draw particles only (no animation, no connections)
    this.particles.forEach(particle => {
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fillStyle = this.config.particleColor;
      this.ctx.globalAlpha = particle.opacity * 0.5; // Dimmer for static
      this.ctx.fill();
      this.ctx.globalAlpha = 1;
    });
  }
  
  /**
   * Clean up resources and prevent memory leaks
   */
  destroy() {
    // Stop animation
    this.pause();
    
    // Clear resize timeout
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
      this.resizeTimeout = null;
    }
    
    // Remove event listeners
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    
    const motionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motionMediaQuery.removeEventListener) {
      motionMediaQuery.removeEventListener('change', this.handleReducedMotionChange);
    } else {
      // Fallback for older browsers
      motionMediaQuery.removeListener(this.handleReducedMotionChange);
    }
    
    // Clear particles array
    this.particles = [];
    
    // Clear canvas
    if (this.ctx) {
      this.ctx.clearRect(0, 0, this.width, this.height);
    }
    
    // Nullify references
    this.canvas = null;
    this.ctx = null;
    this.animationId = null;
  }
  
  /**
   * Update configuration dynamically
   * @param {Object} newConfig - New configuration options
   */
  updateConfig(newConfig) {
    const needsRecreate = newConfig.particleCount && 
                          newConfig.particleCount !== this.config.particleCount;
    
    // Merge new config
    this.config = { ...this.config, ...newConfig };
    
    // Recreate particles if count changed
    if (needsRecreate) {
      this.createParticles();
    }
    
    // Update frame interval if FPS changed
    if (newConfig.fps) {
      this.frameInterval = 1000 / this.config.fps;
    }
  }
  
  /**
   * Get current particle count
   * @returns {number} Current number of particles
   */
  getParticleCount() {
    return this.particles.length;
  }
  
  /**
   * Check if animation is running
   * @returns {boolean} Animation state
   */
  isRunning() {
    return this.isAnimating;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuantumField;
}

// Also make available globally
if (typeof window !== 'undefined') {
  window.QuantumField = QuantumField;
}
