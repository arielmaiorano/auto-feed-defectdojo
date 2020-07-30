###############################################################################

from typing import Optional
from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import status
from pydantic import BaseSettings

import uuid
from datetime import datetime
from urllib.parse import urlparse
import io
import subprocess
import requests

###############################################################################

class Settings(BaseSettings):
    defect_dojo_url: str = ""
    defect_dojo_token: str = ""
    defect_dojo_engagement_id: int = 0

###############################################################################

settings = Settings()
app = FastAPI()

###############################################################################

SCANTASKS = []

###############################################################################

class ScanTask:

    def __init__(self, url, level):
        self.url = url
        self.level = level
        self.id = str(uuid.uuid4())
        self.created_time = datetime.now()
        self.host = urlparse(self.url).hostname
        self.commands = [
            {
                "dd_name": "Nmap Scan",
                "dd_filename": "/tmp/afdd_nmap_" + self.id + ".xml",
                "execute": ["/usr/bin/nmap", "-Pn", "-F", "-oX", "/tmp/afdd_nmap_" + self.id + ".xml", self.host], 
                "started": "", 
                "ended": "", 
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "Nikto Scan",
                "dd_filename": "/tmp/afdd_nikto_" + self.id + ".xml",
                "execute": ["/usr/bin/nikto", "-Format", "xml", "-output", "/tmp/afdd_nikto_" + self.id + ".xml", "-host", self.url, "-maxtime", "10"], 
                "started": "", 
                "ended": "", 
                "output": "",
                "imported": "",
                "error": ""
            },
        ]
        self.status = "initialized"

    def background_work(self):
        self.status = "running commands"
        for command in self.commands:
            command["started"] = datetime.now()
            try:
                # execute command
                proc = subprocess.Popen(command["execute"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    command["output"] += line
                # import in dd
                url = settings.defect_dojo_url + "/api/v2/import-scan/"
                #headers = {"content-type": 'application/json',
                #        "Authorization": "Token " + settings.defect_dojo_token}
                headers = {"Authorization": "Token " + settings.defect_dojo_token}
                data = {"engagement": settings.defect_dojo_engagement_id, "scan_type": command["dd_name"]}
                files = {'file': open(command["dd_filename"], 'rb')}
                r = requests.post(url, headers=headers, data=data, files=files)
                command["imported"] = str(r.status_code) + ": " + str(r.text)
            except Exception as ex:
                command["error"] = str(ex)
            finally:
                command["ended"] = datetime.now()
        self.status = "finished"

###############################################################################

@app.post("/scantask", status_code=status.HTTP_201_CREATED)
async def post_scantask(url: str, level: int, background_tasks: BackgroundTasks):
    scanTask = ScanTask(url, level)
    SCANTASKS.append(scanTask)
    background_tasks.add_task(scanTask.background_work)
    return {"message": "ScanTask created.", "id": scanTask.id}

@app.get("/scantasks")
def get_scantasks():
    tasks = []
    for st in SCANTASKS:
        item = {}
        item["id"] = st.id
        item["created_time"] = st.created_time
        item["status"] = st.status
        tasks.append(item)
    return tasks

@app.get("/scantask/{scantask_id}")
def get_scantask(scantask_id: str):
    for st in SCANTASKS:
        if st.id == scantask_id:
            item = {}
            item["id"] = st.id
            item["created_time"] = st.created_time
            item["status"] = st.status
            item["commands"] = st.commands
            return item
    return {"message": "ScanTask not found."}


###############################################################################
