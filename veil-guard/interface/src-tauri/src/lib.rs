#[tauri::command]
fn launch_maintenance_tool(app: tauri::AppHandle) -> Result<(), String> {
  #[cfg(target_os = "macos")]
  {
    use std::path::PathBuf;
    use std::process::Command;

    // 1. Locate current running executable
    let executable = std::env::current_exe()
      .map_err(|error| format!("Could not locate VEIL Guard: {error}"))?;

    // 2. Resolve the enclosing .app bundle
    let bundle = executable
      .ancestors()
      .find(|path| path.extension().is_some_and(|extension| extension == "app"))
      .ok_or_else(|| "VEIL Guard is not running from an installed app bundle.".to_owned())?;

    if bundle.file_name().and_then(|name| name.to_str()) != Some("VEIL Guard.app") {
      return Err("The running application does not appear to be VEIL Guard.".to_owned());
    }

    let bundle = std::fs::canonicalize(bundle)
      .map_err(|error| format!("Could not resolve the app location: {error}"))?;

    // 3. Safety Check: Verify the app is running from an official Applications directory
    let home_dir = std::env::var_os("HOME").map(PathBuf::from);
    let mut allowed_base_locations = vec![PathBuf::from("/Applications")];
    if let Some(home) = home_dir {
      allowed_base_locations.push(home.join("Applications"));
    }

    let is_in_allowed_location = allowed_base_locations.iter().any(|allowed| {
      if let Ok(canonical_allowed) = std::fs::canonicalize(allowed) {
        bundle.starts_with(&canonical_allowed)
      } else {
        false
      }
    });

    if !is_in_allowed_location {
      return Err(
        "For safety, VEIL Guard uninstallation can only be triggered from an installed Applications directory."
          .to_owned(),
      );
    }

    // 4. Identity Check: Verify CFBundleIdentifier using plutil
    let info_plist = bundle.join("Contents/Info.plist");
    let identifier = Command::new("/usr/bin/plutil")
      .args(["-extract", "CFBundleIdentifier", "raw", "-o", "-"])
      .arg(&info_plist)
      .output()
      .map_err(|error| format!("Could not verify the app bundle: {error}"))?;

    if !identifier.status.success()
      || String::from_utf8_lossy(&identifier.stdout).trim() != "com.hacksmiths.veilguard"
    {
      return Err("The selected app bundle is not the VEIL Guard application.".to_owned());
    }

    // 5. Locate maintenancetool in the installation directory
    let install_dir = bundle
      .parent()
      .ok_or_else(|| "Could not resolve application parent directory.".to_owned())?;

    let candidate_app = install_dir.join("maintenancetool.app");
    let candidate_bin = install_dir.join("maintenancetool");

    let tool_path: PathBuf = if candidate_app.exists() {
      candidate_app
    } else if candidate_bin.exists() {
      candidate_bin
    } else {
      return Err(format!(
        "Maintenance tool not found at {}. Ensure VEIL Guard was installed via the setup installer.",
        install_dir.display()
      ));
    };

    // 6. Launch maintenancetool directly into uninstall mode
    let status = Command::new("/usr/bin/open")
      .arg("-n")
      .arg(&tool_path)
      .arg("--args")
      .arg("--uninstall-only")
      .status()
      .map_err(|error| format!("Failed to launch maintenance tool: {error}"))?;

    if !status.success() {
      return Err("Failed to start the maintenance tool process.".to_owned());
    }

    // 7. Gracefully exit app
    app.exit(0);
    return Ok(());
  }

  #[cfg(not(target_os = "macos"))]
  {
    let _ = app;
    Err("In-app removal is currently available only on macOS.".to_owned())
  }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .invoke_handler(tauri::generate_handler![launch_maintenance_tool])
    .run(tauri::generate_context!())
    .expect("error while building tauri application");
}