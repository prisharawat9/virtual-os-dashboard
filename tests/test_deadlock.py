"""Tests for Banker's Algorithm and Deadlock Detection modules."""

from __future__ import annotations

import pytest

from backend.banker import BankersAlgorithm
from backend.deadlock import DeadlockManager, detect_deadlock


def test_banker_safe_state():
    processes = ["P1", "P2", "P3"]
    resources = ["CPU", "Printer"]
    total = {"CPU": 10, "Printer": 5}
    allocation = {
        "P1": {"CPU": 2, "Printer": 1},
        "P2": {"CPU": 3, "Printer": 2},
        "P3": {"CPU": 2, "Printer": 1},
    }
    maximum = {
        "P1": {"CPU": 4, "Printer": 2},
        "P2": {"CPU": 5, "Printer": 3},
        "P3": {"CPU": 4, "Printer": 2},
    }

    banker = BankersAlgorithm(processes, resources, total, allocation, maximum)
    result = banker.check_safety()

    assert result["safe"] is True
    assert isinstance(result["safe_sequence"], list)
    assert len(result["safe_sequence"]) == 3
    assert set(result["safe_sequence"]) == {"P1", "P2", "P3"}
    assert result["need"] == {
        "P1": {"CPU": 2, "Printer": 1},
        "P2": {"CPU": 2, "Printer": 1},
        "P3": {"CPU": 2, "Printer": 1},
    }
    assert result["available"] == {"CPU": 3, "Printer": 1}


def test_banker_unsafe_state():
    processes = ["P1", "P2"]
    resources = ["CPU"]
    total = {"CPU": 5}
    allocation = {
        "P1": {"CPU": 3},
        "P2": {"CPU": 2},
    }
    maximum = {
        "P1": {"CPU": 5},
        "P2": {"CPU": 4},
    }

    banker = BankersAlgorithm(processes, resources, total, allocation, maximum)
    result = banker.check_safety()

    assert result["safe"] is False
    assert result["safe_sequence"] == []
    assert "UNSAFE" in result["explanation"]


def test_resource_request_granted():
    processes = ["P1", "P2"]
    resources = ["CPU", "Printer"]
    total = {"CPU": 10, "Printer": 10}
    allocation = {
        "P1": {"CPU": 1, "Printer": 1},
        "P2": {"CPU": 2, "Printer": 2},
    }
    maximum = {
        "P1": {"CPU": 4, "Printer": 4},
        "P2": {"CPU": 5, "Printer": 5},
    }

    banker = BankersAlgorithm(processes, resources, total, allocation, maximum)
    req_result = banker.request_resources("P1", {"CPU": 1, "Printer": 1})

    assert req_result["granted"] is True
    assert req_result["safe"] is True
    assert banker.allocation["P1"] == {"CPU": 2, "Printer": 2}


def test_resource_request_denied_due_to_available():
    processes = ["P1", "P2"]
    resources = ["CPU"]
    total = {"CPU": 5}
    allocation = {
        "P1": {"CPU": 2},
        "P2": {"CPU": 2},
    }
    maximum = {
        "P1": {"CPU": 4},
        "P2": {"CPU": 4},
    }

    banker = BankersAlgorithm(processes, resources, total, allocation, maximum)
    # Available CPU is 1. P1 requests 2.
    req_result = banker.request_resources("P1", {"CPU": 2})

    assert req_result["granted"] is False
    assert "exceeds currently Available" in req_result["reason"]
    # State should remain unchanged
    assert banker.allocation["P1"] == {"CPU": 2}


def test_resource_request_denied_due_to_unsafe():
    processes = ["P1", "P2"]
    resources = ["CPU"]
    total = {"CPU": 5}
    allocation = {
        "P1": {"CPU": 2},
        "P2": {"CPU": 2},
    }
    maximum = {
        "P1": {"CPU": 5},
        "P2": {"CPU": 5},
    }

    banker = BankersAlgorithm(processes, resources, total, allocation, maximum)
    # Available CPU is 1. P1 requests 1.
    # If granted, P1 allocation=3, P2 allocation=2, Available=0.
    # P1 Need=2, P2 Need=3. Neither can finish -> Unsafe!
    req_result = banker.request_resources("P1", {"CPU": 1})

    assert req_result["granted"] is False
    assert req_result["safe"] is False
    assert banker.allocation["P1"] == {"CPU": 2}


def test_deadlock_detection_scenario():
    processes = ["P1", "P2"]
    resources = ["R1", "R2"]
    available = {"R1": 0, "R2": 0}
    allocation = {
        "P1": {"R1": 1, "R2": 0},
        "P2": {"R1": 0, "R2": 1},
    }
    request = {
        "P1": {"R1": 0, "R2": 1},
        "P2": {"R1": 1, "R2": 0},
    }

    result = detect_deadlock(processes, resources, available, allocation, request)

    assert result["deadlock_detected"] is True
    assert set(result["involved_processes"]) == {"P1", "P2"}
    assert set(result["involved_resources"]) == {"R1", "R2"}


def test_deadlock_detection_no_deadlock():
    processes = ["P1", "P2"]
    resources = ["R1", "R2"]
    available = {"R1": 1, "R2": 1}
    allocation = {
        "P1": {"R1": 1, "R2": 0},
        "P2": {"R1": 0, "R2": 1},
    }
    request = {
        "P1": {"R1": 0, "R2": 1},
        "P2": {"R1": 0, "R2": 0},
    }

    result = detect_deadlock(processes, resources, available, allocation, request)

    assert result["deadlock_detected"] is False
    assert result["involved_processes"] == []


def test_banker_validation_errors():
    processes = ["P1"]
    resources = ["CPU"]
    total = {"CPU": 5}
    allocation = {"P1": {"CPU": 6}}
    maximum = {"P1": {"CPU": 5}}

    with pytest.raises(ValueError, match="exceeds maximum"):
        BankersAlgorithm(processes, resources, total, allocation, maximum)

    with pytest.raises(ValueError, match="unknown process ID"):
        banker = BankersAlgorithm(["P1"], ["CPU"], {"CPU": 5}, {"P1": {"CPU": 2}}, {"P1": {"CPU": 4}})
        banker.request_resources("P99", {"CPU": 1})


def test_deadlock_manager_sync():
    manager = DeadlockManager()
    summary = manager.get_state_summary()

    assert "resources" in summary
    assert "available" in summary
    assert summary["safe"] is True

    manager.sync_with_processes(["P1", "P2", "P5"])
    assert "P5" in manager.processes
    assert "P3" not in manager.processes
