"""Banker's Algorithm implementation for deadlock avoidance."""

from __future__ import annotations

from typing import Any


class BankersAlgorithm:
    """
    Implements Banker's Safety and Resource Request algorithms.
    """

    def __init__(
        self,
        processes: list[str],
        resources: list[str],
        total_resources: dict[str, int],
        allocation: dict[str, dict[str, int]],
        maximum: dict[str, dict[str, int]],
    ) -> None:
        """
        Initialize Banker's Algorithm with processes, resources, total resources,
        allocation matrix, and maximum matrix.
        """
        self.processes = list(processes)
        self.resources = list(resources)
        self.total_resources = dict(total_resources)
        self.allocation = {p: dict(alloc) for p, alloc in allocation.items()}
        self.maximum = {p: dict(max_res) for p, max_res in maximum.items()}
        
        self.validate_state()

    def validate_state(self) -> None:
        """Validate inputs and matrix consistency."""
        if not isinstance(self.processes, list) or not self.processes:
            raise ValueError("processes list cannot be empty")
        
        if len(set(self.processes)) != len(self.processes):
            raise ValueError("duplicate process IDs in process list")

        if not isinstance(self.resources, list) or not self.resources:
            raise ValueError("resources list cannot be empty")
            
        if len(set(self.resources)) != len(self.resources):
            raise ValueError("duplicate resource IDs in resource list")

        # Validate total resources
        for r in self.resources:
            if r not in self.total_resources:
                raise ValueError(f"missing total count for resource: {r}")
            if self.total_resources[r] < 0:
                raise ValueError(f"total resource quantity cannot be negative for {r}")

        # Check process matrices
        for p in self.processes:
            if p not in self.allocation:
                raise ValueError(f"missing allocation matrix row for process: {p}")
            if p not in self.maximum:
                raise ValueError(f"missing maximum matrix row for process: {p}")

            for r in self.resources:
                if r not in self.allocation[p]:
                    raise ValueError(f"missing resource {r} in allocation for process {p}")
                if r not in self.maximum[p]:
                    raise ValueError(f"missing resource {r} in maximum for process {p}")

                alloc_val = self.allocation[p][r]
                max_val = self.maximum[p][r]

                if alloc_val < 0:
                    raise ValueError(f"negative allocation for process {p}, resource {r}")
                if max_val < 0:
                    raise ValueError(f"negative maximum requirement for process {p}, resource {r}")
                if alloc_val > max_val:
                    raise ValueError(
                        f"allocation ({alloc_val}) exceeds maximum ({max_val}) for process {p}, resource {r}"
                    )

        # Validate total allocated vs total capacity
        for r in self.resources:
            sum_alloc = sum(self.allocation[p][r] for p in self.processes)
            if sum_alloc > self.total_resources[r]:
                raise ValueError(
                    f"total allocated {r} ({sum_alloc}) exceeds total available capacity ({self.total_resources[r]})"
                )

    def calculate_need(self) -> dict[str, dict[str, int]]:
        """Calculate Need matrix: Need[i][j] = Maximum[i][j] - Allocation[i][j]."""
        need: dict[str, dict[str, int]] = {}
        for p in self.processes:
            need[p] = {}
            for r in self.resources:
                need[p][r] = self.maximum[p][r] - self.allocation[p][r]
        return need

    def calculate_available(self) -> dict[str, int]:
        """Calculate currently Available vector: Available[j] = Total[j] - Sum(Allocation[i][j])."""
        available: dict[str, int] = {}
        for r in self.resources:
            allocated_total = sum(self.allocation[p][r] for p in self.processes)
            available[r] = self.total_resources[r] - allocated_total
        return available

    def check_safety(self) -> dict[str, Any]:
        """
        Execute Banker's Safety Algorithm.
        
        Returns:
            Structured dictionary with safe (bool), safe_sequence (list),
            available, allocation, maximum, need, finished_processes, explanation.
        """
        need = self.calculate_need()
        available = self.calculate_available()
        work = dict(available)
        finish = {p: False for p in self.processes}
        safe_sequence: list[str] = []

        while len(safe_sequence) < len(self.processes):
            found_candidate = False

            for p in self.processes:
                if not finish[p]:
                    # Check if Need[p] <= Work
                    can_fulfill = all(need[p][r] <= work[r] for r in self.resources)
                    if can_fulfill:
                        # Simulate process completion and resource release
                        for r in self.resources:
                            work[r] += self.allocation[p][r]
                        finish[p] = True
                        safe_sequence.append(p)
                        found_candidate = True
                        break

            if not found_candidate:
                break

        is_safe = len(safe_sequence) == len(self.processes)
        finished_processes = [p for p, is_done in finish.items() if is_done]

        if is_safe:
            seq_str = " -> ".join(safe_sequence)
            explanation = f"System is in a SAFE state. Safe sequence: {seq_str}"
        else:
            unfinished = [p for p, is_done in finish.items() if not is_done]
            explanation = (
                f"System is in an UNSAFE state. Processes {unfinished} cannot finish "
                f"with available resources."
            )

        return {
            "safe": is_safe,
            "safe_sequence": safe_sequence,
            "available": available,
            "allocation": self.allocation,
            "maximum": self.maximum,
            "need": need,
            "finished_processes": finished_processes,
            "explanation": explanation,
        }

    def request_resources(
        self, process_id: str, request: dict[str, int]
    ) -> dict[str, Any]:
        """
        Execute Banker's Resource Request Algorithm.
        
        Args:
            process_id: PID making the request.
            request: Dict mapping resource names to requested amounts.
            
        Returns:
            Structured dictionary with granted (bool), safe (bool),
            safe_sequence (list), state matrices, explanation.
        """
        if process_id not in self.processes:
            raise ValueError(f"unknown process ID: {process_id}")

        for r, req_val in request.items():
            if r not in self.resources:
                raise ValueError(f"unknown resource ID: {r}")
            if req_val < 0:
                raise ValueError(f"request amount cannot be negative for {r}")

        need = self.calculate_need()
        available = self.calculate_available()

        # Check Request <= Need
        for r in self.resources:
            req_amt = request.get(r, 0)
            if req_amt > need[process_id][r]:
                return {
                    "granted": False,
                    "reason": f"Request for {r} ({req_amt}) exceeds process {process_id}'s Need ({need[process_id][r]})",
                    "safe": False,
                    "explanation": f"Request denied: process {process_id} asked for more than its claimed maximum need.",
                }

        # Check Request <= Available
        for r in self.resources:
            req_amt = request.get(r, 0)
            if req_amt > available[r]:
                return {
                    "granted": False,
                    "reason": f"Request for {r} ({req_amt}) exceeds currently Available ({available[r]})",
                    "safe": False,
                    "explanation": f"Request denied: insufficient resources currently available.",
                }

        # Tentatively allocate resources
        temp_allocation = {p: dict(alloc) for p, alloc in self.allocation.items()}
        for r in self.resources:
            req_amt = request.get(r, 0)
            temp_allocation[process_id][r] += req_amt

        # Create temporary Banker instance to check safety
        temp_banker = BankersAlgorithm(
            processes=self.processes,
            resources=self.resources,
            total_resources=self.total_resources,
            allocation=temp_allocation,
            maximum=self.maximum,
        )

        safety_result = temp_banker.check_safety()

        if safety_result["safe"]:
            # Commit allocation to current state if safe
            self.allocation = temp_allocation
            return {
                "granted": True,
                "safe": True,
                "safe_sequence": safety_result["safe_sequence"],
                "available": temp_banker.calculate_available(),
                "allocation": self.allocation,
                "maximum": self.maximum,
                "need": temp_banker.calculate_need(),
                "explanation": f"Request GRANTED for {process_id}. System remains in a safe state.",
            }
        else:
            return {
                "granted": False,
                "reason": "Granting request leads to an UNSAFE state",
                "safe": False,
                "safe_sequence": [],
                "available": available,
                "allocation": self.allocation,
                "maximum": self.maximum,
                "need": need,
                "explanation": f"Request DENIED for {process_id}: allocating requested resources would result in an unsafe state.",
            }
