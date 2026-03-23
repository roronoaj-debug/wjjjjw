# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:59:52 2025

@author: sharma
"""
import subprocess
import os
import shutil
import sys
from pathlib import Path

def run_drc(gds_file, testcase):
    print("Running DRC in KLayout...")

    configured_klayout = os.getenv("KLAYOUT_BIN")

    # Try to find KLayout executable
    klayout_paths = [
        configured_klayout,
        shutil.which("klayout") or "klayout",
        str(Path(sys.executable).with_name("klayout")),
        "/usr/bin/klayout",
        "/usr/local/bin/klayout",
        "/opt/klayout/bin/klayout",
    ]
    
    klayout_path = None
    for path in dict.fromkeys(klayout_paths):
        try:
            result = subprocess.run([path, "-v"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                klayout_path = path
                print(f"Found KLayout at: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if klayout_path is None:
        print("Error: KLayout executable not found. Set KLAYOUT_BIN to the klayout binary path if it is installed outside PATH.")
        return
    
    drc_script = "./PhotonicsAI/Photon/drc/drc_script.drc"
    report = "./PhotonicsAI/Photon/drc/report.lydrb"
    
    try:
        result = subprocess.run([klayout_path, "-b", "-r", drc_script, "-rd", f"input_gds={gds_file}", "-rd", f"report={report}"], capture_output=True, text=True, timeout=60)
        print(f"DRC command executed: {klayout_path} -b -r {drc_script} -rd input_gds={gds_file} -rd report={report}")
        print(f"DRC return code: {result.returncode}")
        
        if result.returncode == 0:
            print("DRC completed successfully.")
            if os.path.exists(report):
                with open(report, 'r') as f:
                    report_content = f.read()
                if report_content.strip():
                    print(f"DRC violations found: {len(report_content.splitlines())} lines in report")
                else:
                    print("DRC completed with no violations found.")
            else:
                print("Warning: DRC report file was not created.")
        else:
            print("DRC encountered errors:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("DRC timed out after 60 seconds")
    except Exception as e:
        print(f"Error running DRC: {e}")
    
    return

#run_drc()