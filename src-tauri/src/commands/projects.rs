use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct AllProject {
    name: String,
    project_type: String,
    last_used: String,
}

#[tauri::command]
pub fn get_all_projects() -> Vec<AllProject> {
    let mut data = Vec::new(); // Make the vector mutable to push items
    for i in 1..10 {
        data.push(AllProject {
            name: format!("Project {}", i),
            project_type: "Type A".to_string(), // Example project type
            last_used: format!("2024-10-{:02}", i), // Example last used date
        });
    }

    data
}
