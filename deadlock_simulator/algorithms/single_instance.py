"""
Single-Instance Resource Allocation Graph & Wait-For Graph Deadlock Detection
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Any

class SingleInstanceDetector:
    def __init__(self, processes: List[str], resources: List[str], allocations: List[Tuple[str, str]], requests: List[Tuple[str, str]]):
        """
        processes: ['P0', 'P1', ...]
        resources: ['R0', 'R1', ...]
        allocations: [(R, P), ...] -> Resource R is allocated to Process P
        requests: [(P, R), ...] -> Process P is requesting Resource R
        """
        self.processes = list(processes)
        self.resources = list(resources)
        self.allocations = list(allocations)  # (R, P)
        self.requests = list(requests)        # (P, R)

    def build_rag(self) -> nx.DiGraph:
        """Builds the Resource Allocation Graph (RAG)"""
        rag = nx.DiGraph()
        for p in self.processes:
            rag.add_node(p, node_type="process")
        for r in self.resources:
            rag.add_node(r, node_type="resource")
        
        # Allocations: R -> P
        for r, p in self.allocations:
            rag.add_edge(r, p, edge_type="allocation")
            
        # Requests: P -> R
        for p, r in self.requests:
            rag.add_edge(p, r, edge_type="request")
            
        return rag

    def build_wfg(self) -> nx.DiGraph:
        """
        Builds the Wait-For Graph (WFG) from the RAG.
        Edge Pi -> Pk exists if Pi requests R and R is allocated to Pk.
        """
        wfg = nx.DiGraph()
        for p in self.processes:
            wfg.add_node(p)

        # Mapping: Resource -> Process holding it (single instance assumption)
        res_holder = {}
        for r, p in self.allocations:
            res_holder[r] = p

        for p_req, r in self.requests:
            if r in res_holder:
                p_holder = res_holder[r]
                if p_req != p_holder:
                    wfg.add_edge(p_req, p_holder, resource=r)

        return wfg

    def detect_cycles(self) -> Dict[str, Any]:
        """
        Finds all elementary cycles in the Wait-For Graph and the RAG.
        Returns:
            is_deadlocked: bool
            deadlocked_processes: Set of process names
            wfg_cycles: List of cycles (each cycle is a list of nodes)
            rag_cycles: List of cycles in RAG
            deadlocked_resources: Set of resource names involved in cycles
            step_by_step_trace: Walkthrough of DFS cycle detection
        """
        wfg = self.build_wfg()
        rag = self.build_rag()
        
        # Elementary cycles in WFG
        wfg_cycles = list(nx.simple_cycles(wfg))
        
        # Elementary cycles in RAG
        rag_cycles = list(nx.simple_cycles(rag))
        
        deadlocked_processes = set()
        for c in wfg_cycles:
            deadlocked_processes.update(c)
            
        deadlocked_resources = set()
        for c in rag_cycles:
            for node in c:
                if node in self.resources:
                    deadlocked_resources.add(node)

        # Build DFS trace for step-by-step educational visualization
        steps = self._generate_dfs_trace(wfg)

        return {
            "is_deadlocked": len(wfg_cycles) > 0,
            "deadlocked_processes": sorted(list(deadlocked_processes)),
            "deadlocked_resources": sorted(list(deadlocked_resources)),
            "wfg_cycles": wfg_cycles,
            "rag_cycles": rag_cycles,
            "trace": steps,
            "wfg_graph": wfg,
            "rag_graph": rag
        }

    def _generate_dfs_trace(self, wfg: nx.DiGraph) -> List[Dict[str, Any]]:
        """
        Generates an educational step-by-step trace of DFS cycle detection
        with color states: UNVISITED (white), VISITING (gray), VISITED (black).
        """
        steps = []
        color = {node: "UNVISITED" for node in wfg.nodes()}
        parent = {}
        detected_cycles = []

        def dfs(u, path):
            color[u] = "VISITING"
            path.append(u)
            steps.append({
                "step": len(steps) + 1,
                "current_node": u,
                "action": f"Visiting node {u}. Path stack: {' -> '.join(path)}",
                "path": list(path),
                "colors": dict(color),
                "cycle_found": None
            })

            for v in wfg.neighbors(u):
                edge_res = wfg[u][v].get("resource", "")
                res_desc = f" (waiting on {edge_res})" if edge_res else ""
                
                if color[v] == "VISITING":
                    # Cycle found!
                    cycle_start_idx = path.index(v)
                    cycle = path[cycle_start_idx:] + [v]
                    detected_cycles.append(cycle)
                    steps.append({
                        "step": len(steps) + 1,
                        "current_node": v,
                        "action": f"CYCLE DETECTED! Back-edge found from {u} to {v}{res_desc}. Cycle: {' -> '.join(cycle)}",
                        "path": list(path),
                        "colors": dict(color),
                        "cycle_found": cycle
                    })
                elif color[v] == "UNVISITED":
                    dfs(v, path)

            path.pop()
            color[u] = "VISITED"
            steps.append({
                "step": len(steps) + 1,
                "current_node": u,
                "action": f"Finished exploring all branches from {u}. Marked as VISITED (safe / no new cycles from here).",
                "path": list(path),
                "colors": dict(color),
                "cycle_found": None
            })

        for node in sorted(wfg.nodes()):
            if color[node] == "UNVISITED":
                dfs(node, [])

        return steps

    def suggest_victim(self) -> Dict[str, Any]:
        """
        Suggests which process to terminate to break the most cycles with minimal disruption.
        Uses process frequency in cycles.
        """
        results = self.detect_cycles()
        if not results["is_deadlocked"]:
            return {"victim": None, "reason": "System is not in a deadlock state."}

        counts = {}
        for c in results["wfg_cycles"]:
            for p in c:
                counts[p] = counts.get(p, 0) + 1

        # Sort by most cycles broken
        sorted_victims = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        best_victim, cycle_count = sorted_victims[0]

        return {
            "victim": best_victim,
            "cycles_broken": cycle_count,
            "total_cycles": len(results["wfg_cycles"]),
            "all_candidates": sorted_victims,
            "reason": f"Process {best_victim} is involved in {cycle_count} out of {len(results['wfg_cycles'])} deadlock cycle(s). Terminating it maximizes cycle reduction."
        }

    def terminate_process(self, process_to_kill: str) -> "SingleInstanceDetector":
        """
        Returns a new SingleInstanceDetector instance with process_to_kill removed.
        Allocated resources are released, and pending requests are cancelled.
        """
        new_processes = [p for p in self.processes if p != process_to_kill]
        new_allocations = [(r, p) for r, p in self.allocations if p != process_to_kill]
        new_requests = [(p, r) for p, r in self.requests if p != process_to_kill]

        return SingleInstanceDetector(
            processes=new_processes,
            resources=self.resources,
            allocations=new_allocations,
            requests=new_requests
        )
