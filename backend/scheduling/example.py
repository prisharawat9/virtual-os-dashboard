"""Demonstration script for Round Robin scheduling."""

from backend.scheduling import Process, schedule


def main() -> None:
    processes = [
        Process("P1", "Chrome", 0, 5, 2, 200),
        Process("P2", "Python", 1, 3, 1, 150),
        Process("P3", "Terminal", 2, 4, 3, 100),
        Process("P4", "Editor", 4, 2, 2, 120),
    ]

    result = schedule(processes, "RR", quantum=2)

    print(f"Algorithm: {result['algorithm']}")
    print("\nGantt chart:")
    for entry in result["gantt"]:
        label = entry["pid"] if entry["pid"] is not None else "IDLE"
        print(
            f"  {label}: {entry['start']} -> {entry['end']} "
            f"(duration={entry['duration']})"
        )

    metrics = result["metrics"]
    print(f"\nAverage waiting time: {metrics['average_waiting_time']}")
    print(f"Average turnaround time: {metrics['average_turnaround_time']}")
    print(f"Average response time: {metrics['average_response_time']}")
    print(f"CPU utilization: {metrics['cpu_utilization']}%")


if __name__ == "__main__":
    main()
