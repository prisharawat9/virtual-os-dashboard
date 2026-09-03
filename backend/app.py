"""Flask Web Application and REST API for Virtual OS Dashboard."""

from __future__ import annotations

import os
import sys
from typing import Any

# Ensure project root directory is in Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, render_template, request, send_from_directory

from backend.deadlock import DeadlockManager
from backend.scheduling import Process, schedule


class SimulatedOS:
    """Central state manager for the simulated operating system."""

    def __init__(self) -> None:
        # Processes list starts empty; user creates processes via UI or API
        self.processes: list[Process] = []
        self.next_pid_counter = 1
        
        # Deadlock Manager instance (starts empty)
        self.deadlock_mgr = DeadlockManager()
        self.deadlock_mgr.sync_with_processes([])

        # Member 2 Memory Module Integration State Placeholder
        self.memory_state: dict[str, Any] = {
            "total_mb": 1024,
            "used_mb": 0,
            "free_mb": 1024,
            "utilization_pct": 0.0,
            "allocation_map": [],
            "integrated": False,
            "message": "Memory management module awaiting Member 2 integration.",
        }

        # Member 2 Paging Module Integration State Placeholder
        self.paging_state: dict[str, Any] = {
            "page_faults": 0,
            "page_hits": 0,
            "total_references": 0,
            "hit_ratio_pct": 0.0,
            "frame_count": 4,
            "frames": [],
            "supported_algorithms": ["FIFO", "LRU", "OPTIMAL"],
            "integrated": False,
            "message": "Paging & replacement module awaiting Member 2 integration.",
        }

        self.cpu_ticks = 0
        self.cpu_usage_pct = 0.0


    def generate_unique_pid(self) -> str:
        """Generate next authoritative PID sequentially (P1, P2, P3...)."""
        count = len(self.processes) + 1
        while True:
            candidate = f"P{count}"
            if not any(p.pid == candidate for p in self.processes):
                return candidate
            count += 1

    def update_metrics(self) -> None:
        """Synchronize process matrices and compute dynamic memory metrics."""
        # Synchronize deadlock processes
        self.deadlock_mgr.sync_with_processes([p.pid for p in self.processes])
        
        # Recalculate dynamic memory metrics based on active processes
        used_mem = sum(p.memory_required for p in self.processes)
        total_mem = max(1024, used_mem + 256)
        free_mem = max(0, total_mem - used_mem)
        util_pct = round((used_mem / total_mem) * 100, 1) if total_mem > 0 else 0.0

        # Dynamic allocation map based on active processes
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4"]
        alloc_map = []
        current_offset = 0
        for idx, p in enumerate(self.processes):
            if p.memory_required > 0:
                alloc_map.append({
                    "pid": p.pid,
                    "start": current_offset,
                    "size": p.memory_required,
                    "color": colors[idx % len(colors)],
                })
                current_offset += p.memory_required

        if free_mem > 0 and self.processes:
            alloc_map.append({
                "pid": None,
                "start": current_offset,
                "size": free_mem,
                "color": "#374151",
            })

        self.memory_state["total_mb"] = total_mem
        self.memory_state["used_mb"] = used_mem
        self.memory_state["free_mb"] = free_mem
        self.memory_state["utilization_pct"] = util_pct
        self.memory_state["allocation_map"] = alloc_map

    def get_full_state(self) -> dict[str, Any]:
        """Return the aggregated central OS state snapshot."""
        self.update_metrics()
        deadlock_info = self.deadlock_mgr.get_state_summary()

        return {
            "cpu": {
                "usage_pct": round(self.cpu_usage_pct, 1) if self.processes else 0.0,
                "ticks": self.cpu_ticks if self.processes else 0,
                "active_processes": len(self.processes),
            },
            "memory": self.memory_state,
            "paging": self.paging_state,
            "processes": [p.to_dict() for p in self.processes],
            "deadlock": deadlock_info,
            "system_status": "NORMAL" if deadlock_info["safe"] else ("DEADLOCK" if deadlock_info["deadlock_detected"] else "WARNING"),
        }


# Path setup for frontend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
os_sim = SimulatedOS()


