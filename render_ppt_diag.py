import os
import subprocess
from pathlib import Path

base_dir = Path("d:/Projects/Multiplayer_AI")
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
browser = chrome_path if os.path.exists(chrome_path) else edge_path

targets = ["ppt_architecture_diagram", "ppt_dual_memory_diagram"]

for target in targets:
    svg_path = base_dir / f"{target}.svg"
    html_path = base_dir / f"{target}.html"
    png_path = base_dir / f"{target}.png"

    if not svg_path.exists():
        continue

    svg_content = svg_path.read_text(encoding="utf-8")
    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{ margin:0; padding:0; background:#0f172a; overflow:hidden; }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""
    html_path.write_text(html_wrapper, encoding="utf-8")

    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        f"--screenshot={png_path.resolve()}",
        "--window-size=1200,675",
        f"file:///{html_path.resolve()}".replace("\\", "/")
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"Generated {png_path.name}: {png_path.exists()} ({png_path.stat().st_size} bytes)")
