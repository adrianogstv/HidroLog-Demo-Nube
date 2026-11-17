//! Adaptador Tauri 2. Incorporar como módulo nuevo; no reemplazar main.rs.
//! Requiere Python con cryptography y el kit de demostración en este PC.
use serde_json::{json, Value};
use std::{io::Write, process::{Command, Stdio}};
use tauri::Manager;

#[tauri::command]
pub async fn nube_subir_proyecto(app: tauri::AppHandle, ruta: String, password: String) -> Result<Value, String> {
    if password.len() > 1024 || ruta.len() > 4096 { return Err("Entrada no válida".into()); }
    let config_path = app.path().resolve("nube/config_nube.json", tauri::path::BaseDirectory::Resource)
        .map_err(|_| "No se localizó la configuración del módulo".to_string())?;
    tauri::async_runtime::spawn_blocking(move || {
        let bytes = std::fs::read(config_path).map_err(|_| "Falta nube/config_nube.json".to_string())?;
        let config: Value = serde_json::from_slice(&bytes).map_err(|_| "Configuración no válida".to_string())?;
        let python = config["python"].as_str().ok_or("Falta el ejecutable Python")?;
        let script = config["script"].as_str().ok_or("Falta la ruta del módulo")?;
        let mut cmd = Command::new(python);
        cmd.args(["-B", "-X", "utf8", script, "bridge"])
            .stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
        #[cfg(target_os = "windows")]
        { use std::os::windows::process::CommandExt; cmd.creation_flags(0x08000000); }
        let mut child = cmd.spawn().map_err(|_| "No se pudo iniciar el módulo Python".to_string())?;
        let body = serde_json::to_vec(&json!({"path": ruta, "password": password}))
            .map_err(|_| "No se pudo preparar la solicitud".to_string())?;
        if let Some(mut input) = child.stdin.take() {
            input.write_all(&body).map_err(|_| "No se pudo comunicar con el módulo".to_string())?;
        }
        let output = child.wait_with_output().map_err(|_| "No se pudo leer el resultado".to_string())?;
        if !output.status.success() { return Err("El módulo no inició correctamente; revisa Python y dependencias".to_string()); }
        // No registrar body, password, stderr ni stdout completo.
        serde_json::from_slice::<Value>(&output.stdout).map_err(|_| "Respuesta del módulo no válida".to_string())
    }).await.map_err(|_| "No se pudo ejecutar la subida".to_string())?
}
