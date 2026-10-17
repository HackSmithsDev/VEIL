#[tauri::command]
fn uninstall_application(app: tauri::AppHandle) -> Result<(), String> {
  #[cfg(target_os = "macos")]
  {
    use std::path::Path;
    use std::process::Command;

    let executable = std::env::current_exe()
      .map_err(|error| format!("Could not locate VEIL Guard: {error}"))?;
    let bundle = executable
      .ancestors()
      .find(|path| path.extension().is_some_and(|extension| extension == "app"))
      .ok_or_else(|| "VEIL Guard is not running from an installed app bundle.".to_owned())?;

    if bundle.file_name().and_then(|name| name.to_str()) != Some("VEIL Guard.app") {
      return Err("The running application does not appear to be VEIL Guard.".to_owned());
    }

    let bundle = std::fs::canonicalize(bundle)
      .map_err(|error| format!("Could not resolve the app location: {error}"))?;
    let home_app = std::env::var_os("HOME")
      .map(|home| Path::new(&home).join("Applications").join("VEIL Guard.app"));
    let allowed_locations = [
      Some(Path::new("/Applications/VEIL Guard.app").to_path_buf()),
      home_app,
    ];
    if !allowed_locations.iter().flatten().any(|location| {
      std::fs::canonicalize(location).is_ok_and(|allowed| allowed == bundle)
    }) {
      return Err(
        "For safety, VEIL Guard can only remove its installed app from Applications."
          .to_owned(),
      );
    }

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

    let script = "on run argv\n tell application \"Finder\" to delete (POSIX file (item 1 of argv))\nend run";
    let result = Command::new("/usr/bin/osascript")
      .arg("-e")
      .arg(script)
      .arg(bundle.as_os_str())
      .output()
      .map_err(|error| format!("Could not move VEIL Guard to the Trash: {error}"))?;
    if !result.status.success() {
      let detail = String::from_utf8_lossy(&result.stderr).trim().to_owned();
      return Err(if detail.is_empty() {
        "Finder could not move VEIL Guard to the Trash.".to_owned()
      } else {
        format!("Finder could not move VEIL Guard to the Trash: {detail}")
      });
    }

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
    .invoke_handler(tauri::generate_handler![uninstall_application])
    .run(tauri::generate_context!())
    .expect("error while building tauri application");
}
