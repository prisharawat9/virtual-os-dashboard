"""Metrics calculation for scheduling results."""

from __future__ import annotations

from typing import Any

from .models import GanttEntry, Process


def _round2(value: float) -> float:
    return round(value, 2)


def calculate_metrics(
    processes: list[Process],
    completion_times: dict[str, int],
    response_times: dict[str, int],
    gantt: list[GanttEntry],
) -> dict[str, Any]:
    """
    Calculate per-process and aggregate scheduling metrics.

    Args:
        processes: Original process list in input order.
        completion_times: Mapping of pid to completion time.
        response_times: Mapping of pid to first-response time.
        gantt: Gantt chart entries from the simulation.

    Returns:
        A JSON-friendly metrics dictionary.
    """
    process_metrics: list[dict[str, Any]] = []
    total_waiting = 0
    total_turnaround = 0
    total_response = 0

    for process in processes:
        completion_time = completion_times[process.pid]
        turnaround_time = completion_time - process.arrival_time
        waiting_time = turnaround_time - process.burst_time
        response_time = response_times[process.pid]

        process_metrics.append(
            {
                "pid": process.pid,
                "completion_time": completion_time,
                "turnaround_time": turnaround_time,
                "waiting_time": waiting_time,
                "response_time": response_time,
            }
        )

        total_waiting += waiting_time
        total_turnaround += turnaround_time
        total_response += response_time

    count = len(processes)
    total_elapsed = max((entry.end for entry in gantt), default=0)
    busy_time = sum(entry.duration for entry in gantt if entry.pid is not None)

    if total_elapsed == 0:
        cpu_utilization = 0.0
    else:
        cpu_utilization = (busy_time / total_elapsed) * 100

    return {
        "processes": process_metrics,
        "average_waiting_time": _round2(total_waiting / count),
        "average_turnaround_time": _round2(total_turnaround / count),
        "average_response_time": _round2(total_response / count),
        "cpu_utilization": _round2(cpu_utilization),
    }
