"""
Pre-configured scenarios and educational presets for Deadlock Detection Simulator
"""

from typing import Dict, Any

SINGLE_INSTANCE_PRESETS: Dict[str, Dict[str, Any]] = {
    "Classic 3-Process Circular Deadlock": {
        "description": "Textbook 3-process circular wait. P1 holds R1 and waits for R2. P2 holds R2 and waits for R3. P3 holds R3 and waits for R1. A closed cycle forms in the Wait-For Graph.",
        "processes": ["P1", "P2", "P3"],
        "resources": ["R1", "R2", "R3"],
        "allocations": [("R1", "P1"), ("R2", "P2"), ("R3", "P3")],
        "requests": [("P1", "R2"), ("P2", "R3"), ("P3", "R1")],
    },
    "Dining Philosophers (5 Philosophers)": {
        "description": "Dijkstra's classic Dining Philosophers problem where all 5 philosophers simultaneously pick up their left fork (chopstick) and wait indefinitely for their right fork.",
        "processes": ["Phil_0", "Phil_1", "Phil_2", "Phil_3", "Phil_4"],
        "resources": ["Fork_0", "Fork_1", "Fork_2", "Fork_3", "Fork_4"],
        "allocations": [
            ("Fork_0", "Phil_0"),
            ("Fork_1", "Phil_1"),
            ("Fork_2", "Phil_2"),
            ("Fork_3", "Phil_3"),
            ("Fork_4", "Phil_4")
        ],
        "requests": [
            ("Phil_0", "Fork_1"),
            ("Phil_1", "Fork_2"),
            ("Phil_2", "Fork_3"),
            ("Phil_3", "Fork_4"),
            ("Phil_4", "Fork_0")
        ],
    },
    "Safe System (Linear Dependency - No Cycle)": {
        "description": "Processes form a directed acyclic chain: P1 waits for R2 held by P2. P2 waits for R3 held by P3. P3 requests nothing and can complete, freeing R3 for P2, which then frees R2 for P1.",
        "processes": ["P1", "P2", "P3"],
        "resources": ["R1", "R2", "R3"],
        "allocations": [("R1", "P1"), ("R2", "P2"), ("R3", "P3")],
        "requests": [("P1", "R2"), ("P2", "R3")],
    },
    "Partial Deadlock with Bystander": {
        "description": "Processes P1 and P2 are locked in a mutual cycle (R1 <-> R2). Meanwhile, P3 is holding R3 and waiting on R4 held by independent process P4. P4 can complete freely, showing that deadlock affects only a subset.",
        "processes": ["P1", "P2", "P3", "P4"],
        "resources": ["R1", "R2", "R3", "R4"],
        "allocations": [("R1", "P1"), ("R2", "P2"), ("R3", "P3"), ("R4", "P4")],
        "requests": [("P1", "R2"), ("P2", "R1"), ("P3", "R4")],
    }
}

MULTI_INSTANCE_PRESETS: Dict[str, Dict[str, Any]] = {
    "Silberschatz OS Textbook Deadlock (Sec 8.6)": {
        "description": "The exact multi-instance deadlock example from Operating System Concepts (Silberschatz et al.). P0 completes and frees resources, but P1, P2, P3, and P4 remain mutually deadlocked.",
        "processes": ["P0", "P1", "P2", "P3", "P4"],
        "resources": ["A", "B", "C"],
        "available": [0, 0, 0],
        "allocation": [
            [0, 1, 0], # P0
            [2, 0, 0], # P1
            [3, 0, 3], # P2
            [2, 1, 1], # P3
            [0, 0, 2]  # P4
        ],
        "request": [
            [0, 0, 0], # P0
            [2, 0, 2], # P1
            [0, 0, 1], # P2
            [1, 0, 0], # P3
            [0, 0, 2]  # P4
        ]
    },
    "Silberschatz Safe Example (All Finish)": {
        "description": "Same system as above before P2 requests additional instance of C. In this case, P0 finishes, then P2 finishes and releases resources, enabling all processes to finish without deadlock.",
        "processes": ["P0", "P1", "P2", "P3", "P4"],
        "resources": ["A", "B", "C"],
        "available": [0, 0, 0],
        "allocation": [
            [0, 1, 0], # P0
            [2, 0, 0], # P1
            [3, 0, 3], # P2
            [2, 1, 1], # P3
            [0, 0, 2]  # P4
        ],
        "request": [
            [0, 0, 0], # P0
            [2, 0, 2], # P1
            [0, 0, 0], # P2 has no pending request
            [1, 0, 0], # P3
            [0, 0, 2]  # P4
        ]
    },
    "Cycle Exists but NO Deadlock (Multi-Instance)": {
        "description": "Famous OS counterexample! A cycle exists between P1, R1, P2, and R2. However, because R1 and R2 have additional instances held by non-requesting processes (P3, P4), those processes finish and break the wait without deadlock.",
        "processes": ["P1", "P2", "P3", "P4"],
        "resources": ["R1", "R2"],
        "available": [0, 0],
        "allocation": [
            [1, 0], # P1
            [0, 1], # P2
            [1, 0], # P3
            [0, 1]  # P4
        ],
        "request": [
            [0, 1], # P1 waits for R2
            [1, 0], # P2 waits for R1
            [0, 0], # P3 has no request!
            [0, 0]  # P4 has no request!
        ]
    },
    "Severe Multi-Resource Gridlock": {
        "description": "4 processes competing heavily for 4 resource types (CPU, GPU, RAM, Disk) with 0 available units left and circular interdependent requests.",
        "processes": ["Proc_Alpha", "Proc_Beta", "Proc_Gamma", "Proc_Delta"],
        "resources": ["CPU", "GPU", "RAM", "Disk"],
        "available": [0, 0, 0, 0],
        "allocation": [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 0, 0],
            [0, 0, 1, 1]
        ],
        "request": [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0]
        ]
    }
}
