# Mindustry Modding & Packaging Guidelines (Lessons Learned)

## 1. Mindustry Mod Update Mechanism
Mindustry features a robust in-game mod browser. When a mod is downloaded via this browser (especially from GitHub), the game tracks its metadata.
*   **The Issue:** If you modify a GitHub-sourced mod locally (e.g., editing `mod.json` or content files) and place it in the `mods` folder, **Mindustry will automatically redownload the original ZIP from GitHub on startup and overwrite your changes.**
*   **The Failed Fix:** Changing the internal `name` in `mod.json` or modifying the extracted folder name is often insufficient if the game still detects the `mod.json` structure or has cached the mod state.
*   **The Correct Fix:** To apply a local fix to a GitHub-sourced mod, you must:
    1. Extract the original `.zip`.
    2. Make your modifications.
    3. Update the `version` string in `mod.json` (e.g., `1.9.1` -> `1.9.1.1-fixed`) so the game recognizes it as a newer version rather than a corrupted installation.
    4. Repackage the zip **exactly** matching the original filename (e.g., `aureusstratusexogenesis.zip`).

## 2. ZIP Archive Packaging & Security (The "Not permitted" Error)
When repackaging a mod into a `.zip` file, the internal path separators are **critical**.
*   **The Issue:** Windows PowerShell's `Compress-Archive` command creates ZIP archives where the internal directory separators are backslashes (`\`).
*   **The Security Block:** Mindustry's mod loader (`arc.files.ZipFi.read`) includes "Zip Slip" vulnerability protection. If it encounters a backslash (`\`) in a ZIP entry path, it instantly throws a `java.lang.RuntimeException: Not permitted.` and completely fails to load the mod, hiding the tech tree and breaking the game.
*   **The Correct Fix:** **Never use Windows `Compress-Archive` for Mindustry mods.** Always use a tool that enforces POSIX standard forward slashes (`/`), such as:
    *   A custom Python script utilizing `zipfile` with `replace('\\', '/')`.
    *   Standard archiving tools like `7z` or `tar` configured for cross-platform compatibility.

## 3. Tech Tree Sibling Dependencies
When fixing missing tech tree nodes (e.g., `b-calamity-forge` not showing up):
*   Ensure that a `research` property exists in the block's `.json` definition.
*   Example: `"research": "b-stellar-furnace"`
*   Verify that the parent node actually exists in the current mod environment and is accessible, otherwise the block will remain hidden.
