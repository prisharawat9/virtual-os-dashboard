"""
Virtual Memory & Page Replacement Algorithms Module.

Implements standard page replacement algorithms:
- FIFO (First-In, First-Out)
- LRU (Least Recently Used)
- Optimal (Belady's Optimal Page Replacement)
"""

from typing import Dict, List, Union, Optional, Any


def parse_reference_string(ref_input: Union[str, List[Union[int, str]]]) -> List[Union[int, str]]:
    """
    Parses strings (comma/space-separated) or lists into a sanitized reference string list.
    """
    if isinstance(ref_input, list):
        parsed = []
        for item in ref_input:
            if isinstance(item, int):
                parsed.append(item)
            else:
                s = str(item).strip()
                if s:
                    try:
                        parsed.append(int(s))
                    except ValueError:
                        parsed.append(s)
        return parsed
    elif isinstance(ref_input, str):
        # Replace commas with spaces and split
        cleaned = ref_input.replace(",", " ").split()
        parsed = []
        for item in cleaned:
            try:
                parsed.append(int(item))
            except ValueError:
                parsed.append(item)
        return parsed
    else:
        raise TypeError("Reference string must be a list or a string.")


def _validate_inputs(reference_string: Union[str, List[Union[int, str]]], frame_count: int) -> tuple[List[Union[int, str]], int]:
    """Helper to validate reference string and frame count inputs."""
    if not isinstance(frame_count, int) or frame_count <= 0:
        raise ValueError(f"Number of frames must be a positive integer greater than 0 (got {frame_count}).")

    parsed_ref = parse_reference_string(reference_string)
    if not parsed_ref:
        raise ValueError("Reference string cannot be empty.")

    return parsed_ref, frame_count


