"""
Memory Allocation Module.

Simulates dynamic memory allocation algorithms used by operating systems:
- First Fit
- Best Fit
- Worst Fit
- Process Deallocation & Free Block Coalescing
"""

from typing import Dict, List, Optional, Any


class MemoryBlock:
    """
    Represents a contiguous block of physical memory.
    """

    def __init__(self, start: int, size: int, is_allocated: bool = False, process_id: Optional[str] = None):
        self.start = start
        self.size = size
        self.end = start + size
        self.is_allocated = is_allocated
        self.process_id = process_id if is_allocated else None

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of the block."""
        return {
            "start": self.start,
            "end": self.end,
            "size": self.size,
            "is_allocated": self.is_allocated,
            "process_id": self.process_id,
        }

    def __repr__(self) -> str:
        status = f"Allocated({self.process_id})" if self.is_allocated else "Free"
        return f"<Block [{self.start}:{self.end}] {self.size}MB {status}>"


class MemoryManager:
    """
    Manages physical memory partitioning, process allocation, and deallocation.
    """

    def __init__(self, total_memory: int = 1024):
        if total_memory <= 0:
            raise ValueError("Total memory must be greater than 0.")
        self.total_memory = total_memory
        self.blocks: List[MemoryBlock] = [MemoryBlock(start=0, size=total_memory, is_allocated=False)]

    def reset(self, total_memory: Optional[int] = None) -> None:
        """Resets the memory manager to an empty initial state."""
        if total_memory is not None:
            if total_memory <= 0:
                raise ValueError("Total memory must be greater than 0.")
            self.total_memory = total_memory
        self.blocks = [MemoryBlock(start=0, size=self.total_memory, is_allocated=False)]

    def get_allocated_processes(self) -> Dict[str, int]:
        """Returns a mapping of process_id -> total allocated memory size."""
        allocated: Dict[str, int] = {}
        for block in self.blocks:
            if block.is_allocated and block.process_id:
                allocated[block.process_id] = allocated.get(block.process_id, 0) + block.size
        return allocated

    def get_used_memory(self) -> int:
        """Calculates total used memory in MB."""
        return sum(block.size for block in self.blocks if block.is_allocated)

    def get_free_memory(self) -> int:
        """Calculates total free memory in MB."""
        return sum(block.size for block in self.blocks if not block.is_allocated)

    def get_external_fragmentation(self, requested_size: int = 0) -> int:
        """
        Calculates total free memory that cannot satisfy a request because it is split into smaller non-contiguous blocks.
        If requested_size is 0, returns total free memory across all free blocks if there is more than 1 free block.
        """
        free_blocks = [b.size for b in self.blocks if not b.is_allocated]
        if not free_blocks:
            return 0
        max_free_block = max(free_blocks)
        total_free = sum(free_blocks)
        if requested_size > 0:
            if requested_size <= total_free and requested_size > max_free_block:
                return total_free
            return 0
        return total_free - max_free_block if len(free_blocks) > 1 else 0

    def get_state_dict(self, success: bool = True, message: str = "") -> Dict[str, Any]:
        """Builds a structured dictionary representation of the current memory state."""
        used = self.get_used_memory()
        free = self.get_free_memory()
        utilization = round((used / self.total_memory) * 100, 2) if self.total_memory > 0 else 0.0

        return {
            "success": success,
            "message": message,
            "total_memory": self.total_memory,
            "used_memory": used,
            "free_memory": free,
            "utilization_percentage": utilization,
            "external_fragmentation": self.get_external_fragmentation(),
            "allocated_processes": self.get_allocated_processes(),
            "blocks": [block.to_dict() for block in self.blocks],
        }

    def _find_target_block(self, size: int, algorithm: str) -> Optional[int]:
        """
        Finds the index of the target free block based on the selected allocation strategy.
        Algorithms: 'first_fit', 'best_fit', 'worst_fit'.
        """
        algo = algorithm.lower().strip()
        candidate_indices = [
            idx for idx, block in enumerate(self.blocks) if not block.is_allocated and block.size >= size
        ]

        if not candidate_indices:
            return None

        if algo in ("first_fit", "firstfit", "first fit"):
            return candidate_indices[0]

        elif algo in ("best_fit", "bestfit", "best fit"):
            # Select free block with minimum size >= requested size
            return min(candidate_indices, key=lambda idx: (self.blocks[idx].size, idx))

        elif algo in ("worst_fit", "worstfit", "worst fit"):
            # Select free block with maximum size >= requested size
            return max(candidate_indices, key=lambda idx: (self.blocks[idx].size, -idx))

        else:
            raise ValueError(f"Unknown allocation algorithm: '{algorithm}'. Choose from 'first_fit', 'best_fit', or 'worst_fit'.")

    def allocate(self, process_id: str, size: int, algorithm: str = "first_fit") -> Dict[str, Any]:
        """
        Allocates memory to a process using First Fit, Best Fit, or Worst Fit.
        Returns a structured dictionary of the outcome and updated memory state.
        """
        # Input Validations
        if not process_id or not str(process_id).strip():
            return self.get_state_dict(success=False, message="Process ID must not be empty.")

        process_id = str(process_id).strip()

        if size <= 0:
            return self.get_state_dict(success=False, message=f"Memory size requested must be greater than 0 MB (got {size} MB).")

        if size > self.total_memory:
            return self.get_state_dict(
                success=False,
                message=f"Process {process_id} requested {size} MB, which exceeds total memory ({self.total_memory} MB).",
            )

        # Check if process_id is already allocated
        if process_id in self.get_allocated_processes():
            return self.get_state_dict(
                success=False,
                message=f"Process ID '{process_id}' is already present in memory.",
            )

        try:
            target_idx = self._find_target_block(size, algorithm)
        except ValueError as err:
            return self.get_state_dict(success=False, message=str(err))

        if target_idx is None:
            total_free = self.get_free_memory()
            if total_free >= size:
                msg = f"Allocation failed for process {process_id} ({size} MB). External fragmentation detected: {total_free} MB free but no single block is large enough."
            else:
                msg = f"Allocation failed for process {process_id} ({size} MB). Insufficient free memory ({total_free} MB available)."
            return self.get_state_dict(success=False, message=msg)

        target_block = self.blocks[target_idx]

        if target_block.size == size:
            target_block.is_allocated = True
            target_block.process_id = process_id
        else:
            # Split block into allocated segment and remaining free segment
            allocated_block = MemoryBlock(
                start=target_block.start, size=size, is_allocated=True, process_id=process_id
            )
            remaining_block = MemoryBlock(
                start=target_block.start + size,
                size=target_block.size - size,
                is_allocated=False,
            )
            self.blocks[target_idx] = allocated_block
            self.blocks.insert(target_idx + 1, remaining_block)

        algo_formatted = algorithm.replace("_", " ").title()
        return self.get_state_dict(
            success=True,
            message=f"Process {process_id} ({size} MB) successfully allocated using {algo_formatted}.",
        )

    def deallocate(self, process_id: str) -> Dict[str, Any]:
        """
        Deallocates memory for a specified process ID and merges adjacent free blocks (coalescing).
        """
        if not process_id or not str(process_id).strip():
            return self.get_state_dict(success=False, message="Process ID must not be empty.")

        process_id = str(process_id).strip()
        found = False

        for block in self.blocks:
            if block.is_allocated and block.process_id == process_id:
                block.is_allocated = False
                block.process_id = None
                found = True

        if not found:
            return self.get_state_dict(
                success=False, message=f"Deallocation failed. Process '{process_id}' not found in memory."
            )

        self._coalesce()
        return self.get_state_dict(
            success=True, message=f"Process '{process_id}' successfully deallocated and adjacent free blocks merged."
        )

    def _coalesce(self) -> None:
        """Merges contiguous unallocated blocks into single larger free blocks."""
        if not self.blocks:
            return

        coalesced: List[MemoryBlock] = []
        current = self.blocks[0]

        for next_block in self.blocks[1:]:
            if not current.is_allocated and not next_block.is_allocated:
                # Merge next_block into current
                current = MemoryBlock(
                    start=current.start,
                    size=current.size + next_block.size,
                    is_allocated=False,
                )
            else:
                coalesced.append(current)
                current = next_block

        coalesced.append(current)
        self.blocks = coalesced


# Standalone function interfaces for modular import
def allocate_first_fit(memory_manager: MemoryManager, process_id: str, size: int) -> Dict[str, Any]:
    """Allocates memory using First Fit algorithm."""
    return memory_manager.allocate(process_id, size, algorithm="first_fit")


def allocate_best_fit(memory_manager: MemoryManager, process_id: str, size: int) -> Dict[str, Any]:
    """Allocates memory using Best Fit algorithm."""
    return memory_manager.allocate(process_id, size, algorithm="best_fit")


def allocate_worst_fit(memory_manager: MemoryManager, process_id: str, size: int) -> Dict[str, Any]:
    """Allocates memory using Worst Fit algorithm."""
    return memory_manager.allocate(process_id, size, algorithm="worst_fit")


def deallocate_process(memory_manager: MemoryManager, process_id: str) -> Dict[str, Any]:
    """Deallocates memory for the given process ID."""
    return memory_manager.deallocate(process_id)


def reset_memory(memory_manager: MemoryManager, total_size: Optional[int] = None) -> Dict[str, Any]:
    """Resets memory manager to an initial unallocated state."""
    memory_manager.reset(total_size)
    return memory_manager.get_state_dict(success=True, message="Memory reset successfully.")
