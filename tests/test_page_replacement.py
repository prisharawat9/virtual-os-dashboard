"""
Unit tests for Virtual Memory & Page Replacement Algorithms:
- FIFO
- LRU
- Optimal
- Edge Cases & Input Validation
"""

import pytest
from backend.memory.page_replacement import (
    fifo,
    lru,
    optimal,
    parse_reference_string,
)


def test_parse_reference_string():
    assert parse_reference_string("1 2 3 4 1 2") == [1, 2, 3, 4, 1, 2]
    assert parse_reference_string("1, 2, 3, 4, 1, 2") == [1, 2, 3, 4, 1, 2]
    assert parse_reference_string([1, "2", 3, "4"]) == [1, 2, 3, 4]
    assert parse_reference_string(["P1", "P2", "P1"]) == ["P1", "P2", "P1"]


def test_fifo_page_replacement():
    ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    res = fifo(ref_str, frame_count=3)

    assert res["algorithm"] == "FIFO"
    assert res["total_references"] == 10
    assert res["page_faults"] == 8
    assert res["page_hits"] == 2
    assert res["page_fault_rate"] == 80.0
    assert res["page_hit_rate"] == 20.0

    # Step 4: Page 4 replaces 1
    step4 = res["frame_history"][3]
    assert step4["page"] == 4
    assert step4["status"] == "Fault"
    assert step4["replaced_page"] == 1
    assert step4["frames"] == [4, 2, 3]

    # Step 8: Page 1 hit
    step8 = res["frame_history"][7]
    assert step8["page"] == 1
    assert step8["status"] == "Hit"
    assert step8["replaced_page"] is None


def test_lru_page_replacement():
    ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    res = lru(ref_str, frame_count=3)

    assert res["algorithm"] == "LRU"
    assert res["total_references"] == 10
    assert res["page_faults"] == 8
    assert res["page_hits"] == 2

    # Verify frame history step format
    for step_data in res["frame_history"]:
        assert "step" in step_data
        assert "page" in step_data
        assert "frames" in step_data
        assert "status" in step_data


def test_optimal_page_replacement():
    ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    res = optimal(ref_str, frame_count=3)

    assert res["algorithm"] == "Optimal"
    assert res["total_references"] == 10
    assert res["page_faults"] == 6
    assert res["page_hits"] == 4
    assert res["page_fault_rate"] == 60.0
    assert res["page_hit_rate"] == 40.0

    # Optimal performs better than FIFO and LRU on this reference string
    assert res["page_faults"] < fifo(ref_str, 3)["page_faults"]


def test_single_frame():
    ref_str = [1, 2, 1, 3, 1]
    res_fifo = fifo(ref_str, frame_count=1)
    # Total references = 5. All page switches cause faults.
    assert res_fifo["page_faults"] == 5
    assert res_fifo["page_hits"] == 0


def test_frame_count_larger_than_unique_pages():
    ref_str = [1, 2, 3, 1, 2, 3]
    res_fifo = fifo(ref_str, frame_count=5)
    # Unique pages = 3. Initial 3 references fault, subsequent references hit.
    assert res_fifo["page_faults"] == 3
    assert res_fifo["page_hits"] == 3


def test_repeated_pages():
    ref_str = [7, 7, 7, 7, 7]
    res = lru(ref_str, frame_count=3)
    assert res["page_faults"] == 1
    assert res["page_hits"] == 4


def test_edge_cases_and_validation():
    # Frame count <= 0
    with pytest.raises(ValueError):
        fifo([1, 2, 3], frame_count=0)

    with pytest.raises(ValueError):
        lru([1, 2, 3], frame_count=-2)

    # Empty reference string
    with pytest.raises(ValueError):
        optimal("", frame_count=3)

    with pytest.raises(ValueError):
        fifo([], frame_count=3)
