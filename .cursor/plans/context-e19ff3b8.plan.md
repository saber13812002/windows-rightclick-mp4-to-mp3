<!-- e19ff3b8-fcdf-4e3b-8591-82dd1a3eb19f 23acdae2-2a4a-4ab1-b232-f9a3c0a3b5f3 -->
# Context Menu Installer Plan

1. Inventory Existing Tools

- Inspect folders such as `convert-mp4-to-mp3`, `split-on-silence-mp3`, etc. to confirm each tool’s Python entry script and current `.reg` template structure.

2. Define Metadata for Each Tool

- Create a compact data table (inside the script) that maps file extensions, menu labels, comments (if any), and python script paths relative to repo root.

3. Implement `generate-installers.ps1`

- Detect repo root via `$PSScriptRoot` and resolve full paths for every tool.
- Detect Python executable by probing `py`, `python`, `python3`, or registry (fallback to user prompt if no match).
- For each tool, render a `.reg` file under its folder with the correct absolute paths.
- Combine all entries into a single master `.reg` file at repo root so the user can register everything in one import.

4. Add Usage Documentation

- Update `README.md` (or create `INSTALL.md`) explaining how to run `generate-installers.ps1` and apply the resulting `.reg` files, plus troubleshooting for Python detection.

### To-dos

- [ ] Review tool folders and current reg templates
- [ ] List tool metadata for registry generation
- [ ] Implement generate-installers.ps1 logic
- [ ] Document installer usage & troubleshooting