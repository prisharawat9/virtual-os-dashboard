# Virtual OS Dashboard

A comprehensive, simulated Operating System dashboard built in Python (Flask) and modern HTML5/CSS3/JavaScript. This application simulates CPU scheduling, deadlock avoidance/detection, and provides ready integration hooks for memory management and page replacement.

---

## 🌟 Project Purpose

The **Virtual OS Dashboard** simulates internal Operating System kernel behaviors and visualizes key algorithms in real-time, including:
- **CPU Scheduling**: FCFS, SJF, Priority Scheduling, and Round Robin (RR) with dynamic Gantt charts and timing metrics.
- **Deadlock Management**: Banker's Safety Algorithm, Resource Request Algorithm, Multi-instance Resource Deadlock Detection, and interactive Resource Allocation Graphs (RAG).
- **Process Control**: Real-time process creation, state inspection, and termination.
- **Memory & Paging Hooks**: Structured state representations and UI layouts ready for Member 2's memory module integration.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies

Ensure Python 3.8+ is installed. Install the minimum required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the Application

Start the Flask web server from the project root:

```bash
python backend/app.py
```

Open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

### 3. Run Automated Tests

To run the complete unit test suite (covering CPU scheduling, Banker's Algorithm, deadlock detection, and Flask REST API endpoints):

```bash
python -m pytest
```

---

## 📱 Dashboard Navigation & Pages

1. **Dashboard Home**: Summary metrics (CPU Usage, Memory, Active Processes, Page Faults, Deadlock Status), real-time CPU canvas activity monitor, system event log, and active process overview.
2. **Processes**: Full process control panel to create new simulated processes (`POST /api/processes`) and delete processes (`DELETE /api/processes/<pid>`).
3. **Scheduling**: Interactive CPU scheduling simulator. Select from FCFS, SJF, Priority, or Round Robin, specify time quantum, and view animated visual Gantt charts and performance metrics.
4. **Memory (Member 2 Hook)**: Displays RAM allocation map, memory utilization, and structured placeholders ready for Member 2's allocation/deallocation algorithms.
5. **Paging (Member 2 Hook)**: Displays page frame status, page hits/faults, and placeholders ready for FIFO, LRU, and Optimal page replacement algorithms.
6. **Deadlocks (Member 3 Main Feature)**: Complete deadlock control center featuring Banker's Safety algorithm, Resource Request simulation, Deadlock Detection, and an interactive SVG Resource Allocation Graph (RAG).

---

## 🔒 Deadlock Module & Banker's Algorithm

- **Generic Resources**: Manages dynamic resource vectors (`CPU`, `Printer`, `Disk`, `Network`).
- **Programmatic Need Matrix**: Computes `Need[i][j] = Maximum[i][j] - Allocation[i][j]`.
- **Banker's Safety Algorithm**: Finds a safe process execution sequence (`P1 -> P2 -> P3 -> ...`) or identifies an unsafe state.
- **Resource Request Algorithm**: Evaluates whether `Request <= Need` and `Request <= Available`, tentatively allocates resources, runs safety verification, and GRANTS or DENIES requests.
- **Deadlock Detection**: Analyzes multi-instance resource allocation to detect active deadlocks and identify involved processes and resources.
- **Resource Allocation Graph (RAG)**: Renders process nodes, resource nodes, allocation arrows (Resource -> Process), and request arrows (Process -> Resource) dynamically.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves main web dashboard (`frontend/index.html`) |
| `GET` | `/api/state` | Returns aggregated central OS state snapshot (CPU, Memory, Processes, Deadlocks) |
| `GET` | `/api/processes` | Returns list of active processes |
| `POST` | `/api/processes` | Creates a new process (`pid`, `name`, `arrival_time`, `burst_time`, `priority`, `memory_required`) |
| `DELETE` | `/api/processes/<pid>` | Deletes a process by PID |
| `POST` | `/api/scheduling/run` | Executes Member 1's scheduling dispatcher (`FCFS`, `SJF`, `PRIORITY`, `RR`) |
| `GET` | `/api/deadlock/state` | Returns deadlock matrices, available resources, and safety status |
| `POST` | `/api/deadlock/safety` | Executes Banker's Safety Algorithm |
| `POST` | `/api/deadlock/request` | Executes Banker's Resource Request Algorithm (`process_id`, `request`) |
| `POST` | `/api/deadlock/detect` | Executes Deadlock Detection algorithm |
| `GET` | `/api/memory/state` | Integration endpoint for Member 2 memory state |
| `GET` | `/api/paging/state` | Integration endpoint for Member 2 paging state |

---

## 🧩 Member 2 Integration Guide

To connect Member 2's memory allocation and page replacement modules:
1. Place Member 2's code in `backend/memory.py` and `backend/paging.py`.
2. In `backend/app.py`, update `SimulatedOS.memory_state` and `SimulatedOS.paging_state` inside `update_metrics()`.
3. Connect `GET /api/memory/state`, `POST /api/memory/allocate`, `GET /api/paging/state`, and `POST /api/paging/simulate` to Member 2's functions.
4. The frontend (`frontend/dashboard.js`) will automatically consume updated memory and paging data without requiring UI redesign.
