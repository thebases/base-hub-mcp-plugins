"""Build an uploadable plugin zip with .claude-plugin/plugin.json at the zip root.

Usage: python scripts/build_plugin_zip.py [plugin_dir] [output_zip]
Defaults: plugins/base-hub -> dist/base-hub-edc.zip
"""
import sys
import zipfile
from pathlib import Path

SKIP = {".DS_Store", "Thumbs.db"}
DEFAULT_ZIP_NAME = "base-hub-edc.zip"

repo = Path(__file__).resolve().parent.parent
plugin_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "plugins" / "base-hub"
if len(sys.argv) > 2:
    out = Path(sys.argv[2])
elif len(sys.argv) > 1:
    out = repo / "dist" / f"{plugin_dir.name}.zip"
else:
    out = repo / "dist" / DEFAULT_ZIP_NAME

if not (plugin_dir / ".claude-plugin" / "plugin.json").is_file():
    sys.exit(f"{plugin_dir} has no .claude-plugin/plugin.json")

out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(plugin_dir.rglob("*")):
        if f.is_file() and f.name not in SKIP:
            zf.write(f, f.relative_to(plugin_dir).as_posix())

print(f"Wrote {out}")
