//! VCS adapter interface for multi-VCS support

use crate::{object_store::ObjectId, Result};

/// Universal VCS adapter trait
///
/// Provides a common interface for different VCS backends (Git, Mercurial, SVN)
pub trait VcsAdapter {
    /// Get the name of the VCS system
    fn name(&self) -> &str;

    /// Initialize a new repository
    fn init(&mut self) -> Result<()>;

    /// Clone a repository from a URL
    fn clone(&mut self, url: &str) -> Result<()>;

    /// Commit changes with a message
    fn commit(&mut self, message: &str) -> Result<ObjectId>;

    /// Get the current HEAD commit
    fn get_head(&self) -> Result<ObjectId>;

    /// List all branches
    fn list_branches(&self) -> Result<Vec<String>>;

    /// Create a new branch
    fn create_branch(&mut self, name: &str) -> Result<()>;

    /// Checkout a branch or commit
    fn checkout(&mut self, target: &str) -> Result<()>;

    /// Merge a branch into current branch
    fn merge(&mut self, branch: &str) -> Result<ObjectId>;
}

/// Configuration for VCS repository
#[derive(Debug, Clone)]
pub struct VcsConfig {
    pub repo_path: String,
    pub vcs_type: VcsType,
}

/// Supported VCS types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VcsType {
    Git,
    Mercurial,
    Svn,
}

impl VcsType {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "git" => Some(VcsType::Git),
            "hg" | "mercurial" => Some(VcsType::Mercurial),
            "svn" | "subversion" => Some(VcsType::Svn),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &str {
        match self {
            VcsType::Git => "git",
            VcsType::Mercurial => "mercurial",
            VcsType::Svn => "svn",
        }
    }
}
