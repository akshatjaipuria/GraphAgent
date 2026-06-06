import sys
import json
from pathlib import Path

# Resolve path to sessions directory relative to this script
session_dir = Path(__file__).parent / "state" / "sessions"

def main():
    # Find latest session
    if not session_dir.exists():
        print(f"Sessions directory not found at: {session_dir}")
        return
        
    sessions = sorted([p for p in session_dir.iterdir() if p.is_dir() and p.name.startswith("s8-")], key=lambda x: x.stat().st_mtime)
    if not sessions:
        print("No sessions found in state/sessions/")
        return
    
    latest_session = sessions[-1]
    print(f"Analyzing latest session: {latest_session.name}")
    
    # Read query
    query_file = latest_session / "query.txt"
    if query_file.exists():
        print(f"Query: {query_file.read_text().strip()}")
        
    nodes_dir = latest_session / "nodes"
    if not nodes_dir.exists():
        print("No nodes directory found in session.")
        return
        
    # Read all nodes
    node_files = sorted(nodes_dir.glob("n_*.json"))
    nodes = []
    for f in node_files:
        try:
            with open(f) as fh:
                nodes.append(json.load(fh))
        except Exception:
            pass
            
    # Filter completed nodes that have timing info
    active_nodes = [n for n in nodes if n.get("status") == "complete" and "started_at" in n]
    active_nodes.sort(key=lambda x: x["started_at"])

    # Group overlapping nodes into concurrent batches
    batches = []
    for node in active_nodes:
        placed = False
        for batch in batches:
            # If this node overlaps with any node in the batch, add it to this batch
            if any(node["started_at"] < member["completed_at"] and member["started_at"] < node["completed_at"] for member in batch):
                batch.append(node)
                placed = True
                break
        if not placed:
            batches.append([node])

    # Filter for batches that actually ran in parallel (size > 1)
    parallel_batches = [b for b in batches if len(b) > 1]
    
    if not parallel_batches:
        print("No parallel execution layers detected in this session.")
        return

    for idx, batch in enumerate(parallel_batches, 1):
        print(f"\n--- Parallel Execution Layer {idx} ---")
        sum_time = 0.0
        earliest_start = float('inf')
        latest_complete = 0.0
        
        for n in batch:
            nid = n["node_id"]
            skill = n["skill"]
            elapsed = n["result"]["elapsed_s"]
            started = n["started_at"]
            completed = n["completed_at"]
            print(f"Node {nid} ({skill}): started at {started:.2f}, completed at {completed:.2f}, elapsed: {elapsed:.2f}s")
            
            sum_time += elapsed
            if started < earliest_start:
                earliest_start = started
            if completed > latest_complete:
                latest_complete = completed
                
        actual_parallel_time = latest_complete - earliest_start
        
        print("\n--- Concurrency Proof ---")
        print(f"Sum of execution times (Sequential): {sum_time:.2f} seconds")
        print(f"Actual Wall-Clock Time (Parallel):  {actual_parallel_time:.2f} seconds")
        print(f"Time saved by running in parallel:   {sum_time - actual_parallel_time:.2f} seconds ({((sum_time - actual_parallel_time)/sum_time)*100:.1f}% speedup!)")
    
if __name__ == "__main__":
    main()
