# 🔒 Deadlock Detection Simulator (Streamlit)

An interactive, production-ready Deadlock Detection and Recovery Simulator built with Streamlit. Designed for computer science students, educators, and software engineers to visualize, analyze, and experiment with deadlock detection algorithms in Operating Systems.

---

## 🌟 Key Features

### 1. 🔄 Single-Instance Resource Allocation & Wait-For Graphs
- **Resource Allocation Graph (RAG):** Visualizes Processes (circles), Resources (rectangles), Assignment edges ($R \rightarrow P$), and Request edges ($P \rightarrow R$).
- **Wait-For Graph (WFG) Conversion:** Automatically derives direct process-to-process wait dependencies ($P_i \rightarrow P_k$).
- **Cycle Detection Engine:** DFS recursion stack algorithm that identifies and highlights elementary cycles and deadlocked processes in bold crimson.
- **Interactive DFS Stepper:** Step forward and backward through the cycle detection traversal with node visit color-coding (`UNVISITED`, `VISITING`, `VISITED`).

### 2. 📊 Multiple-Instance Resource Deadlock Detection
- **Silberschatz / Operating Systems Algorithm:** Implements the classic $O(m \times n^2)$ Work-Finish vector algorithm.
- **Dynamic Step-by-Step Execution Stepper:** Real-time visualization of intermediate Work vectors, Finish states, candidate evaluations, and resource release events.
- **Bipartite Capacity Visualizer:** Graphs processes and multi-instance resources with available and total capacity counts.

### 3. 🩹 Deadlock Recovery Simulator
- **Algorithmic Victim Selection:** Automatically pinpoints the optimal victim process (e.g. process participating in the most cycles, or process releasing the critical resources to break the deadlock).
- **One-Click Abortion & Rollback:** Simulates terminating a process, reclaiming its held resources, and verifying instant resolution.

### 4. 🛠️ Interactive Custom Playground
- **Graph Builder:** Add processes and resources, wire custom allocations and requests, and detect cycles on the fly.
- **Matrix Editor:** Live editable tables for `Available`, `Allocation`, and `Request` matrices.
- **Import / Export:** Export custom scenarios to JSON for sharing or homework assignments.

### 5. 📚 Built-in OS Theory & Primer
- Comprehensive guide on the 4 Coffman conditions, RAG vs. WFG comparative table, Banker's vs. Detection distinction, and recovery trade-offs.

---

## 🚀 Quickstart (Run Locally)

### 1. Prerequisites
Ensure Python 3.9+ is installed.

### 2. Installation
Clone the repository or navigate to the project directory:

```bash
cd deadlock_simulator
pip install -r requirements.txt
```

### 3. Launch Streamlit App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

Deploying this app to Streamlit Community Cloud takes less than 2 minutes:

1. **Push this folder to a GitHub Repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Deadlock Simulator"
   git remote add origin https://github.com/<your-username>/deadlock-simulator.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
   - Click **"New app"**.
   - Select your repository: `<your-username>/deadlock-simulator`.
   - Branch: `main`.
   - Main file path: `app.py`.
   - Click **"Deploy!"**.

Streamlit Cloud will automatically install dependencies from `requirements.txt` and render the Graphviz charts using native in-browser Viz.js rendering.

---

## 📁 Project Structure

```text
deadlock_simulator/
├── .streamlit/
│   └── config.toml          # Streamlit theme & UI configurations
├── algorithms/
│   ├── single_instance.py   # RAG/WFG building, DFS cycle detection, victim heuristic
│   └── multi_instance.py    # Silberschatz Work-Finish vector algorithm & simulation
├── presets.py               # Classic scenarios (Dining Philosophers, Silberschatz, etc.)
├── visualizer.py            # Graphviz DOT generators with color coding & highlight rules
├── test_algorithms.py       # Automated unit test suite
├── app.py                   # Main Streamlit web application
├── requirements.txt         # Pinned lightweight dependencies
└── README.md                # Documentation & Deployment Guide
```

---

## 🧪 Running Unit Tests

To verify detection correctness:
```bash
python test_algorithms.py
```

---

## 📜 License
MIT License. Open source for educational and academic use.
# deadlock-detection-simulator
