###############################################################################

from typing import Optional
from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException
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
    gvm_hostname: str = ""
    gvm_username: str = ""
    gvm_password: str = ""

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
                "execute": ["/usr/bin/nikto", "-Format", "xml", "-output", "/tmp/afdd_nikto_" + self.id + ".xml", "-host", self.url, "-maxtime", "60"], 
                "started": "",
                "ended": "",
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "Wapiti Scan",
                "dd_filename": "/tmp/afdd_wapiti_" + self.id + ".xml",
                "execute": ["/usr/bin/wapiti", "--level", "1", "--scope", "url", "--format", "xml", "--output", "/tmp/afdd_wapiti_" + self.id + ".xml", "--url", self.url], 
                "started": "",
                "ended": "",
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "SSLyze 3 Scan (JSON)",
                "dd_filename": "/tmp/afdd_sslyze_" + self.id + ".xml",
                "execute": ["/usr/bin/sslyze", "--json_out=/tmp/afdd_sslyze_" + self.id + ".xml", self.host], 
                "started": "",
                "ended": "",
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "DrHeader JSON Importer",
                "dd_filename": "/tmp/afdd_drheader_" + self.id + ".json",
                "execute": ["/bin/bash", "-c", "drheader scan single " + self.url + " --json | tee /tmp/afdd_drheader_" + self.id + ".json"], 
                "started": "",
                "ended": "",
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "ZAP Scan",
                "dd_filename": "/tmp/afdd_zap_" + self.id + ".xml",
                "execute": ["/usr/share/zaproxy/zap.sh", "-cmd", "-config", "spider.maxDepth=1", "-config", "spider.maxChildren=1", "-newsession", "/tmp/afdd_zap_ses_" + self.id, "-quickurl", self.url, "-quickout", "/tmp/afdd_zap_" + self.id + ".xml"],
                "started": "",
                "ended": "",
                "output": "",
                "imported": "",
                "error": ""
            },
            {
                "dd_name": "OpenVAS CSV",
                "dd_filename": "/tmp/afdd_openvas_" + self.id + ".csv",
                "execute": ["/usr/bin/sudo", "-u", "nobody", "/usr/local/bin/gvm-script", "--gmp-username", settings.gvm_username, "--gmp-password", settings.gvm_password, "tls", "--hostname", settings.gvm_hostname, "/opt/afdd/openvas_scan.py", self.host, "/tmp/afdd_openvas_" + self.id + ".csv"],
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

@app.post("/scantasks", status_code=status.HTTP_201_CREATED)
async def post_scantask(url: str, level: int, background_tasks: BackgroundTasks):
    try:
        scanTask = ScanTask(url, level)
        SCANTASKS.append(scanTask)
        background_tasks.add_task(scanTask.background_work)
        return {"message": "ScanTask created.", "id": scanTask.id}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@app.get("/scantasks")
def get_scantasks():
    tasks = []
    for st in SCANTASKS:
        item = {}
        item["id"] = st.id
        item["status"] = st.status
        tasks.append(item)
    return tasks

@app.get("/scantasks/{scantask_id}")
def get_scantask(scantask_id: str):
    for st in SCANTASKS:
        if st.id == scantask_id:
            return st
    raise HTTPException(status_code=404, detail="ScanTask not found")

###############################################################################