def _build_result_dict(
    algorithm: str,
    ref_str: List[Union[int, str]],
    frame_count: int,
    page_faults: int,
    page_hits: int,
    frame_history: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Builds a standardized return dictionary for page replacement algorithm results."""
    total_refs = len(ref_str)
    fault_rate = round((page_faults / total_refs) * 100, 2) if total_refs > 0 else 0.0
    hit_rate = round((page_hits / total_refs) * 100, 2) if total_refs > 0 else 0.0

    return {
        "algorithm": algorithm,
        "reference_string": ref_str,
        "frame_count": frame_count,
        "total_references": total_refs,
        "page_faults": page_faults,
        "page_hits": page_hits,
        "page_fault_rate": fault_rate,
        "page_hit_rate": hit_rate,
        "frame_history": frame_history,
    }


def fifo(reference_string: Union[str, List[Union[int, str]]], frame_count: int) -> Dict[str, Any]:
    """
    First-In-First-Out (FIFO) Page Replacement Algorithm.
    Replaces the page that has been in memory the longest when a page fault occurs and frames are full.
    """
    ref_str, frames_num = _validate_inputs(reference_string, frame_count)

    frames: List[Optional[Union[int, str]]] = [None] * frames_num
    fifo_queue: List[Union[int, str]] = []  # Tracks insertion order of pages in frames
    history: List[Dict[str, Any]] = []
    faults = 0
    hits = 0

    for idx, page in enumerate(ref_str, start=1):
        if page in frames:
            hits += 1
            status = "Hit"
            replaced_page = None
            reason = f"Page {page} is already in frame {frames.index(page)}."
        else:
            faults += 1
            status = "Fault"
            if None in frames:
                # Fill first empty slot
                empty_idx = frames.index(None)
                frames[empty_idx] = page
                fifo_queue.append(page)
                replaced_page = None
                reason = f"Page {page} loaded into empty frame slot {empty_idx}."
            else:
                # Frames full -> replace page at head of FIFO queue
                victim_page = fifo_queue.pop(0)
                victim_idx = frames.index(victim_page)
                frames[victim_idx] = page
                fifo_queue.append(page)
                replaced_page = victim_page
                reason = f"Page fault occurred. Replaced oldest page ({victim_page}) with page {page}."

        history.append({
            "step": idx,
            "page": page,
            "frames": list(frames),
            "status": status,
            "replaced_page": replaced_page,
            "reason": reason,
        })

    return _build_result_dict("FIFO", ref_str, frames_num, faults, hits, history)


def lru(reference_string: Union[str, List[Union[int, str]]], frame_count: int) -> Dict[str, Any]:
    """
    Least Recently Used (LRU) Page Replacement Algorithm.
    Replaces the page that has not been accessed for the longest time when a page fault occurs and frames are full.
    """
    ref_str, frames_num = _validate_inputs(reference_string, frame_count)

    frames: List[Optional[Union[int, str]]] = [None] * frames_num
    last_accessed: Dict[Union[int, str], int] = {}  # page -> step index
    history: List[Dict[str, Any]] = []
    faults = 0
    hits = 0

    for step_idx, page in enumerate(ref_str, start=1):
        if page in frames:
            hits += 1
            status = "Hit"
            replaced_page = None
            reason = f"Page {page} hit in frame {frames.index(page)}."
            last_accessed[page] = step_idx
        else:
            faults += 1
            status = "Fault"
            if None in frames:
                empty_idx = frames.index(None)
                frames[empty_idx] = page
                replaced_page = None
                reason = f"Page {page} loaded into empty frame slot {empty_idx}."
            else:
                # Find page in frames with smallest last_accessed value
                victim_page = min(frames, key=lambda p: last_accessed.get(p, -1))
                victim_idx = frames.index(victim_page)
                frames[victim_idx] = page
                replaced_page = victim_page
                reason = f"Page fault occurred. Replaced least recently used page ({victim_page}) with page {page}."

            last_accessed[page] = step_idx

        history.append({
            "step": step_idx,
            "page": page,
            "frames": list(frames),
            "status": status,
            "replaced_page": replaced_page,
            "reason": reason,
        })

    return _build_result_dict("LRU", ref_str, frames_num, faults, hits, history)


def optimal(reference_string: Union[str, List[Union[int, str]]], frame_count: int) -> Dict[str, Any]:
    """
    Optimal Page Replacement Algorithm (Belady's Optimal).
    Replaces the page whose next usage is farthest in the future (or never used again).
    """
    ref_str, frames_num = _validate_inputs(reference_string, frame_count)

    frames: List[Optional[Union[int, str]]] = [None] * frames_num
    history: List[Dict[str, Any]] = []
    faults = 0
    hits = 0

    for step_idx, page in enumerate(ref_str, start=1):
        if page in frames:
            hits += 1
            status = "Hit"
            replaced_page = None
            reason = f"Page {page} hit in frame {frames.index(page)}."
        else:
            faults += 1
            status = "Fault"
            if None in frames:
                empty_idx = frames.index(None)
                frames[empty_idx] = page
                replaced_page = None
                reason = f"Page {page} loaded into empty frame slot {empty_idx}."
            else:
                future_refs = ref_str[step_idx:]  # remaining page references
                victim_page = None
                farthest_distance = -1

                for loaded_page in frames:
                    if loaded_page not in future_refs:
                        # Page never used again -> highest priority victim
                        victim_page = loaded_page
                        break
                    else:
                        next_use = future_refs.index(loaded_page)
                        if next_use > farthest_distance:
                            farthest_distance = next_use
                            victim_page = loaded_page

                victim_idx = frames.index(victim_page)
                frames[victim_idx] = page
                replaced_page = victim_page
                reason = f"Page fault occurred. Replaced page ({victim_page}) (farthest in future/never used) with page {page}."

        history.append({
            "step": step_idx,
            "page": page,
            "frames": list(frames),
            "status": status,
            "replaced_page": replaced_page,
            "reason": reason,
        })

    return _build_result_dict("Optimal", ref_str, frames_num, faults, hits, history)
