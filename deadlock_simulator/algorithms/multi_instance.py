"""
Multiple-Instance Deadlock Detection Algorithm (Silberschatz / Operating Systems)
"""

import numpy as np
from typing import Dict, List, Any, Optional

class MultiInstanceDetector:
    def __init__(
        self,
        process_names: List[str],
        resource_names: List[str],
        available: List[int],
        allocation: List[List[int]],
        request: List[List[int]]
    ):
        self.process_names = list(process_names)
        self.resource_names = list(resource_names)
        self.available = np.array(available, dtype=int)
        self.allocation = np.array(allocation, dtype=int)
        self.request = np.array(request, dtype=int)

        self.n = len(self.process_names)
        self.m = len(self.resource_names)

        # Validate dimensions
        assert self.allocation.shape == (self.n, self.m), f"Allocation shape {self.allocation.shape} != ({self.n}, {self.m})"
        assert self.request.shape == (self.n, self.m), f"Request shape {self.request.shape} != ({self.n}, {self.m})"
        assert len(self.available) == self.m, f"Available length {len(self.available)} != {self.m}"

    def detect_deadlock(self) -> Dict[str, Any]:
        """
        Executes the detection algorithm and records detailed step-by-step execution.
        """
        work = self.available.copy()
        finish = np.zeros(self.n, dtype=bool)

        # Step 1: Initialize finish
        # If Allocation[i] == 0, finish[i] = True; otherwise False
        initial_zero_alloc = []
        for i in range(self.n):
            if np.all(self.allocation[i] == 0):
                finish[i] = True
                initial_zero_alloc.append(self.process_names[i])
            else:
                finish[i] = False

        steps = []
        safe_sequence = []

        step_counter = 1
        initial_step_desc = (
            f"Initialization: Work = {list(work)}. "
            f"Processes with zero allocation ({', '.join(initial_zero_alloc) if initial_zero_alloc else 'None'}) set to Finish = True."
        )
        steps.append({
            "step": step_counter,
            "action": "Initialization",
            "process_evaluated": None,
            "work": list(work),
            "finish": {self.process_names[k]: bool(finish[k]) for k in range(self.n)},
            "explanation": initial_step_desc,
            "successful_process": None
        })

        # Step 2 & 3: Iterate until no process can be satisfied
        while True:
            found = False
            candidate_logs = []

            for i in range(self.n):
                if not finish[i]:
                    req_i = self.request[i]
                    can_satisfy = np.all(req_i <= work)

                    candidate_logs.append({
                        "process": self.process_names[i],
                        "request": list(req_i),
                        "work": list(work),
                        "can_satisfy": bool(can_satisfy)
                    })

                    if can_satisfy:
                        found = True
                        step_counter += 1
                        old_work = list(work)
                        work = work + self.allocation[i]
                        finish[i] = True
                        p_name = self.process_names[i]
                        safe_sequence.append(p_name)

                        explanation = (
                            f"Process {p_name} can be satisfied! "
                            f"Request {list(req_i)} <= Work {old_work}. "
                            f"{p_name} finishes and releases its allocated resources {list(self.allocation[i])}. "
                            f"New Work = {list(work)}."
                        )

                        steps.append({
                            "step": step_counter,
                            "action": f"Process {p_name} Completed",
                            "process_evaluated": p_name,
                            "work": list(work),
                            "finish": {self.process_names[k]: bool(finish[k]) for k in range(self.n)},
                            "explanation": explanation,
                            "successful_process": p_name,
                            "candidate_evaluations": candidate_logs
                        })
                        # Restart search from beginning to allow newly freed resources to satisfy earlier processes
                        break

            if not found:
                break

        # Step 4: Check if any process has finish == False
        deadlocked_indices = [i for i in range(self.n) if not finish[i]]
        deadlocked_processes = [self.process_names[i] for i in deadlocked_indices]
        is_deadlocked = len(deadlocked_processes) > 0

        final_explanation = (
            f"TERMINATION: No more processes with Finish = False have Request <= Work. "
            + (f"Deadlock detected! Processes {deadlocked_processes} are deadlocked." if is_deadlocked else "No deadlock detected! All processes can finish successfully.")
        )

        steps.append({
            "step": step_counter + 1,
            "action": "Final Conclusion",
            "process_evaluated": None,
            "work": list(work),
            "finish": {self.process_names[k]: bool(finish[k]) for k in range(self.n)},
            "explanation": final_explanation,
            "successful_process": None,
            "is_final": True
        })

        return {
            "is_deadlocked": is_deadlocked,
            "deadlocked_processes": deadlocked_processes,
            "safe_sequence": safe_sequence,
            "final_work": list(work),
            "final_finish": {self.process_names[k]: bool(finish[k]) for k in range(self.n)},
            "steps": steps
        }

    def simulate_process_termination(self, victim_process: str) -> "MultiInstanceDetector":
        """
        Creates a new detector state where victim_process has been terminated.
        Its allocated resources are released to Available, its row is removed from Allocation and Request.
        """
        if victim_process not in self.process_names:
            return self

        idx = self.process_names.index(victim_process)
        released_resources = self.allocation[idx]

        new_available = self.available + released_resources
        new_process_names = [p for i, p in enumerate(self.process_names) if i != idx]
        new_allocation = [list(self.allocation[i]) for i in range(self.n) if i != idx]
        new_request = [list(self.request[i]) for i in range(self.n) if i != idx]

        return MultiInstanceDetector(
            process_names=new_process_names,
            resource_names=self.resource_names,
            available=list(new_available),
            allocation=new_allocation,
            request=new_request
        )

    def suggest_victim_termination(self) -> Dict[str, Any]:
        """
        Evaluates deadlocked processes and determines which one's termination
        releases the most needed resources or breaks the deadlock fastest.
        """
        detection = self.detect_deadlock()
        if not detection["is_deadlocked"]:
            return {"victim": None, "reason": "No deadlock present."}

        deadlocked = detection["deadlocked_processes"]
        best_victim = None
        max_freed_total = -1

        victim_scores = []
        for p in deadlocked:
            idx = self.process_names.index(p)
            alloc = self.allocation[idx]
            total_held = int(np.sum(alloc))

            # Test simulating termination
            sim = self.simulate_process_termination(p)
            sim_res = sim.detect_deadlock()
            deadlocked_after = len(sim_res["deadlocked_processes"])

            victim_scores.append({
                "process": p,
                "total_held": total_held,
                "allocation": list(alloc),
                "deadlocked_after": deadlocked_after,
                "resolves_deadlock": not sim_res["is_deadlocked"]
            })

        # Prefer victim that completely resolves deadlock; if tie, the one holding most resources
        victim_scores.sort(key=lambda x: (not x["resolves_deadlock"], x["deadlocked_after"], -x["total_held"]))
        chosen = victim_scores[0]

        return {
            "victim": chosen["process"],
            "resolves_deadlock": chosen["resolves_deadlock"],
            "deadlocked_remaining": chosen["deadlocked_after"],
            "candidates": victim_scores,
            "reason": (
                f"Terminating {chosen['process']} releases {chosen['allocation']} resources. "
                + ("It completely resolves the deadlock!" if chosen["resolves_deadlock"] else f"It reduces deadlocked processes to {chosen['deadlocked_after']}.")
            )
        }