@app.route("/")
def index():
    """Serve main web dashboard."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path: str):
    """Serve frontend static assets (CSS, JS)."""
    return send_from_directory(FRONTEND_DIR, path)


@app.route("/api/state", methods=["GET"])
def get_state():
    """Return complete simulated OS state snapshot as JSON."""
    return jsonify(os_sim.get_full_state())


@app.route("/api/processes", methods=["GET"])
def get_processes():
    """Return list of active processes."""
    return jsonify([p.to_dict() for p in os_sim.processes])


@app.route("/api/processes", methods=["POST"])
def create_process():
    """
    Create a new simulated process.
    Expected JSON: {name, arrival_time, burst_time, priority, memory_required, [pid], [maximum_resources]}
    """
    data = request.get_json() or {}
    
    try:
        raw_pid = str(data.get("pid", "")).strip()
        if raw_pid:
            if any(p.pid == raw_pid for p in os_sim.processes):
                return jsonify({"error": f"process with PID '{raw_pid}' already exists"}), 400
            pid = raw_pid
        else:
            pid = os_sim.generate_unique_pid()

        name = str(data.get("name", "")).strip() or pid
        arrival_time = int(data.get("arrival_time", 0))
        burst_time = int(data.get("burst_time", 1))
        priority = int(data.get("priority", 0))
        memory_required = int(data.get("memory_required", 0))
        max_resources = data.get("maximum_resources")

        new_process = Process(
            pid=pid,
            name=name,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority,
            memory_required=memory_required,
            state="READY",
        )
        
        os_sim.processes.append(new_process)
        
        # Synchronize deadlock manager with process and optional max claims
        max_demands_dict = {pid: max_resources} if isinstance(max_resources, dict) else None
        os_sim.deadlock_mgr.sync_with_processes(
            [p.pid for p in os_sim.processes], max_demands=max_demands_dict
        )
        
        return jsonify({
            "message": f"Process '{pid}' created successfully.",
            "process": new_process.to_dict(),
        }), 201

    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"invalid payload: {str(err)}"}), 400



@app.route("/api/processes/<pid>", methods=["DELETE"])
def delete_process(pid: str):
    """Delete a process by PID."""
    matching = [p for p in os_sim.processes if p.pid == pid]
    if not matching:
        return jsonify({"error": f"process '{pid}' not found"}), 404

    os_sim.processes = [p for p in os_sim.processes if p.pid != pid]
    os_sim.deadlock_mgr.sync_with_processes([p.pid for p in os_sim.processes])
    
    return jsonify({
        "message": f"Process '{pid}' deleted.",
        "processes": [p.to_dict() for p in os_sim.processes],
    })


@app.route("/api/scheduling/run", methods=["POST"])
def run_scheduling():
    """
    Run CPU scheduling simulation calling Member 1's scheduler module.
    Expected JSON: {algorithm: "FCFS"|"SJF"|"PRIORITY"|"RR", quantum: int}
    """
    if not os_sim.processes:
        return jsonify({"error": "No processes available to schedule"}), 400

    data = request.get_json() or {}
    algorithm = str(data.get("algorithm", "FCFS")).strip().upper()
    quantum = int(data.get("quantum", 2))

    try:
        # Direct call to Member 1's schedule module
        result = schedule(os_sim.processes, algorithm=algorithm, quantum=quantum)
        
        # Compute CPU ticks and utilization from actual scheduling activity
        gantt = result.get("gantt", [])
        if gantt:
            os_sim.cpu_ticks += gantt[-1]["end"]
        os_sim.cpu_usage_pct = float(result.get("metrics", {}).get("cpu_utilization", 0.0))

        return jsonify(result)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"Scheduling error: {str(err)}"}), 500


@app.route("/api/deadlock/state", methods=["GET"])
def get_deadlock_state():
    """Return current deadlock module state."""
    return jsonify(os_sim.deadlock_mgr.get_state_summary())


@app.route("/api/deadlock/safety", methods=["POST"])
def run_safety_check():
    """Run Banker's Safety Algorithm."""
    try:
        banker = os_sim.deadlock_mgr.get_banker()
        result = banker.check_safety()
        return jsonify(result)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400


@app.route("/api/deadlock/request", methods=["POST"])
def process_resource_request():
    """
    Run Banker's Resource Request Algorithm.
    Expected JSON: {process_id: "P1", request: {CPU: 1, Printer: 0, ...}}
    """
    data = request.get_json() or {}
    pid = str(data.get("process_id", "")).strip()
    req_dict = data.get("request", {})

    if not pid:
        return jsonify({"error": "process_id is required"}), 400
    if not isinstance(req_dict, dict):
        return jsonify({"error": "request must be a dictionary of resource quantities"}), 400

    try:
        banker = os_sim.deadlock_mgr.get_banker()
        req_clean = {r: int(val) for r, val in req_dict.items()}
        result = banker.request_resources(pid, req_clean)
        
        # If granted, persist the allocation change in deadlock manager
        if result.get("granted"):
            os_sim.deadlock_mgr.allocation = banker.allocation

        return jsonify(result)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400


@app.route("/api/deadlock/detect", methods=["POST"])
def run_deadlock_detection():
    """Run Deadlock Detection algorithm."""
    try:
        summary = os_sim.deadlock_mgr.get_state_summary()
        return jsonify({
            "deadlock_detected": summary["deadlock_detected"],
            "involved_processes": summary["involved_processes"],
            "involved_resources": summary["involved_resources"],
            "explanation": summary["explanation"],
            "status": summary["status"],
        })
    except ValueError as err:
        return jsonify({"error": str(err)}), 400


# Member 2 Integration Endpoints (Memory & Paging)
@app.route("/api/memory/state", methods=["GET"])
def get_memory_state():
    """Integration point for Member 2 memory state."""
    return jsonify(os_sim.memory_state)


@app.route("/api/paging/state", methods=["GET"])
def get_paging_state():
    """Integration point for Member 2 paging state."""
    return jsonify(os_sim.paging_state)


if __name__ == "__main__":
    print("Starting Virtual OS Dashboard server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
