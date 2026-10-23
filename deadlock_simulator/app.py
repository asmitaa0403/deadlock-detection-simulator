"""
Deadlock Detection Simulator - Streamlit Application
Interactive visualizer and step-by-step simulator for Deadlock Detection in Operating Systems.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from typing import List, Tuple, Set, Dict, Any

from algorithms.single_instance import SingleInstanceDetector
from algorithms.multi_instance import MultiInstanceDetector
from visualizer import GraphVisualizer
from presets import SINGLE_INSTANCE_PRESETS, MULTI_INSTANCE_PRESETS

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Deadlock Detection Simulator",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value-safe {
        font-size: 1.4rem;
        font-weight: 700;
        color: #059669;
    }
    .metric-value-danger {
        font-size: 1.4rem;
        font-weight: 700;
        color: #DC2626;
    }
    .metric-value-neutral {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1E293B;
    }
    .badge-pill-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 6px;
        border: 1px solid #FCA5A5;
    }
    .badge-pill-safe {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 6px;
        border: 1px solid #6EE7B7;
    }
    .step-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 10px 0;
        font-size: 0.95rem;
        color: #1E3A8A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        border-radius: 6px 6px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🔒 Deadlock Simulator")
st.sidebar.caption("Operating Systems Deadlock Detection & Recovery Lab")

mode = st.sidebar.radio(
    "Choose Simulator Mode:",
    [
        "🔄 Single-Instance (RAG & WFG)",
        "📊 Multi-Instance (Matrix Detection)",
        "🛠️ Interactive Playground (Custom)",
        "📚 Theory & Algorithm Primer"
    ],
    index=0
)

st.sidebar.markdown("---")

# ==============================================================================
# MODE 1: SINGLE-INSTANCE RESOURCE ALLOCATION GRAPH & WAIT-FOR GRAPH
# ==============================================================================
if mode == "🔄 Single-Instance (RAG & WFG)":
    st.header("🔄 Single-Instance Deadlock Detection")
    st.caption("Resource Allocation Graph (RAG) and Wait-For Graph (WFG) Cycle Detection")

    # Preset selection
    preset_col1, preset_col2 = st.columns([2, 1])
    with preset_col1:
        selected_preset = st.selectbox(
            "Select Scenario Preset:",
            list(SINGLE_INSTANCE_PRESETS.keys()),
            key="si_preset_selector"
        )
    with preset_col2:
        layout_dir = st.selectbox("Graph Layout Direction:", ["LR (Left-to-Right)", "TB (Top-to-Bottom)"], index=0)
        rankdir = "LR" if "LR" in layout_dir else "TB"

    preset_data = SINGLE_INSTANCE_PRESETS[selected_preset]
    st.info(f"💡 **Scenario Overview:** {preset_data['description']}")

    # Session state for working allocations/requests to support recovery simulation
    state_key = f"si_state_{selected_preset}"
    if state_key not in st.session_state or st.session_state.get(f"{state_key}_last_preset") != selected_preset:
        st.session_state[state_key] = {
            "processes": list(preset_data["processes"]),
            "resources": list(preset_data["resources"]),
            "allocations": list(preset_data["allocations"]),
            "requests": list(preset_data["requests"]),
            "terminated": []
        }
        st.session_state[f"{state_key}_last_preset"] = selected_preset

    current_state = st.session_state[state_key]

    # Instantiate detector
    detector = SingleInstanceDetector(
        processes=current_state["processes"],
        resources=current_state["resources"],
        allocations=current_state["allocations"],
        requests=current_state["requests"]
    )

    result = detector.detect_cycles()
    is_deadlocked = result["is_deadlocked"]
    deadlocked_procs = result["deadlocked_processes"]
    deadlocked_res = result["deadlocked_resources"]
    wfg_cycles = result["wfg_cycles"]
    rag_cycles = result["rag_cycles"]
    wfg_graph = result["wfg_graph"]

    # --- TOP METRICS ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        status_html = (
            f'<div class="metric-card">'
            f'<div class="metric-title">System Status</div>'
            f'<div class="{ "metric-value-danger" if is_deadlocked else "metric-value-safe" }">'
            f'{"🔴 DEADLOCKED" if is_deadlocked else "🟢 SAFE (NO DEADLOCK)"}'
            f'</div></div>'
        )
        st.markdown(status_html, unsafe_allow_html=True)
    with m_col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Deadlocked Processes</div>'
            f'<div class="{ "metric-value-danger" if is_deadlocked else "metric-value-safe" }">'
            f'{len(deadlocked_procs)} / {len(current_state["processes"])}'
            f'</div></div>',
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Detected Cycles</div>'
            f'<div class="{ "metric-value-danger" if len(wfg_cycles) > 0 else "metric-value-neutral" }">'
            f'{len(wfg_cycles)}'
            f'</div></div>',
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Resources Involved</div>'
            f'<div class="metric-value-neutral">{len(current_state["resources"])}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # If deadlocked, show warning banner with deadlocked nodes & cycles
    if is_deadlocked:
        p_pills = "".join([f'<span class="badge-pill-danger">{p}</span>' for p in deadlocked_procs])
        cycles_desc = " &nbsp;|&nbsp; ".join([" &rarr; ".join(c + [c[0]]) for c in wfg_cycles])
        st.error(f"🚨 **Deadlock Detected!**\n\n**Processes in deadlock:** {p_pills}\n\n**Cycle Paths:** `{cycles_desc}`", icon="⚠️")
    else:
        st.success("✅ **System is in a Safe State.** No cycles detected in the Wait-For Graph. All processes can proceed to completion without deadlock.", icon="🎉")

    # --- TABS FOR VISUALIZATION, STEPPER, AND RECOVERY ---
    tab_rag, tab_wfg, tab_trace, tab_recovery = st.tabs([
        "🕸️ Resource Allocation Graph (RAG)",
        "⚡ Wait-For Graph (WFG)",
        "🔍 Step-by-Step Cycle Detection",
        "🩹 Deadlock Recovery Simulator"
    ])

    with tab_rag:
        st.subheader("Resource Allocation Graph (RAG)")
        st.caption("Circles represent Processes; Rectangles represent Resources. Solid lines indicate allocations (R &rarr; P); Dashed lines indicate requests (P &rarr; R). Deadlocked elements are highlighted in red.")

        # Prepare cycle edges for RAG highlighting
        rag_cycle_edges = []
        for c in rag_cycles:
            for i in range(len(c)):
                rag_cycle_edges.append((c[i], c[(i + 1) % len(c)]))

        rag_dot = GraphVisualizer.generate_rag_dot(
            processes=current_state["processes"],
            resources=current_state["resources"],
            allocations=current_state["allocations"],
            requests=current_state["requests"],
            deadlocked_processes=set(deadlocked_procs),
            deadlocked_resources=set(deadlocked_res),
            cycle_edges=rag_cycle_edges,
            layout_dir=rankdir
        )
        st.graphviz_chart(rag_dot, use_container_width=True)

        with st.expander("📝 View Edge List & Allocations"):
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Allocations (Holdings):**")
                alloc_df = pd.DataFrame(current_state["allocations"], columns=["Resource", "Allocated To Process"])
                st.dataframe(alloc_df if not alloc_df.empty else pd.DataFrame({"Message": ["No active allocations"]}), use_container_width=True)
            with c2:
                st.write("**Requests (Pending Waits):**")
                req_df = pd.DataFrame(current_state["requests"], columns=["Process", "Requesting Resource"])
                st.dataframe(req_df if not req_df.empty else pd.DataFrame({"Message": ["No active requests"]}), use_container_width=True)

    with tab_wfg:
        st.subheader("Wait-For Graph (WFG)")
        st.caption("Reduced graph showing direct process-to-process wait dependencies (P_i &rarr; P_k if P_i is waiting for a resource held by P_k). In single-instance systems, a cycle in the WFG is necessary and sufficient for deadlock.")

        wfg_edges_list = []
        for u, v, data in wfg_graph.edges(data=True):
            res_label = data.get("resource", "")
            wfg_edges_list.append((u, v, res_label))

        wfg_cycle_edges = []
        for c in wfg_cycles:
            for i in range(len(c)):
                wfg_cycle_edges.append((c[i], c[(i + 1) % len(c)]))

        wfg_dot = GraphVisualizer.generate_wfg_dot(
            processes=current_state["processes"],
            edges=wfg_edges_list,
            deadlocked_processes=set(deadlocked_procs),
            cycle_edges=wfg_cycle_edges,
            layout_dir=rankdir
        )
        st.graphviz_chart(wfg_dot, use_container_width=True)

        if wfg_cycles:
            st.write("#### 🔁 Elementary Deadlock Cycles Detected:")
            for idx, c in enumerate(wfg_cycles, 1):
                st.markdown(f"**Cycle {idx}:** `{' -> '.join(c)} -> {c[0]}`")

    with tab_trace:
        st.subheader("Step-by-Step Depth-First Search (DFS) Cycle Detection")
        st.caption("Operating systems use DFS with recursion stack tracking to detect cycles in O(V + E) time.")

        trace_steps = result["trace"]
        if trace_steps:
            step_idx = st.slider(
                "DFS Step:",
                min_value=1,
                max_value=len(trace_steps),
                value=len(trace_steps),
                key="si_step_slider"
            )
            step_data = trace_steps[step_idx - 1]

            st.markdown(f'<div class="step-box"><b>Step {step_data["step"]} / {len(trace_steps)}:</b> {step_data["action"]}</div>', unsafe_allow_html=True)

            active_p = step_data.get("current_node")
            step_wfg_dot = GraphVisualizer.generate_wfg_dot(
                processes=current_state["processes"],
                edges=wfg_edges_list,
                deadlocked_processes=set(step_data["cycle_found"]) if step_data.get("cycle_found") else set(),
                active_process=active_p,
                layout_dir=rankdir
            )
            st.graphviz_chart(step_wfg_dot, use_container_width=True)

            # Node visit state colors
            color_df = pd.DataFrame([
                {"Process": p, "DFS State": step_data["colors"].get(p, "UNVISITED")}
                for p in current_state["processes"]
            ])
            st.dataframe(color_df, use_container_width=True)
        else:
            st.info("Wait-For graph has no edges to traverse.")

    with tab_recovery:
        st.subheader("🩹 Deadlock Recovery Simulator")
        st.caption("When a deadlock occurs, the OS must recover by terminating processes or preempting resources.")

        if not is_deadlocked:
            st.success("No recovery needed! System is currently deadlock-free.")
        else:
            victim_info = detector.suggest_victim()
            suggested_victim = victim_info.get("victim")

            st.markdown("#### 🎯 Algorithmic Victim Recommendation")
            st.info(f"💡 **Recommended Victim:** **`{suggested_victim}`**\n\n{victim_info['reason']}")

            col_rec1, col_rec2 = st.columns([2, 1])
            with col_rec1:
                selected_victim = st.selectbox(
                    "Choose process to abort/terminate:",
                    current_state["processes"],
                    index=current_state["processes"].index(suggested_victim) if suggested_victim in current_state["processes"] else 0
                )
            with col_rec2:
                st.write("")
                st.write("")
                if st.button("💥 Terminate Process", type="primary", use_container_width=True):
                    # Terminate process and update state
                    new_detector = detector.terminate_process(selected_victim)
                    current_state["processes"] = new_detector.processes
                    current_state["allocations"] = new_detector.allocations
                    current_state["requests"] = new_detector.requests
                    current_state["terminated"].append(selected_victim)
                    st.rerun()

        if current_state["terminated"]:
            st.warning(f"Terminated processes during recovery: {', '.join(current_state['terminated'])}")
            if st.button("🔄 Reset to Scenario Default"):
                st.session_state.pop(state_key, None)
                st.rerun()


# ==============================================================================
# MODE 2: MULTI-INSTANCE MATRIX DETECTION (SILBERSCHATZ ALGORITHM)
# ==============================================================================
elif mode == "📊 Multi-Instance (Matrix Detection)":
    st.header("📊 Multiple-Instance Deadlock Detection")
    st.caption("Implementation of the standard Silberschatz / Operating System Concepts Deadlock Detection Algorithm (Work & Finish Vectors)")

    # Preset selection
    m_preset_col1, m_preset_col2 = st.columns([2, 1])
    with m_preset_col1:
        selected_m_preset = st.selectbox(
            "Select Multi-Instance Scenario:",
            list(MULTI_INSTANCE_PRESETS.keys()),
            key="mi_preset_selector"
        )
    with m_preset_col2:
        m_layout_dir = st.selectbox("Graph Layout Direction:", ["LR (Left-to-Right)", "TB (Top-to-Bottom)"], index=0, key="mi_layout")
        m_rankdir = "LR" if "LR" in m_layout_dir else "TB"

    preset_data = MULTI_INSTANCE_PRESETS[selected_m_preset]
    st.info(f"💡 **Scenario Overview:** {preset_data['description']}")

    # Session state for working matrices
    mi_state_key = f"mi_state_{selected_m_preset}"
    if mi_state_key not in st.session_state or st.session_state.get(f"{mi_state_key}_last") != selected_m_preset:
        st.session_state[mi_state_key] = {
            "processes": list(preset_data["processes"]),
            "resources": list(preset_data["resources"]),
            "available": list(preset_data["available"]),
            "allocation": [list(row) for row in preset_data["allocation"]],
            "request": [list(row) for row in preset_data["request"]],
            "terminated": []
        }
        st.session_state[f"{mi_state_key}_last"] = selected_m_preset

    current_mi = st.session_state[mi_state_key]

    detector = MultiInstanceDetector(
        process_names=current_mi["processes"],
        resource_names=current_mi["resources"],
        available=current_mi["available"],
        allocation=current_mi["allocation"],
        request=current_mi["request"]
    )

    detection_result = detector.detect_deadlock()
    is_deadlocked = detection_result["is_deadlocked"]
    deadlocked_procs = detection_result["deadlocked_processes"]
    safe_seq = detection_result["safe_sequence"]
    steps = detection_result["steps"]

    # --- TOP METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">System Status</div>'
            f'<div class="{ "metric-value-danger" if is_deadlocked else "metric-value-safe" }">'
            f'{"🔴 DEADLOCK DETECTED" if is_deadlocked else "🟢 SAFE (NO DEADLOCK)"}'
            f'</div></div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Deadlocked Processes</div>'
            f'<div class="{ "metric-value-danger" if is_deadlocked else "metric-value-safe" }">'
            f'{len(deadlocked_procs)} / {len(current_mi["processes"])}'
            f'</div></div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Completed Sequentially</div>'
            f'<div class="metric-value-neutral">{len(safe_seq)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">Available Vector</div>'
            f'<div class="metric-value-neutral">{current_mi["available"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if is_deadlocked:
        p_pills = "".join([f'<span class="badge-pill-danger">{p}</span>' for p in deadlocked_procs])
        st.error(f"🚨 **Deadlock Detected!**\n\nThe algorithm halted because no uncompleted process has its request satisfied by the current Work vector.\n\n**Deadlocked processes:** {p_pills}", icon="⚠️")
    else:
        st.success(f"✅ **No Deadlock! Safe Completion Sequence:** `{' -> '.join(safe_seq)}`", icon="🎉")

    # --- TABS FOR MULTI-INSTANCE VIEW ---
    tab_matrix, tab_stepper, tab_graph, tab_recovery = st.tabs([
        "📋 Matrix & Vectors Overview",
        "⏯️ Interactive Step-by-Step Stepper",
        "🕸️ Resource Bipartite Graph",
        "🩹 Deadlock Resolution & Recovery"
    ])

    with tab_matrix:
        st.subheader("System State Matrices")
        
        c_avail, c_alloc, c_req = st.columns([1, 2, 2])
        with c_avail:
            st.write("**Available Vector [m]:**")
            avail_df = pd.DataFrame([current_mi["available"]], columns=current_mi["resources"], index=["Available"])
            st.dataframe(avail_df, use_container_width=True)

        with c_alloc:
            st.write("**Allocation Matrix [n × m]:**")
            alloc_df = pd.DataFrame(current_mi["allocation"], index=current_mi["processes"], columns=current_mi["resources"])
            st.dataframe(alloc_df, use_container_width=True)

        with c_req:
            st.write("**Request Matrix [n × m]:**")
            req_df = pd.DataFrame(current_mi["request"], index=current_mi["processes"], columns=current_mi["resources"])
            st.dataframe(req_df, use_container_width=True)

        # Highlight which processes are deadlocked
        if deadlocked_procs:
            st.write("**Process Status Summary:**")
            status_records = []
            for p in current_mi["processes"]:
                is_dl = p in deadlocked_procs
                status_records.append({
                    "Process": p,
                    "Status": "DEADLOCKED 🔴" if is_dl else "COMPLETED / SAFE 🟢",
                    "Finish State": detection_result["final_finish"].get(p, False)
                })
            st.dataframe(pd.DataFrame(status_records), use_container_width=True)

    with tab_stepper:
        st.subheader("Step-by-Step Detection Walkthrough")
        st.caption("Examine how the algorithm initializes Work = Available, checks Finish, and iteratively satisfies requests.")

        step_num = st.slider(
            "Algorithm Step:",
            min_value=1,
            max_value=len(steps),
            value=len(steps),
            key="mi_step_slider"
        )
        cur_step = steps[step_num - 1]

        st.markdown(f'<div class="step-box"><b>Step {cur_step["step"]} of {len(steps)}: {cur_step["action"]}</b><br>{cur_step["explanation"]}</div>', unsafe_allow_html=True)

        col_w, col_f = st.columns(2)
        with col_w:
            st.write("**Current Work Vector:**")
            st.dataframe(pd.DataFrame([cur_step["work"]], columns=current_mi["resources"], index=["Work"]), use_container_width=True)
        with col_f:
            st.write("**Current Finish Array:**")
            finish_df = pd.DataFrame([cur_step["finish"]])
            st.dataframe(finish_df, use_container_width=True)

        if "candidate_evaluations" in cur_step and cur_step["candidate_evaluations"]:
            with st.expander("🔍 Candidate Process Evaluations at this Step", expanded=True):
                cand_rows = []
                for cand in cur_step["candidate_evaluations"]:
                    cand_rows.append({
                        "Process": cand["process"],
                        "Request": str(cand["request"]),
                        "Work Vector": str(cand["work"]),
                        "Request <= Work?": "✅ Yes" if cand["can_satisfy"] else "❌ No (Blocked)"
                    })
                st.dataframe(pd.DataFrame(cand_rows), use_container_width=True)

    with tab_graph:
        st.subheader("Multi-Instance Resource Allocation Graph")
        st.caption("Processes (circles) and Resources (boxes with available/total instance counts). Edges show allocated instances and requested quantities.")

        rag_dot = GraphVisualizer.generate_multi_rag_dot(
            process_names=current_mi["processes"],
            resource_names=current_mi["resources"],
            available=current_mi["available"],
            allocation=current_mi["allocation"],
            request=current_mi["request"],
            deadlocked_processes=set(deadlocked_procs),
            layout_dir=m_rankdir
        )
        st.graphviz_chart(rag_dot, use_container_width=True)

    with tab_recovery:
        st.subheader("🩹 Deadlock Recovery Simulator")
        st.caption("Terminate a victim process to release its allocated resources back to the Available pool and re-run the detection algorithm.")

        if not is_deadlocked:
            st.success("No recovery needed! The system is completely deadlock-free.")
        else:
            victim_info = detector.suggest_victim_termination()
            best_victim = victim_info.get("victim")

            st.info(f"💡 **Algorithmic Victim Suggestion:** **`{best_victim}`**\n\n{victim_info['reason']}")

            col_v1, col_v2 = st.columns([2, 1])
            with col_v1:
                chosen_victim = st.selectbox(
                    "Select Process to Terminate / Preempt:",
                    deadlocked_procs,
                    index=deadlocked_procs.index(best_victim) if best_victim in deadlocked_procs else 0
                )
            with col_v2:
                st.write("")
                st.write("")
                if st.button("💥 Abort Selected Process", type="primary", use_container_width=True):
                    new_detector = detector.simulate_process_termination(chosen_victim)
                    current_mi["processes"] = new_detector.process_names
                    current_mi["available"] = list(new_detector.available)
                    current_mi["allocation"] = [list(r) for r in new_detector.allocation]
                    current_mi["request"] = [list(r) for r in new_detector.request]
                    current_mi["terminated"].append(chosen_victim)
                    st.rerun()

        if current_mi["terminated"]:
            st.warning(f"Terminated processes: {', '.join(current_mi['terminated'])}")
            if st.button("🔄 Reset Multi-Instance Scenario Default"):
                st.session_state.pop(mi_state_key, None)
                st.rerun()


# ==============================================================================
# MODE 3: INTERACTIVE PLAYGROUND (CUSTOM GRAPH / MATRIX BUILDER)
# ==============================================================================
elif mode == "🛠️ Interactive Playground (Custom)":
    st.header("🛠️ Custom Deadlock Playground")
    st.caption("Build custom Resource Allocation Graphs or input custom Available/Allocation/Request matrices.")

    pg_type = st.radio("Choose Playground Model:", ["Single-Instance Custom Graph", "Multi-Instance Custom Matrices"], horizontal=True)

    if pg_type == "Single-Instance Custom Graph":
        st.subheader("Single-Instance Graph Builder")

        col_n1, col_n2 = st.columns(2)
        with col_n1:
            num_p = st.number_input("Number of Processes:", min_value=2, max_value=8, value=3, step=1)
        with col_n2:
            num_r = st.number_input("Number of Resources:", min_value=1, max_value=8, value=3, step=1)

        custom_procs = [f"P{i}" for i in range(num_p)]
        custom_res = [f"R{j}" for j in range(num_r)]

        # Allocation edges builder (R -> P)
        st.write("#### 1. Resource Allocations (Who holds which resource?)")
        st.caption("Each single-instance resource can be held by at most one process (or None).")

        allocations = []
        alloc_cols = st.columns(min(num_r, 4))
        for idx, r in enumerate(custom_res):
            with alloc_cols[idx % min(num_r, 4)]:
                holder = st.selectbox(f"Holder of {r}:", ["None"] + custom_procs, index=min(idx + 1, len(custom_procs)) if idx < len(custom_procs) else 0, key=f"alloc_holder_{r}")
                if holder != "None":
                    allocations.append((r, holder))

        # Request edges builder (P -> R)
        st.write("#### 2. Process Requests (Who is waiting for which resource?)")
        requests = []
        req_cols = st.columns(min(num_p, 4))
        for idx, p in enumerate(custom_procs):
            with req_cols[idx % min(num_p, 4)]:
                req_for = st.multiselect(f"{p} requests:", custom_res, default=[custom_res[(idx + 1) % num_r]] if idx < num_r else [], key=f"req_p_{p}")
                for r in req_for:
                    requests.append((p, r))

        st.markdown("---")

        # Run custom detector
        custom_detector = SingleInstanceDetector(
            processes=custom_procs,
            resources=custom_res,
            allocations=allocations,
            requests=requests
        )
        custom_res_result = custom_detector.detect_cycles()

        # Display result
        if custom_res_result["is_deadlocked"]:
            st.error(f"🚨 **Deadlock Detected!** Deadlocked Processes: `{custom_res_result['deadlocked_processes']}`. Cycles: `{custom_res_result['wfg_cycles']}`")
        else:
            st.success("✅ **No Deadlock Detected!** Wait-For Graph is cycle-free.")

        # Visualizations
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.write("**Resource Allocation Graph:**")
            rag_dot = GraphVisualizer.generate_rag_dot(
                processes=custom_procs,
                resources=custom_res,
                allocations=allocations,
                requests=requests,
                deadlocked_processes=set(custom_res_result["deadlocked_processes"]),
                deadlocked_resources=set(custom_res_result["deadlocked_resources"])
            )
            st.graphviz_chart(rag_dot, use_container_width=True)

        with c_v2:
            st.write("**Wait-For Graph:**")
            wfg_edges_list = [(u, v, d.get("resource", "")) for u, v, d in custom_res_result["wfg_graph"].edges(data=True)]
            wfg_dot = GraphVisualizer.generate_wfg_dot(
                processes=custom_procs,
                edges=wfg_edges_list,
                deadlocked_processes=set(custom_res_result["deadlocked_processes"])
            )
            st.graphviz_chart(wfg_dot, use_container_width=True)

        # JSON Export / Import
        with st.expander("💾 Export / Import Scenario Configuration (JSON)"):
            export_payload = {
                "processes": custom_procs,
                "resources": custom_res,
                "allocations": allocations,
                "requests": requests
            }
            st.download_button(
                "📥 Download Scenario JSON",
                data=json.dumps(export_payload, indent=2),
                file_name="deadlock_scenario.json",
                mime="application/json"
            )

    else:
        st.subheader("Multi-Instance Matrix Playground")
        st.caption("Edit the Available Vector, Allocation Matrix, and Request Matrix in real-time.")

        col_p, col_r = st.columns(2)
        with col_p:
            num_proc = st.number_input("Number of Processes (n):", min_value=2, max_value=6, value=4, step=1, key="mi_num_p")
        with col_r:
            num_res = st.number_input("Number of Resource Types (m):", min_value=1, max_value=6, value=3, step=1, key="mi_num_r")

        p_names = [f"P{i}" for i in range(num_proc)]
        r_names = [f"R{j}" for j in range(num_res)]

        # Default initial data
        default_avail = [1] * num_res
        default_alloc = [[1 if i == j else 0 for j in range(num_res)] for i in range(num_proc)]
        default_req = [[1 if (i + 1) % num_proc == j else 0 for j in range(num_res)] for i in range(num_proc)]

        st.write("#### 1. Available Vector [m]")
        df_avail = pd.DataFrame([default_avail], columns=r_names, index=["Available"])
        edited_avail = st.data_editor(df_avail, use_container_width=True)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write("#### 2. Allocation Matrix [n × m]")
            df_alloc = pd.DataFrame(default_alloc, index=p_names, columns=r_names)
            edited_alloc = st.data_editor(df_alloc, use_container_width=True)

        with col_m2:
            st.write("#### 3. Request Matrix [n × m]")
            df_req = pd.DataFrame(default_req, index=p_names, columns=r_names)
            edited_req = st.data_editor(df_req, use_container_width=True)

        # Parse user inputs safely
        try:
            user_avail = [int(edited_avail.iloc[0][r]) for r in r_names]
            user_alloc = [[int(edited_alloc.loc[p, r]) for r in r_names] for p in p_names]
            user_req = [[int(edited_req.loc[p, r]) for r in r_names] for p in p_names]

            cust_mi_detector = MultiInstanceDetector(
                process_names=p_names,
                resource_names=r_names,
                available=user_avail,
                allocation=user_alloc,
                request=user_req
            )
            cust_mi_res = cust_mi_detector.detect_deadlock()

            if cust_mi_res["is_deadlocked"]:
                st.error(f"🚨 **Deadlock Detected!** Deadlocked Processes: `{cust_mi_res['deadlocked_processes']}`. Safe prefix: `{cust_mi_res['safe_sequence']}`")
            else:
                st.success(f"✅ **No Deadlock! Safe Completion Sequence:** `{' -> '.join(cust_mi_res['safe_sequence'])}`")

            # Graph preview
            st.write("**Bipartite Multi-Instance Allocation Graph:**")
            multi_dot = GraphVisualizer.generate_multi_rag_dot(
                process_names=p_names,
                resource_names=r_names,
                available=user_avail,
                allocation=user_alloc,
                request=user_req,
                deadlocked_processes=set(cust_mi_res["deadlocked_processes"])
            )
            st.graphviz_chart(multi_dot, use_container_width=True)

        except Exception as e:
            st.warning(f"Please ensure all matrix entries are valid integers. Error: {e}")


# ==============================================================================
# MODE 4: THEORY & OPERATING SYSTEMS PRIMER
# ==============================================================================
elif mode == "📚 Theory & Algorithm Primer":
    st.header("📚 Operating Systems Deadlock Theory & Cheatsheet")
    st.caption("A comprehensive guide to Deadlock Detection, Characterization, and Recovery.")

    with st.expander("🎯 The 4 Coffman Conditions for Deadlock", expanded=True):
        st.markdown("""
