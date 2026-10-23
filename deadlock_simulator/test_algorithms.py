"""
Quick verification test script for deadlock detection algorithms
"""

from algorithms.single_instance import SingleInstanceDetector
from algorithms.multi_instance import MultiInstanceDetector
from presets import SINGLE_INSTANCE_PRESETS, MULTI_INSTANCE_PRESETS

def test_single_instance():
    print("=== Testing Single Instance Deadlock Detector ===")
    preset = SINGLE_INSTANCE_PRESETS["Classic 3-Process Circular Deadlock"]
    detector = SingleInstanceDetector(
        processes=preset["processes"],
        resources=preset["resources"],
        allocations=preset["allocations"],
        requests=preset["requests"]
    )
    result = detector.detect_cycles()
    print("3-Process Deadlock Result:", result["is_deadlocked"])
    print("Deadlocked processes:", result["deadlocked_processes"])
    print("WFG Cycles:", result["wfg_cycles"])
    assert result["is_deadlocked"] == True
    assert set(result["deadlocked_processes"]) == {"P1", "P2", "P3"}

    # Test victim suggestion
    victim_info = detector.suggest_victim()
    print("Suggested victim:", victim_info["victim"])
    assert victim_info["victim"] in {"P1", "P2", "P3"}

    # Test termination
    new_detector = detector.terminate_process(victim_info["victim"])
    new_result = new_detector.detect_cycles()
    print("After terminating victim, is deadlocked?:", new_result["is_deadlocked"])
    assert new_result["is_deadlocked"] == False

    # Test Safe preset
    safe_preset = SINGLE_INSTANCE_PRESETS["Safe System (Linear Dependency - No Cycle)"]
    safe_detector = SingleInstanceDetector(
        processes=safe_preset["processes"],
        resources=safe_preset["resources"],
        allocations=safe_preset["allocations"],
        requests=safe_preset["requests"]
    )
    safe_res = safe_detector.detect_cycles()
    print("Safe preset is deadlocked?:", safe_res["is_deadlocked"])
    assert safe_res["is_deadlocked"] == False
    print("Single Instance Tests Passed!\n")

def test_multi_instance():
    print("=== Testing Multi Instance Deadlock Detector ===")
    # 1. Silberschatz deadlock preset
    dl_preset = MULTI_INSTANCE_PRESETS["Silberschatz OS Textbook Deadlock (Sec 8.6)"]
    dl_detector = MultiInstanceDetector(
        process_names=dl_preset["processes"],
        resource_names=dl_preset["resources"],
        available=dl_preset["available"],
        allocation=dl_preset["allocation"],
        request=dl_preset["request"]
    )
    dl_result = dl_detector.detect_deadlock()
    print("Silberschatz deadlock is deadlocked?:", dl_result["is_deadlocked"])
    print("Deadlocked processes:", dl_result["deadlocked_processes"])
    print("Safe sequence:", dl_result["safe_sequence"])
    assert dl_result["is_deadlocked"] == True
    assert set(dl_result["deadlocked_processes"]) == {"P1", "P2", "P3", "P4"}
    assert dl_result["safe_sequence"] == ["P0"]

    # 2. Silberschatz safe preset
    safe_preset = MULTI_INSTANCE_PRESETS["Silberschatz Safe Example (All Finish)"]
    safe_detector = MultiInstanceDetector(
        process_names=safe_preset["processes"],
        resource_names=safe_preset["resources"],
        available=safe_preset["available"],
        allocation=safe_preset["allocation"],
        request=safe_preset["request"]
    )
    safe_res = safe_detector.detect_deadlock()
    print("Silberschatz safe is deadlocked?:", safe_res["is_deadlocked"])
    print("Safe sequence:", safe_res["safe_sequence"])
    assert safe_res["is_deadlocked"] == False
    assert len(safe_res["safe_sequence"]) == 5

    # 3. Cycle exists but not deadlocked
    cycle_safe = MULTI_INSTANCE_PRESETS["Cycle Exists but NO Deadlock (Multi-Instance)"]
    cs_detector = MultiInstanceDetector(
        process_names=cycle_safe["processes"],
        resource_names=cycle_safe["resources"],
        available=cycle_safe["available"],
        allocation=cycle_safe["allocation"],
        request=cycle_safe["request"]
    )
    cs_res = cs_detector.detect_deadlock()
    print("Cycle exists but not deadlocked result:", cs_res["is_deadlocked"])
    assert cs_res["is_deadlocked"] == False

    print("Multi Instance Tests Passed!\n")

if __name__ == "__main__":
    test_single_instance()
    test_multi_instance()
