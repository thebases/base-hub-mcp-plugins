"""Build an uploadable plugin zip with .claude-plugin/plugin.json at the zip root.

Usage: python scripts/build_plugin_zip.py [plugin_dir] [output_zip]
Defaults: plugins/base-hub -> dist/base-hub.zip
"""
import sys
import zipfile
from pathlib import Path

SKIP = {".DS_Store", "Thumbs.db"}

repo = Path(__file__).resolve().parent.parent
plugin_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "plugins" / "base-hub"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / "dist" / f"{plugin_dir.name}.zip"

if not (plugin_dir / ".claude-plugin" / "plugin.json").is_file():
    sys.exit(f"{plugin_dir} has no .claude-plugin/plugin.json")

out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(plugin_dir.rglob("*")):
        if f.is_file() and f.name not in SKIP:
            zf.write(f, f.relative_to(plugin_dir).as_posix())

print(f"Wrote {out}")
