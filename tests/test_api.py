"""Tests for Flask API endpoints and integration."""

from __future__ import annotations

import json
import pytest

from backend.app import app, os_sim
from backend.scheduling import Process


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset os_sim state to fresh empty OS before each test
        os_sim.processes = []
        os_sim.next_pid_counter = 1
        os_sim.deadlock_mgr.processes = []
        os_sim.deadlock_mgr.allocation = {}
        os_sim.deadlock_mgr.maximum = {}
        yield client


def test_initial_state_is_empty(client):
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["processes"]) == 0
    assert data["cpu"]["active_processes"] == 0
    assert data["cpu"]["usage_pct"] == 0.0
    assert data["deadlock"]["safe"] is True


def test_create_and_delete_process_with_auto_pid(client):
    # Create first process without specifying PID
    p1_data = {
        "name": "Browser",
        "arrival_time": 0,
        "burst_time": 5,
        "priority": 1,
        "memory_required": 256,
        "maximum_resources": {"CPU": 3, "Printer": 1, "Disk": 2, "Network": 1},
    }
    res = client.post("/api/processes", json=p1_data)
    assert res.status_code == 201
    proc1 = res.get_json()["process"]
    assert proc1["pid"] == "P1"
    assert proc1["name"] == "Browser"

    # Create second process
    p2_data = {
        "name": "Database",
        "arrival_time": 1,
        "burst_time": 3,
        "priority": 2,
        "memory_required": 128,
    }
    res2 = client.post("/api/processes", json=p2_data)
    assert res2.status_code == 201
    proc2 = res2.get_json()["process"]
    assert proc2["pid"] == "P2"

    # Verify process list
    res_list = client.get("/api/processes")
    p_list = res_list.get_json()
    assert len(p_list) == 2
    assert p_list[0]["pid"] == "P1"
    assert p_list[1]["pid"] == "P2"

    # Delete P1
    res_del = client.delete("/api/processes/P1")
    assert res_del.status_code == 200
    assert len(res_del.get_json()["processes"]) == 1


def test_invalid_process_input(client):
    # Invalid burst time <= 0
    bad_proc = {"name": "BadProc", "burst_time": -1}
    res = client.post("/api/processes", json=bad_proc)
    assert res.status_code == 400

    # Delete non-existent process
    res_del = client.delete("/api/processes/NON_EXISTENT")
    assert res_del.status_code == 404


def test_scheduling_empty_processes_returns_error(client):
    # Running scheduling when 0 processes exist
    res = client.post("/api/scheduling/run", json={"algorithm": "FCFS"})
    assert res.status_code == 400
    assert "No processes available" in res.get_json()["error"]


def test_scheduling_user_created_processes(client):
    # Create two processes
    client.post("/api/processes", json={"name": "JobA", "arrival_time": 0, "burst_time": 4, "priority": 1})
    client.post("/api/processes", json={"name": "JobB", "arrival_time": 1, "burst_time": 2, "priority": 2})

    for algo in ["FCFS", "SJF", "PRIORITY", "RR"]:
        res = client.post("/api/scheduling/run", json={"algorithm": algo, "quantum": 2})
        assert res.status_code == 200
        data = res.get_json()
        assert data["algorithm"] == (algo if algo != "ROUND_ROBIN" else "RR")
        assert len(data["processes"]) == 2
        assert "gantt" in data
        assert "metrics" in data


def test_banker_and_deadlock_on_user_processes(client):
    # Create process P1 and P2 with specific claims
    client.post("/api/processes", json={
        "name": "P1",
        "maximum_resources": {"CPU": 4, "Printer": 2, "Disk": 2, "Network": 1}
    })
    client.post("/api/processes", json={
        "name": "P2",
        "maximum_resources": {"CPU": 3, "Printer": 2, "Disk": 3, "Network": 2}
    })

    # Safety check endpoint
    res_safe = client.post("/api/deadlock/safety")
    assert res_safe.status_code == 200
    assert res_safe.get_json()["safe"] is True

    # Resource request endpoint
    res_req = client.post("/api/deadlock/request", json={
        "process_id": "P1",
        "request": {"CPU": 1, "Printer": 0, "Disk": 0, "Network": 0}
    })
    assert res_req.status_code == 200
    assert res_req.get_json()["granted"] is True

    # Deadlock detection endpoint
    res_det = client.post("/api/deadlock/detect")
    assert res_det.status_code == 200
    assert res_det.get_json()["deadlock_detected"] is False
