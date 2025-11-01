# OAuth2 / JWT Pattern

* Expect `Authorization: Bearer <token>` header.
* Validate tokens using JWKS endpoint defined by `OAUTH_JWKS_URL`.
* Scopes: `quasim.read`, `quasim.execute`.
* Rotate signing keys every 30 days.

