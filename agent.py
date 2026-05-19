import pandas as pd
from llm import generate, extract_json
from tools import load_data, compute_correlations, build_network, find_hub_nodes, run_clustering, summarize_results, visualize_network_3d
from gene_kb import get_gene_context, GENE_KB
from probe_mapper import load_probe_annotations, annotate_genes


TOOLS_DESCRIPTION = """
Available tools:
1. load_data - input: filepath string. Loads a CSV file.
2. compute_correlations - input: threshold float (0.0 to 1.0). Builds correlation pairs.
3. build_network - input: none. Builds the network graph from correlations.
4. find_hubs - input: top_n integer. Finds most connected nodes.
5. run_clustering - input: none. Clusters the network nodes.
6. summarize - input: none. Returns a plain English summary.
7. visualize - input: none. Shows a plot of the network.
8. visualize_3d - input: none. Shows an interactive 3D plot of the network.
"""

PLANNER_SYSTEM = """You are a network analysis agent router.
Given the user's request, pick exactly one tool and return ONLY valid JSON like this:
{"tool": "tool_name", "input": "value"}
If no input is needed, use an empty string for input.
Do not add any text outside the JSON."""

# State that persists across tool calls
state = {
    "df": None,
    "corr_df": None,
    "graph": None,
    "hubs": None,
    "clusters": None
}
def keyword_route(user_query: str) -> dict:
    q = user_query.lower()
    
    # Check for questions FIRST before anything else
    if "what" in q or "why" in q or "mean" in q or "explain" in q or "tell me" in q or "?" in q:
        return {"tool": "chat", "input": user_query}
    
    elif "load" in q or "read" in q or "open" in q:
        words = user_query.split()
        filepath = next((w for w in words if ".csv" in w), "")
        return {"tool": "load_data", "input": filepath}
    elif "correlat" in q:
        import re
        nums = re.findall(r"0\.\d+", q)
        return {"tool": "compute_correlations", "input": nums[0] if nums else "0.7"}
    elif "visual" in q or "plot" in q or "show" in q or "3d" in q or "interactive" in q:
        return {"tool": "visualize_3d", "input": ""}
    elif "build" in q or "network" in q or "graph" in q:
        return {"tool": "build_network", "input": ""}
    elif "hub" in q or "connect" in q:
        import re
        nums = re.findall(r"\d+", q)
        return {"tool": "find_hubs", "input": nums[0] if nums else "5"}
    elif "cluster" in q:
        return {"tool": "run_clustering", "input": ""}
    elif "summar" in q:
        return {"tool": "summarize", "input": ""}
    return {}

