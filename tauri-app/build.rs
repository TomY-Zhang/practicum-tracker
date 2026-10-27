fn main() {
    println!("cargo:rerun-if-env-changed=PRACTICUM_TRACKER_DB");
    tauri_build::build()
}
