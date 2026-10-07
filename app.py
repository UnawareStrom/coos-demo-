import streamlit as st
import pandas as pd
from datetime import datetime
import random

# ─── Page Config ───
st.set_page_config(
    page_title="PCB & Process States",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #a8b2d1 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e6f1ff !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    .pcb-card {
        background: linear-gradient(135deg, #0a192f 0%, #112240 100%);
        border: 1px solid #233554;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 12px;
    }
    .pcb-card h4 { color: #64ffda; margin-bottom: 8px; }
    .pcb-card p { color: #a8b2d1; margin: 4px 0; font-size: 0.95rem; }
    .pcb-card .val { color: #ccd6f6; font-weight: 600; font-family: 'Consolas', monospace; }
    .state-badge {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px;
    }
    .state-new        { background: #1c1917; color: #d6d3d1; border: 1px solid #78716c; }
    .state-ready       { background: #172554; color: #60a5fa; border: 1px solid #2563eb; }
    .state-running     { background: #064e3b; color: #34d399; border: 1px solid #059669; }
    .state-waiting     { background: #1e1b4b; color: #a78bfa; border: 1px solid #7c3aed; }
    .state-terminated  { background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a192f 0%, #112240 100%) !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Simulated Process Data ───
PROCESS_TEMPLATES = [
    {"name": "init",        "user": "root",   "priority": 0,  "mem_kb": 2048},
    {"name": "bash",        "user": "user",   "priority": 5,  "mem_kb": 4096},
    {"name": "chrome",      "user": "user",   "priority": 10, "mem_kb": 524288},
    {"name": "vscode",      "user": "user",   "priority": 8,  "mem_kb": 262144},
    {"name": "python3",     "user": "user",   "priority": 7,  "mem_kb": 131072},
    {"name": "sshd",        "user": "root",   "priority": 3,  "mem_kb": 8192},
    {"name": "nginx",       "user": "www",    "priority": 4,  "mem_kb": 16384},
    {"name": "mysql",       "user": "mysql",  "priority": 6,  "mem_kb": 204800},
    {"name": "spotify",     "user": "user",   "priority": 12, "mem_kb": 307200},
    {"name": "explorer",    "user": "user",   "priority": 9,  "mem_kb": 102400},
    {"name": "gcc",         "user": "user",   "priority": 11, "mem_kb": 65536},
    {"name": "node",        "user": "user",   "priority": 7,  "mem_kb": 153600},
    {"name": "docker",      "user": "root",   "priority": 2,  "mem_kb": 409600},
    {"name": "systemd",     "user": "root",   "priority": 1,  "mem_kb": 10240},
    {"name": "cron",        "user": "root",   "priority": 4,  "mem_kb": 3072},
]

STATES = ["New", "Ready", "Running", "Waiting", "Terminated"]

def generate_processes():
    """Generate a set of simulated processes with randomised states and PCB fields."""
    if "processes" not in st.session_state:
        procs = []
        for i, tpl in enumerate(PROCESS_TEMPLATES):
            procs.append({
                "PID": (i + 1) * 100 + random.randint(0, 99),
                "Name": tpl["name"],
                "State": random.choice(["Ready", "Running", "Waiting"]),
                "Priority": tpl["priority"],
                "User": tpl["user"],
                "Mem (MB)": round(tpl["mem_kb"] / 1024, 2),
                "PC (hex)": hex(random.randint(0x400000, 0x7FFFFF)),
                "Registers": f"EAX={hex(random.randint(0,0xFFFF))} EBX={hex(random.randint(0,0xFFFF))}",
                "Open Files": random.randint(1, 30),
                "CPU Burst": random.randint(1, 20),
            })
        st.session_state.processes = procs

    return st.session_state.processes


def randomise_states():
    """Simulate a scheduling tick — randomly transition process states."""
    for p in st.session_state.processes:
        old = p["State"]
        if old == "New":
            p["State"] = "Ready"
        elif old == "Ready":
            p["State"] = random.choice(["Running", "Ready", "Ready"])
        elif old == "Running":
            p["State"] = random.choice(["Ready", "Waiting", "Terminated", "Running"])
        elif old == "Waiting":
            p["State"] = random.choice(["Ready", "Waiting"])
        elif old == "Terminated":
            # Respawn as New
            p["State"] = "New"
            p["PID"] = random.randint(100, 9999)
        # Update volatile PCB fields
        p["PC (hex)"] = hex(random.randint(0x400000, 0x7FFFFF))
        p["CPU Burst"] = random.randint(1, 20)


def state_badge(state: str) -> str:
    cls = f"state-{state.lower()}"
    return f'<span class="state-badge {cls}">{state}</span>'


# ─── Sidebar ───
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col_b:
        if st.button("⏩ Tick", use_container_width=True, help="Simulate one scheduling tick"):
            randomise_states()
            st.rerun()

    if st.button("🆕 Reset All Processes", use_container_width=True):
        if "processes" in st.session_state:
            del st.session_state.processes
        st.rerun()

    st.markdown("---")
    search = st.text_input("🔍 Search process", placeholder="e.g. chrome, python…")
    chosen_states = st.multiselect("Filter states", STATES, default=STATES)
    sort_col = st.selectbox("Sort by", ["Mem (MB)", "PID", "Priority", "CPU Burst"], index=0)
    sort_asc = st.toggle("Ascending", value=False)

    st.markdown("---")
    st.markdown("### 🔬 PCB Inspector")
    inspect_pid = st.number_input("Enter PID", min_value=0, value=0, step=1)

    st.markdown("---")
    st.caption(f"Simulated at: {datetime.now().strftime('%H:%M:%S')}")


# ─── Load & Filter ───
procs = generate_processes()
df = pd.DataFrame(procs)

if search:
    df = df[df['Name'].str.contains(search, case=False, na=False)]
if chosen_states:
    df = df[df['State'].isin(chosen_states)]
df = df.sort_values(by=sort_col, ascending=sort_asc).reset_index(drop=True)


# ─── Header ───
st.markdown("# ⚙️ Process Control Block Dashboard")
st.caption("Simulated process data  ·  Press **⏩ Tick** in the sidebar to simulate state transitions")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total", len(df))
m2.metric("New", len(df[df['State'] == 'New']))
m3.metric("Ready", len(df[df['State'] == 'Ready']))
m4.metric("Running", len(df[df['State'] == 'Running']))
m5.metric("Waiting", len(df[df['State'] == 'Waiting']))


# ─── State Diagram ───
with st.expander("📘 Process State Transition Diagram (Theory)", expanded=False):
    st.markdown("""
```mermaid
stateDiagram-v2
    [*] --> New : Process Created
    New --> Ready : Admitted
    Ready --> Running : Scheduler Dispatch
    Running --> Ready : Interrupt / Preempt
    Running --> Waiting : I/O or Event Wait
    Waiting --> Ready : I/O Complete
    Running --> Terminated : Exit
    Terminated --> [*]
```
""")
    st.info("💡 **PCB (Process Control Block)** stores: PID, State, Program Counter, CPU Registers, Memory Limits, Open Files, Scheduling Info, and Accounting Data. The OS kernel maintains one PCB per process.")


# ─── PCB Inspector ───
if inspect_pid > 0:
    st.markdown("---")
    st.markdown(f"## 🔬 PCB Details — PID `{inspect_pid}`")
    match = [p for p in procs if p["PID"] == inspect_pid]

    if match:
        p = match[0]
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""<div class="pcb-card">
                <h4>🪪 Process Identity</h4>
                <p>PID: <span class="val">{p['PID']}</span></p>
                <p>Name: <span class="val">{p['Name']}</span></p>
                <p>User: <span class="val">{p['User']}</span></p>
                <p>State: {state_badge(p['State'])}</p>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""<div class="pcb-card">
                <h4>📊 CPU Scheduling Info</h4>
                <p>Priority: <span class="val">{p['Priority']}</span></p>
                <p>CPU Burst: <span class="val">{p['CPU Burst']} ms</span></p>
                <p>Program Counter: <span class="val">{p['PC (hex)']}</span></p>
                <p>Registers: <span class="val">{p['Registers']}</span></p>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""<div class="pcb-card">
                <h4>💾 Memory & Resources</h4>
                <p>Memory: <span class="val">{p['Mem (MB)']} MB</span></p>
                <p>Open Files: <span class="val">{p['Open Files']}</span></p>
            </div>""", unsafe_allow_html=True)
    else:
        st.error("⚠️ No process with that PID found in the current simulation.")

    st.divider()


# ─── Charts + Table ───
st.markdown("---")
chart_col, table_col = st.columns([1, 2])

with chart_col:
    st.markdown("### 📊 State Distribution")
    state_counts = df['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    st.bar_chart(state_counts, x='State', y='Count', color='State', horizontal=True)

with table_col:
    st.markdown(f"### 📋 Process Table  ({len(df)} processes)")
    display_df = df[['PID', 'Name', 'State', 'Priority', 'Mem (MB)', 'CPU Burst', 'PC (hex)']].copy()
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "PID": st.column_config.NumberColumn("PID", width="small"),
            "Priority": st.column_config.NumberColumn("Priority", width="small"),
            "Mem (MB)": st.column_config.NumberColumn("Mem (MB)", format="%.2f"),
        }
    )


# ─── Top Memory ───
st.markdown("---")
st.markdown("### 🧠 Top 10 Memory Consumers")
top_mem = df.nlargest(10, 'Mem (MB)')[['Name', 'Mem (MB)']].reset_index(drop=True)
st.bar_chart(top_mem, x='Name', y='Mem (MB)')
