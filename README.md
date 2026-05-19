# Network Analysis LLM Agent

This is a conversational AI agent I built for analyzing gene expression data. You load a CSV, it builds a correlation network, finds the most connected genes and clusters, throws up an interactive 3D visualization in the browser, and lets you ask plain English questions about what it found. The whole thing runs locally with no API key needed.

Built this as an extension of an AI micro-credential I completed.

## What it actually does

You just talk to it. It figures out what you want and runs the right analysis. It can load datasets, compute Pearson correlations between every gene pair, build a network graph from those correlations, identify hub nodes (the most connected genes), cluster genes into pathways using weighted DBSCAN, and then answer questions about why the genes are behaving the way they are using a built-in biological knowledge base.

The 3D visualization opens in your browser and lets you rotate the network, hover over nodes to see their connections, and toggle clusters on and off from the legend.

## Project structure

```
network_agent/
├── agent.py       the main loop, handles routing and tool dispatch
├── tools.py       all the actual analysis functions
├── llm.py         connects to Ollama for local LLM inference
├── gene_kb.py     biological descriptions for 40 cancer relevant genes
└── data/          drop your CSV files here
```

## Setup

Install the Python dependencies:

```bash
pip install pandas numpy networkx scikit-learn matplotlib plotly requests
```

For the LLM you need Ollama. Download it at ollama.com, install it, then run:

```bash
ollama pull llama3.2
```

Ollama runs in the background automatically after that.

## Running it

```bash
cd network_agent
python agent.py
```

Then just type what you want:

```
You: load the data from data/your_file.csv or wherever your data files are stored
You: compute correlations with threshold 0.7
You: build the network
You: find the top 5 hub nodes
You: run clustering
You: summarize the results
You: visualize the network
You: what does it mean that TP53 is a hub node?
You: why do KRAS and EGFR move together?
You: what should my next steps be?
```

## How the architecture works

There are three layers. First a keyword router checks your input for obvious commands like load, correlate, cluster, visualize and dispatches them instantly without touching the LLM. If the router can't figure it out, Llama 3.2 takes over and outputs a JSON tool call that Python executes. For questions, the agent pulls the full analysis results plus relevant gene biology from the knowledge base, injects all of it as context, and generates a grounded answer from that rather than just guessing.

The clustering is weighted, meaning it uses actual correlation scores as distances rather than treating all connections the same. A 0.97 correlation becomes a very small distance, a 0.71 becomes a larger one, so genes group together based on how strongly they actually relate. Negative correlations like tumor suppressors are captured too since the code uses absolute values, so PTEN and RB1 still get linked to their pathways even though they move in the opposite direction.

## Dataset

I included a synthetic but realistic gene expression dataset with 200 patients and 40 genes across 6 real biological pathways including MAPK signaling, PI3K-AKT, p53, cell cycle regulation, NF-kB inflammation, and Wnt signaling. TP53 is the main hub connecting multiple pathways. GAPDH, ACTB, and B2M are housekeeping genes that should come out as singletons which is a good sanity check that the clustering is working right.

## Limitations

The chat quality depends on Llama 3.2 so very complex mechanistic questions might not get perfect answers. The biological knowledge base only covers 40 genes so anything outside that set gets structural analysis only. The correlation threshold and DBSCAN epsilon parameter both affect results significantly and may need tuning for different datasets.

## Stack

NetworkX for graph analysis, Plotly for the 3D visualization, scikit-learn for DBSCAN, Ollama with Llama 3.2 for local inference, pandas and NumPy for everything else.
