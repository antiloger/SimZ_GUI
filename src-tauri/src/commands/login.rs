use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    sub: String,  // subject (user id)
    exp: usize,   // expiration time
    role: String, // user role
}

#[derive(Debug, Serialize, Deserialize)]
pub struct User {
    username: String,
    password_hash: String,
    role: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginCredentials {
    username: String,
    password: String,
}

const JWT_SECRET: &[u8] = b"your-secret-key";

#[tauri::command]
pub async fn login(credentials: LoginCredentials) -> Result<String, String> {
    // In a real app, verify against a database
    // This is just a demonstration
    if credentials.username == "demo" && credentials.password == "password" {
        let expiration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as usize
            + 3600; // 1 hour from now

        let claims = Claims {
            sub: credentials.username,
            exp: expiration,
            role: "user".to_string(),
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(JWT_SECRET),
        )
        .map_err(|e| e.to_string())
    } else {
        Err("Invalid credentials".to_string())
    }
}

#[tauri::command]
pub fn verify_token(token: String) -> Result<Claims, String> {
    let validation = Validation::new(Algorithm::HS256);

    // decode::{
    //     &token,
    //     &DecodingKey::from_secret(JWT_SECRET),
    //     &validation,
    // }
    //
    decode(&token, &DecodingKey::from_secret(JWT_SECRET), &validation)
        .map(|tokendata| tokendata.claims)
        .map_err(|e| e.to_string())
}

// Middleware-style function to check permissions
pub fn check_permission(token: &str, required_role: &str) -> Result<bool, String> {
    let claims = verify_token(token.to_string())?;
    Ok(claims.role == required_role)
}

#[tauri::command]
pub async fn protectedroute(token: String) -> Result<String, String> {
    // Verify the token first
    verify_token(token)?;
    Ok("Access granted to protected resource".to_string())
}
