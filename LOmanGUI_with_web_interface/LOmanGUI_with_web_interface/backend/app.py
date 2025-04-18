import sys
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# Import existing LastOasis management functionality
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import LastOasisManager
import admin_writer
from mod_checker import add_new_mod_ids, read_json, update_mods_info

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='loman_web.log',
    filemode='a'
)
logger = logging.getLogger('LOManagerWeb')

# Initialize FastAPI app
app = FastAPI(
    title="Last Oasis Manager API",
    description="API for managing Last Oasis dedicated servers",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
config = {}
try:
    with open("config.json", 'r') as file:
        config = json.load(file)
except Exception as e:
    logger.error(f"Error loading configuration: {e}")

# Initialize LastOasisManager with config
LastOasisManager.update_config()

# Define API models
class ServerStatus(BaseModel):
    server_id: str
    status: str
    tile_name: Optional[str] = None
    player_count: Optional[int] = None
    uptime: Optional[str] = None

class ModInfo(BaseModel):
    mod_id: str
    name: str
    version: str
    status: str
    last_update: Optional[str] = None

class ServerAction(BaseModel):
    server_id: str
    action: str

class AdminMessage(BaseModel):
    message: str
    server_ids: List[str] = []

# API endpoints
@app.get("/")
async def root():
    """API root with basic info"""
    return {
        "app": "Last Oasis Manager API",
        "version": "1.0.0", 
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/servers", response_model=List[ServerStatus])
async def get_servers():
    """Get status of all server tiles"""
    servers = []
    try:
        for i in range(config.get("tile_num", 0)):
            server_id = f"{config.get('identifier', 'server')}{i}"
            tile_name = LastOasisManager.tile_tracker.get_tile_name(server_id, server_id)
            
            # Check if process is running (simplified)
            status = "offline"
            if i < len(LastOasisManager.processes) and LastOasisManager.processes[i] is not None:
                if LastOasisManager.processes[i].is_alive():
                    status = "online"
            
            servers.append(ServerStatus(
                server_id=server_id,
                status=status,
                tile_name=tile_name,
                player_count=0,  # Would need to implement player count tracking
                uptime="Unknown"  # Would need to implement uptime tracking
            ))
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return servers

@app.post("/servers/action")
async def server_action(action: ServerAction, background_tasks: BackgroundTasks):
    """Perform action on server (start, stop, restart)"""
    try:
        server_id = action.server_id
        action_type = action.action.lower()
        
        # Extract tile_id from server_id
        if server_id.startswith(config.get('identifier', '')):
            tile_id = int(server_id[len(config.get('identifier', '')):])
        else:
            raise HTTPException(status_code=400, detail="Invalid server ID format")
        
        if action_type == "start":
            # Start in background to not block API
            background_tasks.add_task(LastOasisManager.start_single_process, tile_id)
            return {"status": "success", "message": f"Starting server {server_id}"}
            
        elif action_type == "stop":
            if tile_id < len(LastOasisManager.stop_events) and LastOasisManager.stop_events[tile_id] is not None:
                LastOasisManager.stop_events[tile_id].set()
                return {"status": "success", "message": f"Stopping server {server_id}"}
            else:
                raise HTTPException(status_code=404, detail="Server not found or not running")
                
        elif action_type == "restart":
            admin_writer.write("Server restart initiated from web interface", config["folder_path"], tile_id)
            if tile_id < len(LastOasisManager.stop_events) and LastOasisManager.stop_events[tile_id] is not None:
                LastOasisManager.stop_events[tile_id].set()
                # Start in background after brief delay
                async def delayed_start():
                    await asyncio.sleep(5)
                    LastOasisManager.start_single_process(tile_id)
                background_tasks.add_task(delayed_start)
                return {"status": "success", "message": f"Restarting server {server_id}"}
            else:
                raise HTTPException(status_code=404, detail="Server not found or not running")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action_type}")
            
    except Exception as e:
        logger.error(f"Error performing server action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mods", response_model=List[ModInfo])
async def get_mods():
    """Get list of all mods and their status"""
    try:
        mods = []
        mod_ids = config.get('mods', '').split(',')
        mods_info = read_json('mods_info.json')
        
        for mod_id in mod_ids:
            if not mod_id:
                continue
                
            mod_info_str = mods_info.get(mod_id, "")
            
            # Default values
            name = f'Mod {mod_id}'
            version = 'Unknown'
            last_update = 'Unknown'
            
            # Parse mod info
            if mod_info_str:
                parts = mod_info_str.split('\n')
                if len(parts) >= 1:
                    version = parts[0]
                if len(parts) >= 3:
                    last_update = parts[2]
            
            mods.append(ModInfo(
                mod_id=mod_id,
                name=name,
                version=version,
                status="Active",
                last_update=last_update
            ))
            
        return mods
    except Exception as e:
        logger.error(f"Error getting mods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/message")
async def send_admin_message(message: AdminMessage):
    """Send admin message to servers"""
    try:
        if not message.server_ids:
            # Send to all servers if none specified
            for i in range(config["tile_num"]):
                admin_writer.write(message.message, config["folder_path"], i)
            return {"status": "success", "message": "Message sent to all servers"}
        else:
            # Send to specified servers
            for server_id in message.server_ids:
                if server_id.startswith(config.get('identifier', '')):
                    tile_id = int(server_id[len(config.get('identifier', '')):])
                    admin_writer.write(message.message, config["folder_path"], tile_id)
            return {"status": "success", "message": f"Message sent to servers: {', '.join(message.server_ids)}"}
    except Exception as e:
        logger.error(f"Error sending admin message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/{server_id}")
async def get_logs(server_id: str, lines: int = Query(100, gt=0, lt=1000)):
    """Get recent logs for a specific server"""
    try:
        if server_id.startswith(config.get('identifier', '')):
            tile_id = int(server_id[len(config.get('identifier', '')):])
            
            # Construct log file path
            log_folder = os.path.join(config["folder_path"].replace("Binaries\\Win64\\", ""), "Saved\\Logs")
            log_files = sorted(Path(log_folder).glob(f"*{server_id}*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not log_files:
                return {"logs": "No log files found"}
                
            # Get most recent log file
            log_file = log_files[0]
            
            # Read last N lines
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-lines:]
                
            return {"log_file": str(log_file), "logs": recent_logs}
        else:
            raise HTTPException(status_code=400, detail="Invalid server ID format")
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