def route_and_run(user_query: str) -> str:

     # Try keyword routing first — faster and more reliable than LLM for simple commands
    plan = keyword_route(user_query)
    
    # Fall back to LLM only if keyword routing couldn't figure it out
    if not plan:
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": TOOLS_DESCRIPTION + "\nUser request: " + user_query}
        ]
        raw = generate(messages, temperature=0.1)
        plan = extract_json(raw)

    if not plan or "tool" not in plan:
        return "Could not determine which tool to use. Try saying 'load', 'correlate', 'build network', 'find hubs', 'cluster', 'summarize', or 'visualize'."

    tool = plan.get("tool", "")
    inp = plan.get("input", "")


    # write the if/elif block that calls the right tool
    # based on the tool name, call the matching function from tools.py
    # store results in the state dict so later tools can use them
    # return a string result for each tool

    if tool == "load_data":
        try:
            state["df"] = load_data(inp)
            return f"Data loaded successfully from {inp}."
        except Exception as e:
            return f"Error loading data: {str(e)}"
    
    elif tool == "compute_correlations":
        try:
            threshold = float(inp)
            if state["df"] is None:
                return "No data loaded. Please load data first."
            state["corr_df"] = compute_correlations(state["df"], threshold)
            return f"Correlations computed with threshold {threshold}."
        except Exception as e:
            return f"Error computing correlations: {str(e)}"
    
    elif tool == "build_network":
        try:
            if state["corr_df"] is None:
                return "No correlation data. Please compute correlations first."
            state["graph"] = build_network(state["corr_df"])
            return "Network graph built successfully."
        except Exception as e:
            return f"Error building network: {str(e)}"
    
    elif tool == "find_hubs":
        try:
            top_n = int(inp)
            if state["graph"] is None:
                return "No graph built. Please build the network first."
            state["hubs"] = find_hub_nodes(state["graph"], top_n)
            return f"Top {top_n} hub nodes: {', '.join(str(h) for h in state['hubs'])}"
        except Exception as e:
            return f"Error finding hubs: {str(e)}"
    elif tool == "run_clustering":
        try:
            if state["graph"] is None:
                return "No graph built. Please build the network first."
            state["clusters"] = run_clustering(state["graph"])
            return "Clustering completed successfully."
        except Exception as e:
            return f"Error running clustering: {str(e)}"
    elif tool == "summarize":
        try:
            if state["graph"] is None:
                return "No graph built. Please build the network first."
            summary = summarize_results(state["graph"], state["hubs"], state["clusters"])
            return summary
        except Exception as e:
            return f"Error summarizing results: {str(e)}"
    
    elif tool == "visualize_3d":
        try:
            if state["graph"] is None:
                return "No graph built. Please build the network first."
            visualize_network_3d(state["graph"], state["clusters"])
            return "3D visualization opened in browser."
        except Exception as e:
            return f"Error visualizing 3D network: {str(e)}"
    
    elif tool == "chat":
        try:
            context = ""
            if state["graph"] is not None:
                context += f"Network has {state['graph'].number_of_nodes()} nodes and {state['graph'].number_of_edges()} edges.\n"
            if state["hubs"] is not None:
                context += f"Top hub nodes: {', '.join(str(h) for h in state['hubs'])}.\n"
            if state["clusters"] is not None:
                unique = set(v for v in state["clusters"].values() if v != -1)
                singletons = sum(1 for v in state["clusters"].values() if v == -1)
                context += f"Found {len(unique)} clusters and {singletons} singleton nodes.\n"
                for cid in unique:
                    members = [n for n, c in state["clusters"].items() if c == cid]
                    context += f"Cluster {cid}: {', '.join(str(m) for m in members)}\n"

            # Get biological context for all genes in the network
            if state["graph"] is not None:
                network_genes = list(state["graph"].nodes())
            
                # Try probe annotations first (for real GEO data with probe IDs)
                bio_context = annotate_genes(network_genes, PROBE_MAP)
            
                # Also check gene_kb for any named genes
                named_genes = [g for g in network_genes if g.upper() in GENE_KB]
                if named_genes:
                    bio_context += "\n" + get_gene_context(named_genes)
            
                if bio_context:
                    context += "\n" + bio_context

            if not context:
                context = "No analysis has been run yet."

            messages = [
                {"role": "system", "content":
                    "You are a computational biologist and network analysis expert. "
                    "Answer the user's question using the analysis results AND the biological context provided. "
                    "Explain not just what the network shows statistically, but WHY genes are connected based on their biology. "
                    "Be specific and reference actual gene names, biological processes, and mechanisms. "
                    "If something cannot be determined from the data, say so clearly."},
                {"role": "user", "content": f"Analysis results and biological context:\n{context}\n\nQuestion: {inp}"}
            ]
            return generate(messages, max_new_tokens=400, temperature=0.4)
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return f"Unknown tool: {tool}"

print("Loading probe annotations...")
PROBE_MAP = load_probe_annotations()
print(f"Loaded {len(PROBE_MAP)} probe annotations")

def run_agent():
    print("Network Analysis Agent ready. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        result = route_and_run(user_input)
        print(f"Agent: {result}\n")

if __name__ == "__main__":
    run_agent()