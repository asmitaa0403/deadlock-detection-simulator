"""
Graphviz DOT generation & styling for Deadlock Simulator
"""

from typing import List, Tuple, Set, Dict, Optional, Any

class GraphVisualizer:
    @staticmethod
    def generate_rag_dot(
        processes: List[str],
        resources: List[str],
        allocations: List[Tuple[str, str]], # (R, P)
        requests: List[Tuple[str, str]],    # (P, R)
        deadlocked_processes: Optional[Set[str]] = None,
        deadlocked_resources: Optional[Set[str]] = None,
        cycle_edges: Optional[List[Tuple[str, str]]] = None,
        active_process: Optional[str] = None,
        layout_dir: str = "LR"
    ) -> str:
        """
        Generates Graphviz DOT string for Resource Allocation Graph (RAG).
        """
        deadlocked_processes = set(deadlocked_processes or [])
        deadlocked_resources = set(deadlocked_resources or [])
        cycle_edges_set = set(cycle_edges or [])

        dot_lines = [
            f'digraph RAG {{',
            f'    rankdir={layout_dir};',
            f'    bgcolor="transparent";',
            f'    node [fontname="Helvetica, Arial, sans-serif", fontsize=12, style="filled,bold", penwidth=2];',
            f'    edge [fontname="Helvetica, Arial, sans-serif", fontsize=10, penwidth=1.8, arrowsize=0.8];',
            f'',
            f'    // Process Nodes (Circles / Ellipses)',
            f'    subgraph cluster_processes {{',
            f'        style=invis;',
        ]

        for p in processes:
            if p == active_process:
                # Highlighting currently evaluated process in stepper
                dot_lines.append(
                    f'        "{p}" [shape=circle, fillcolor="#FEF08A", color="#CA8A04", fontcolor="#854D0E", label="{p}\\n(ACTIVE)", penwidth=3];'
                )
            elif p in deadlocked_processes:
                dot_lines.append(
                    f'        "{p}" [shape=circle, fillcolor="#FEE2E2", color="#DC2626", fontcolor="#991B1B", label="{p}\\n(DEADLOCKED)", penwidth=3];'
                )
            else:
                dot_lines.append(
                    f'        "{p}" [shape=circle, fillcolor="#E0E7FF", color="#4338CA", fontcolor="#312E81", label="{p}"];'
                )

        dot_lines.append('    }')
        dot_lines.append('')
        dot_lines.append('    // Resource Nodes (Rectangles)')
        dot_lines.append('    subgraph cluster_resources {')
        dot_lines.append('        style=invis;')

        for r in resources:
            if r in deadlocked_resources:
                dot_lines.append(
                    f'        "{r}" [shape=box, style="filled,rounded,bold", fillcolor="#FEE2E2", color="#DC2626", fontcolor="#991B1B", label="[ {r} ]\\n(BLOCKED)", penwidth=3];'
                )
            else:
                dot_lines.append(
                    f'        "{r}" [shape=box, style="filled,rounded,bold", fillcolor="#FEF3C7", color="#D97706", fontcolor="#78350F", label="[ {r} ]"];'
                )

        dot_lines.append('    }')
        dot_lines.append('')
        dot_lines.append('    // Edges')

        # Allocations: R -> P (Solid line)
        for r, p in allocations:
            is_cycle = (r, p) in cycle_edges_set or (p in deadlocked_processes and r in deadlocked_resources)
            if is_cycle:
                dot_lines.append(
                    f'    "{r}" -> "{p}" [label=" holds", color="#DC2626", fontcolor="#DC2626", penwidth=2.8, style=solid];'
                )
            else:
                dot_lines.append(
                    f'    "{r}" -> "{p}" [label=" holds", color="#059669", fontcolor="#065F46", style=solid];'
                )

        # Requests: P -> R (Dashed line)
        for p, r in requests:
            is_cycle = (p, r) in cycle_edges_set or (p in deadlocked_processes and r in deadlocked_resources)
            if is_cycle:
                dot_lines.append(
                    f'    "{p}" -> "{r}" [label=" waits for", color="#DC2626", fontcolor="#DC2626", penwidth=2.8, style=dashed];'
                )
            else:
                dot_lines.append(
                    f'    "{p}" -> "{r}" [label=" requests", color="#D97706", fontcolor="#B45309", style=dashed];'
                )

        dot_lines.append('}')
        return '\n'.join(dot_lines)

    @staticmethod
    def generate_wfg_dot(
        processes: List[str],
        edges: List[Tuple[str, str, str]], # (Pi, Pj, resource_label)
        deadlocked_processes: Optional[Set[str]] = None,
        cycle_edges: Optional[List[Tuple[str, str]]] = None,
        active_process: Optional[str] = None,
        layout_dir: str = "LR"
    ) -> str:
        """
        Generates Graphviz DOT string for Wait-For Graph (WFG).
        """
        deadlocked_processes = set(deadlocked_processes or [])
        cycle_edges_set = set(cycle_edges or [])

        dot_lines = [
            f'digraph WFG {{',
            f'    rankdir={layout_dir};',
            f'    bgcolor="transparent";',
            f'    node [fontname="Helvetica, Arial, sans-serif", fontsize=12, style="filled,bold", shape=circle, penwidth=2];',
            f'    edge [fontname="Helvetica, Arial, sans-serif", fontsize=10, penwidth=1.8, arrowsize=0.8];',
            f'',
            f'    // Processes',
        ]

        for p in processes:
            if p == active_process:
                dot_lines.append(
                    f'    "{p}" [fillcolor="#FEF08A", color="#CA8A04", fontcolor="#854D0E", label="{p}\\n(ACTIVE)", penwidth=3];'
                )
            elif p in deadlocked_processes:
                dot_lines.append(
                    f'    "{p}" [fillcolor="#FEE2E2", color="#DC2626", fontcolor="#991B1B", label="{p}\\n(DEADLOCKED)", penwidth=3];'
                )
            else:
                dot_lines.append(
                    f'    "{p}" [fillcolor="#E0E7FF", color="#4338CA", fontcolor="#312E81", label="{p}"];'
                )

        dot_lines.append('')
        dot_lines.append('    // Wait-For Edges (Pi waits for Pj)')

        for u, v, res in edges:
            is_cycle = (u, v) in cycle_edges_set or (u in deadlocked_processes and v in deadlocked_processes)
            label_text = f" waiting on {res}" if res else " waits for"
            if is_cycle:
                dot_lines.append(
                    f'    "{u}" -> "{v}" [label="{label_text}", color="#DC2626", fontcolor="#DC2626", penwidth=3, style=solid];'
                )
            else:
                dot_lines.append(
                    f'    "{u}" -> "{v}" [label="{label_text}", color="#4F46E5", fontcolor="#4338CA", style=solid];'
                )

        dot_lines.append('}')
        return '\n'.join(dot_lines)

    @staticmethod
    def generate_multi_rag_dot(
        process_names: List[str],
        resource_names: List[str],
        available: List[int],
        allocation: List[List[int]],
        request: List[List[int]],
        deadlocked_processes: Optional[Set[str]] = None,
        active_process: Optional[str] = None,
        layout_dir: str = "LR"
    ) -> str:
        """
        Generates Graphviz DOT string for Multi-Instance Resource Allocation Graph.
        Shows resource instances in nodes and multi-instance weighted edges.
        """
        deadlocked_processes = set(deadlocked_processes or [])

        dot_lines = [
            f'digraph MultiRAG {{',
            f'    rankdir={layout_dir};',
            f'    bgcolor="transparent";',
            f'    node [fontname="Helvetica, Arial, sans-serif", fontsize=12, style="filled,bold", penwidth=2];',
            f'    edge [fontname="Helvetica, Arial, sans-serif", fontsize=10, penwidth=1.8, arrowsize=0.8];',
            f'',
            f'    // Processes',
        ]

        for p in process_names:
            if p == active_process:
                dot_lines.append(
                    f'    "{p}" [shape=circle, fillcolor="#FEF08A", color="#CA8A04", fontcolor="#854D0E", label="{p}\\n(ACTIVE)", penwidth=3];'
                )
            elif p in deadlocked_processes:
                dot_lines.append(
                    f'    "{p}" [shape=circle, fillcolor="#FEE2E2", color="#DC2626", fontcolor="#991B1B", label="{p}\\n(DEADLOCKED)", penwidth=3];'
                )
            else:
                dot_lines.append(
                    f'    "{p}" [shape=circle, fillcolor="#E0E7FF", color="#4338CA", fontcolor="#312E81", label="{p}"];'
                )

        dot_lines.append('')
        dot_lines.append('    // Resources with Instance Counts')

        # Calculate total instances for each resource = Available + Sum of Allocations
        for j, r in enumerate(resource_names):
            avail = available[j]
            allocated_total = sum(allocation[i][j] for i in range(len(process_names)))
            total = avail + allocated_total
            label = f"{r}\\n[Avail: {avail} / Total: {total}]"
            dot_lines.append(
                f'    "{r}" [shape=box, style="filled,rounded,bold", fillcolor="#FEF3C7", color="#D97706", fontcolor="#78350F", label="{label}"];'
            )

        dot_lines.append('')
        dot_lines.append('    // Allocations: R -> P')
        for i, p in enumerate(process_names):
            for j, r in enumerate(resource_names):
                qty = allocation[i][j]
                if qty > 0:
                    is_deadlocked_edge = p in deadlocked_processes
                    color = "#DC2626" if is_deadlocked_edge else "#059669"
                    fontcolor = "#DC2626" if is_deadlocked_edge else "#065F46"
                    dot_lines.append(
                        f'    "{r}" -> "{p}" [label=" {qty} inst", color="{color}", fontcolor="{fontcolor}", penwidth=2];'
                    )

        dot_lines.append('')
        dot_lines.append('    // Requests: P -> R')
        for i, p in enumerate(process_names):
            for j, r in enumerate(resource_names):
                qty = request[i][j]
                if qty > 0:
                    is_deadlocked_edge = p in deadlocked_processes
                    color = "#DC2626" if is_deadlocked_edge else "#D97706"
                    fontcolor = "#DC2626" if is_deadlocked_edge else "#B45309"
                    dot_lines.append(
                        f'    "{p}" -> "{r}" [label=" req {qty}", color="{color}", fontcolor="{fontcolor}", style=dashed, penwidth=2];'
                    )

        dot_lines.append('}')
        return '\n'.join(dot_lines)
