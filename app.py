from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import shutil
import json
import mimetypes
import base64

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Pydantic models
class MoveRequest(BaseModel):
    src_path: str
    dest_dir: str

class RenameRequest(BaseModel):
    src_path: str
    new_name: str

class SaveConfigRequest(BaseModel):
    config: dict
    path: Optional[str] = None

# Helpers
def get_file_info(path):
    mime_type, _ = mimetypes.guess_type(path)
    return {
        "name": os.path.basename(path),
        "full_path": path,
        "type": mime_type or "unknown",
        "size": os.path.getsize(path)
    }

# Endpoints
@app.get("/files")
def list_files(dir_path: str):
    if not os.path.isdir(dir_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    files = [get_file_info(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return files

@app.get("/files/count")
def count_files(dir_path: str):
    if not os.path.isdir(dir_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    return {"count": len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])}

@app.post("/files/move")
def move_file(request: MoveRequest):
    if not os.path.isfile(request.src_path):
        raise HTTPException(status_code=400, detail="Source file does not exist")
    if not os.path.isdir(request.dest_dir):
        raise HTTPException(status_code=400, detail="Destination directory does not exist")
    new_path = os.path.join(request.dest_dir, os.path.basename(request.src_path))
    shutil.move(request.src_path, new_path)
    return {"success": True, "new_path": new_path}

@app.post("/files/rename")
def rename_file(request: RenameRequest):
    if not os.path.isfile(request.src_path):
        raise HTTPException(status_code=400, detail="File does not exist")
    dir_path = os.path.dirname(request.src_path)
    new_path = os.path.join(dir_path, request.new_name)
    os.rename(request.src_path, new_path)
    return {"success": True, "new_path": new_path}

@app.get("/files/preview")
def display_file(file_path: str):
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="File does not exist")
    mime_type, _ = mimetypes.guess_type(file_path)
    file_type = mime_type.split('/')[0] if mime_type else "unknown"
    if file_type in ["image", "text"]:
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return {"type": file_type, "preview_data": f"data:{mime_type};base64,{data}"}
    return {"type": "other", "name": os.path.basename(file_path)}

@app.get("/config")
def load_config(path: Optional[str] = None):
    config_path = path or "config.json"
    if not os.path.isfile(config_path):
        raise HTTPException(status_code=404, detail="Config not found")
    with open(config_path, "r") as f:
        return json.load(f)

@app.post("/config")
def save_config(request: SaveConfigRequest):
    config_path = request.path or "config.json"
    with open(config_path, "w") as f:
        json.dump(request.config, f, indent=4)
    return {"success": True, "path": config_path}
