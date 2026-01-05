from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import shutil
import re
import sys

app = FastAPI()

# =========================
# Frontend
# =========================
def resource_path(filename: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base) / filename

@app.get("/", response_class=HTMLResponse)
def index():
    html = resource_path("app_frontend.html")
    return HTMLResponse(html.read_text(encoding="utf-8"))

# =========================
# PSD COPY
# =========================
@app.post("/psd_copy/plan")
def psd_copy_plan(payload: dict):
    parent = Path(payload["parent_path"])
    suffixes = [s.strip() for s in payload.get("suffix_csv", "").split(",") if s.strip()]
    targets = []

    for p in parent.glob("*.psd"):
        name = p.stem
        for suf in suffixes:
            if name.endswith(suf):
                targets.append(p)
                break

    return {"copy_count": len(targets), "targets": [str(p) for p in targets]}

@app.post("/psd_copy/execute")
def psd_copy_exec(payload: dict):
    parent = Path(payload["parent_path"])
    suffixes = [s.strip() for s in payload.get("suffix_csv", "").split(",") if s.strip()]
    copied = 0

    for p in parent.glob("*.psd"):
        for suf in suffixes:
            if p.stem.endswith(suf):
                dst = parent / f"{p.stem}-600.psd"
                shutil.copy2(p, dst)
                copied += 1
                break

    return {"copied_count": copied}

# =========================
# MOVE + DELETE
# =========================
@app.post("/move/plan")
def move_plan(payload: dict):
    parent = Path(payload["parent_path"])
    jpg_files = []
    dirs = []

    for d in parent.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                jpg_files.append(f)
            dirs.append(d)

    parent_psd = list(parent.glob("*.psd"))

    return {
        "move_to_jpg_count": len(jpg_files),
        "delete_source_dirs_count": len(dirs),
        "move_parent_psd_count": len(parent_psd),
    }

@app.post("/move/execute")
def move_exec(payload: dict):
    parent = Path(payload["parent_path"])
    jpg_dir = parent / "jpg"
    psd_dir = parent / "psd"
    jpg_dir.mkdir(exist_ok=True)
    psd_dir.mkdir(exist_ok=True)

    moved = deleted = psd_moved = 0

    for d in parent.iterdir():
        if d.is_dir() and d.name not in ("jpg", "psd"):
            for f in d.iterdir():
                shutil.move(str(f), jpg_dir / f.name)
                moved += 1
            shutil.rmtree(d)
            deleted += 1

    for p in parent.glob("*.psd"):
        shutil.move(str(p), psd_dir / p.name)
        psd_moved += 1

    return {
        "result": {
            "moved_to_jpg_count": moved,
            "deleted_dirs_count": deleted,
            "moved_parent_psd_count": psd_moved,
        }
    }

# =========================
# TEXT FORMATTER
# =========================
MM_PATTERN = re.compile(r"(\d+(?:\.\d+)?)mm")

def mm_to_cm(text: str) -> str:
    def repl(m):
        v = float(m.group(1)) / 10
        return f"{v:.2f}".rstrip("0").rstrip(".") + "cm"
    return MM_PATTERN.sub(repl, text)

def is_title_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith("※") or s.startswith("■"):
        return False
    if "\t" in s:
        return False
    if " " in s or "　" in s:
        return False
    return True

def format_text(src: str) -> str:
    lines = src.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []

    for raw in lines:
        line = raw.rstrip()

        if not line:
            out.append("")
            continue

        if line.startswith("※"):
            out.append(line)
            continue

        if line.startswith("■"):
            out.append(line)
            continue

        if is_title_line(line):
            out.append(f"【{line}】")
            continue

        if line.startswith("保証期間"):
            continue

        if "\t" in line:
            key, val = line.split("\t", 1)
            val = val.replace("最大", "MAX")
            if key == "サイズ":
                val = val.replace("W", "幅").replace("D", "奥行").replace("H", "高さ")
            val = mm_to_cm(val)
            out.append(f"■{key}：{val}")
            continue

        out.append(line)

    while out and out[-1] == "":
        out.pop()

    return "\n".join(out)

@app.post("/text/convert")
def text_convert(payload: dict):
    result = format_text(payload.get("text", ""))
    return {"output": result}