A deadlock state can occur if and only if the following four conditions hold simultaneously in a system:

1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode (only one process can use it at any given time).
2. **Hold and Wait:** A process must be holding at least one resource and simultaneously waiting to acquire additional resources currently held by other processes.
3. **No Preemption:** Resources cannot be forcibly taken away from a process; they can only be released voluntarily by the process after completing its task.
4. **Circular Wait:** A closed chain of processes exists: $P_0$ waits for a resource held by $P_1$, $P_1$ waits for $P_2$, ..., and $P_{n-1}$ waits for $P_0$.
""")

    with st.expander("🔍 Resource Allocation Graph (RAG) vs Wait-For Graph (WFG)", expanded=True):
        st.markdown(r"""
| Feature | Resource Allocation Graph (RAG) | Wait-For Graph (WFG) |
| :--- | :--- | :--- |
| **Nodes** | Processes ($P$) and Resources ($R$) | Processes only ($P$) |
| **Edges** | Assignment ($R \rightarrow P$) and Request ($P \rightarrow R$) | Wait-for ($P_i \rightarrow P_k$) |
| **Applicability** | Both Single-Instance and Multi-Instance | Strictly Single-Instance systems |
| **Cycle & Deadlock** | In single-instance: Cycle $\iff$ Deadlock.<br>In multi-instance: Cycle is a **necessary but NOT sufficient** condition. | Cycle $\iff$ Deadlock |
| **Time Complexity** | $O(V + E)$ cycle detection | $O(V^2)$ where $V = |P|$ |
""")

    with st.expander("📊 Multiple-Instance Deadlock Detection Algorithm (Work & Finish)", expanded=True):
        st.markdown(r"""
