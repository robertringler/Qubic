# Security Posture

* **TLS**: Managed by cert-manager ClusterIssuer `letsencrypt`. Apply `security/cluster-issuer.yaml` to enable automatic certificate provisioning.
* **Authentication**: OAuth2 bearer tokens validated via JWKS endpoint configured through environment variable `OAUTH_JWKS_URL`.
* **Network Policies**: Kubernetes NetworkPolicy restricts ingress to backend pods from the ingress controller namespace only.
* **IAM**: Terraform provisions a scoped IAM role for the backend service account with permissions limited to required AWS APIs.
* **Secrets**: Use AWS Secrets Manager or HashiCorp Vault; GitHub Actions expects secrets stored as repository secrets.

