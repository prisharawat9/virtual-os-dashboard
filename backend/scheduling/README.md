# Process Management and CPU Scheduling

This module simulates process scheduling for the Virtual OS Dashboard project. It models processes, runs classic CPU scheduling algorithms, and returns a JSON-friendly result with a Gantt chart and performance metrics.

## Algorithms Implemented

| Name | Description |
|------|-------------|
| **FCFS** | First Come First Served — non-preemptive; processes run in arrival order |
| **SJF** | Shortest Job First — non-preemptive; shortest burst time runs next |
| **PRIORITY** | Non-preemptive; lower priority number means higher priority |
| **RR** | Round Robin — preemptive; each process gets a fixed time quantum |

## Input Format

Create `Process` objects with:

- `pid` — unique process ID (string)
- `name` — display name
- `arrival_time` — when the process arrives (>= 0)
- `burst_time` — CPU time needed (> 0)
- `priority` — lower number = higher priority (default 0)
- `memory_required` — for future memory module integration (default 0)
- `state` — one of `NEW`, `READY`, `RUNNING`, `WAITING`, `TERMINATED` (default `NEW`)

## Output Format

`schedule()` returns a dictionary with:

- `algorithm` — algorithm name used
- `gantt` — list of CPU usage segments (`pid`, `start`, `end`, `duration`)
- `metrics` — per-process and average metrics
- `processes` — original process data

A Gantt entry with `"pid": null` represents CPU idle time.

## Usage

```python
from backend.scheduling import Process, schedule

processes = [
    Process("P1", "Chrome", 0, 5, 2, 200),
    Process("P2", "Python", 1, 3, 1, 150),
]

result = schedule(processes, "RR", quantum=2)
```

Supported algorithm names: `"FCFS"`, `"SJF"`, `"PRIORITY"`, `"RR"`, `"ROUND_ROBIN"`.

## Metrics

For each process:

- **Completion Time** — time when the process finishes
- **Turnaround Time** — completion time − arrival time
- **Waiting Time** — turnaround time − burst time
- **Response Time** — first time on CPU − arrival time

Aggregates:

- **Average Waiting / Turnaround / Response Time** — mean across all processes
- **CPU Utilization** — `(busy CPU time / total elapsed time) × 100`

## Running Tests

From the project root:

```bash
pip install pytest
pytest
```

## Integration Notes

This module has no Flask, database, or frontend dependencies. Member 3 can import it in `backend/app.py` and return `result` as JSON in an API route.