When resources have multiple instances, cycle detection alone is insufficient. We employ the **Silberschatz Work-Finish Algorithm**:

1. **Initialization:**
   - Let $\text{Work} = \text{Available}$ (vector of length $m$).
   - For $i = 0, \dots, n-1$:
     - If $\text{Allocation}[i] \neq [0, 0, \dots, 0]$, then $\text{Finish}[i] = \text{False}$;
     - Else $\text{Finish}[i] = \text{True}$.
2. **Search for candidate:**
   - Find an index $i$ such that:
     - $\text{Finish}[i] == \text{False}$
     - $\text{Request}[i] \le \text{Work}$
   - If no such $i$ exists, skip to step 4.
3. **Reclaim & Update:**
   - $\text{Work} = \text{Work} + \text{Allocation}[i]$
   - $\text{Finish}[i] = \text{True}$
   - Go back to Step 2.
4. **Conclusion:**
   - If $\text{Finish}[i] == \text{False}$ for any $i$, then the system is in a **Deadlock State**, and all processes with $\text{Finish}[i] == \text{False}$ are **Deadlocked**!
""")

    with st.expander("🩹 Deadlock Recovery Strategies", expanded=True):
        st.markdown("""
Once a deadlock has been detected, the operating system can recover using one of two primary strategies:

### 1. Process Termination
- **Abort all deadlocked processes:** Breaks the cycle immediately, but discards partial computations at high computational cost.
- **Abort one process at a time:** Selects a victim process, aborts it, frees its resources, and re-runs detection until the deadlock cycle is broken.
  - *Victim selection criteria:* Process holding the most resources, process with lowest priority, process furthest from completion, or process involved in the maximum number of cycles.

### 2. Resource Preemption
- **Victim Selection:** Determine which resources and which processes are to be preempted to minimize cost.
- **Rollback:** Return the victim process to a safe checkpoint state and restart it from there.
- **Starvation Prevention:** Ensure the same process is not consistently chosen as a victim by incorporating rollback counts into cost functions.
""")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94A3B8; font-size: 0.85rem;'>"
    "⚡ Built with Streamlit • Ready for Streamlit Community Cloud Deployment • Operating Systems Lab Tool"
    "</div>",
    unsafe_allow_html=True
)
