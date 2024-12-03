mod commands;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            commands::login::login,
            commands::login::verify_token,
            commands::login::protectedroute,
            commands::projects::get_all_projects,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}