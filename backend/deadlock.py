"""Deadlock detection and management module."""

from __future__ import annotations

from typing import Any

from backend.banker import BankersAlgorithm


def detect_deadlock(
    processes: list[str],
    resources: list[str],
    available: dict[str, int],
    allocation: dict[str, dict[str, int]],
    request: dict[str, dict[str, int]],
) -> dict[str, Any]:
    """
    Detect deadlock in a system with multi-instance resources.
    
    Uses standard deadlock detection algorithm (Shoshani & Coffman / Silberschatz):
    1. Work = Available
    2. Finish[i] = True if Allocation[i] == 0, else False
    3. Find process i where Finish[i] == False and Request[i] <= Work
    4. Work += Allocation[i], Finish[i] = True
    5. If any Finish[i] == False at the end, deadlock exists and involved processes are identified.
    
    Args:
        processes: List of process IDs.
        resources: List of resource names.
        available: Currently available resource quantities.
        allocation: Allocation matrix [process -> [resource -> count]].
        request: Request matrix [process -> [resource -> count]].
        
    Returns:
        Structured dict with deadlock_detected, involved_processes, involved_resources, explanation.
    """
    _validate_detection_inputs(processes, resources, available, allocation, request)

    work = dict(available)
    finish: dict[str, bool] = {}

    # Initialize Finish: processes with no allocated resources are initially True
    for p in processes:
        has_allocation = any(allocation[p][r] > 0 for r in resources)
        finish[p] = not has_allocation

    while True:
        found_candidate = False
        for p in processes:
            if not finish[p]:
                can_satisfy = all(request[p][r] <= work[r] for r in resources)
                if can_satisfy:
                    for r in resources:
                        work[r] += allocation[p][r]
                    finish[p] = True
                    found_candidate = True
                    break

        if not found_candidate:
            break

    deadlocked_processes = [p for p in processes if not finish[p]]
    deadlock_detected = len(deadlocked_processes) > 0

    involved_resources: list[str] = []
    if deadlock_detected:
        # Resources requested by deadlocked processes that are unsatisfied
        needed_res = set()
        for p in deadlocked_processes:
            for r in resources:
                if request[p][r] > 0:
                    needed_res.add(r)
        involved_resources = sorted(list(needed_res))
        explanation = (
            f"DEADLOCK DETECTED! Processes {deadlocked_processes} are deadlocked "
            f"waiting for resources {involved_resources}."
        )
    else:
        explanation = "No deadlock detected. All processes can eventually execute to completion."

    return {
        "deadlock_detected": deadlock_detected,
        "involved_processes": deadlocked_processes,
        "involved_resources": involved_resources,
        "explanation": explanation,
    }


def _validate_detection_inputs(
    processes: list[str],
    resources: list[str],
    available: dict[str, int],
    allocation: dict[str, dict[str, int]],
    request: dict[str, dict[str, int]],
) -> None:
    if not processes:
        raise ValueError("processes list cannot be empty")
    if not resources:
        raise ValueError("resources list cannot be empty")

    for r in resources:
        if r not in available:
            raise ValueError(f"missing resource {r} in available vector")
        if available[r] < 0:
            raise ValueError(f"available quantity cannot be negative for {r}")

    for p in processes:
        if p not in allocation:
            raise ValueError(f"missing allocation entry for process {p}")
        if p not in request:
            raise ValueError(f"missing request entry for process {p}")

        for r in resources:
            if r not in allocation[p]:
                raise ValueError(f"missing resource {r} in allocation for {p}")
            if r not in request[p]:
                raise ValueError(f"missing resource {r} in request for {p}")
            if allocation[p][r] < 0:
                raise ValueError(f"negative allocation for {p}, {r}")
            if request[p][r] < 0:
                raise ValueError(f"negative request for {p}, {r}")


class DeadlockManager:
    """Central manager for simulated deadlock and resource allocation state."""

    def __init__(self) -> None:
        self.resources = ["CPU", "Printer", "Disk", "Network"]
        self.total_resources = {"CPU": 10, "Printer": 5, "Disk": 7, "Network": 4}
        
        # Dynamic process resource matrices for simulation (starts empty)
        self.processes: list[str] = []
        self.allocation: dict[str, dict[str, int]] = {}
        self.maximum: dict[str, dict[str, int]] = {}

    def sync_with_processes(
        self, active_pids: list[str], max_demands: dict[str, dict[str, int]] | None = None
    ) -> None:
        """Synchronize deadlock resource matrices with active OS processes."""
        existing_pids = set(self.processes)
        
        # Add new processes
        for pid in active_pids:
            if pid not in existing_pids:
                self.processes.append(pid)
                self.allocation[pid] = {r: 0 for r in self.resources}
                if max_demands and pid in max_demands:
                    self.maximum[pid] = {
                        r: max(0, min(int(max_demands[pid].get(r, 0) or 0), self.total_resources[r]))
                        for r in self.resources
                    }
                else:
                    self.maximum[pid] = {r: 0 for r in self.resources}
                
        # Remove processes no longer present
        current_active = set(active_pids)
        self.processes = [p for p in self.processes if p in current_active]
        self.allocation = {p: self.allocation[p] for p in self.processes if p in self.allocation}
        self.maximum = {p: self.maximum[p] for p in self.processes if p in self.maximum}

    def get_banker(self) -> BankersAlgorithm:
        return BankersAlgorithm(
            processes=self.processes,
            resources=self.resources,
            total_resources=self.total_resources,
            allocation=self.allocation,
            maximum=self.maximum,
        )

    def get_state_summary(self) -> dict[str, Any]:
        """Return complete deadlock status dictionary."""
        if not self.processes:
            return {
                "resources": self.resources,
                "total_resources": self.total_resources,
                "available": self.total_resources,
                "allocation": {},
                "maximum": {},
                "need": {},
                "safe": True,
                "status": "SAFE",
                "explanation": "No active processes in system.",
            }

        banker = self.get_banker()
        safety = banker.check_safety()
        
        # Check for actual deadlock using detection algorithm with current Need as Request
        detection = detect_deadlock(
            processes=self.processes,
            resources=self.resources,
            available=safety["available"],
            allocation=self.allocation,
            request=safety["need"],
        )

        status = "SAFE" if safety["safe"] else ("DEADLOCK" if detection["deadlock_detected"] else "UNSAFE")

        return {
            "resources": self.resources,
            "total_resources": self.total_resources,
            "available": safety["available"],
            "allocation": self.allocation,
            "maximum": self.maximum,
            "need": safety["need"],
            "safe": safety["safe"],
            "safe_sequence": safety["safe_sequence"],
            "status": status,
            "deadlock_detected": detection["deadlock_detected"],
            "involved_processes": detection["involved_processes"],
            "involved_resources": detection["involved_resources"],
            "explanation": safety["explanation"] if safety["safe"] else detection["explanation"],
        }
