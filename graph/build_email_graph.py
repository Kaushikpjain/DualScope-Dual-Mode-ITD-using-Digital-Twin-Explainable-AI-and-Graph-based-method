from pymongo import MongoClient
import networkx as nx
import json
import os

print("🔹 Building NetworkGraph structures for anomalous relationships...")

client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
events = db["events"]

# Initialize a directed graph
G = nx.DiGraph()

# Fetch a sample of recent events (in a real system, we'd process all or latest sliding window)
print("Querying event data...")
sample_events = events.find({"event_type": {"$in": ["EMAIL", "FILE", "USB"]}}).limit(100000)

for ev in sample_events:
    user = ev["user_id"]
    G.add_node(user, type="user", bipartite=0)
    
    if ev["event_type"] == "EMAIL" and "to" in ev and ev["to"]:
        # Handle multiple recipients
        recipients = ev["to"].split(';') if isinstance(ev["to"], str) else ev["to"]
        for recipient in recipients:
            recipient = recipient.strip()
            if recipient:
                G.add_node(recipient, type="user", bipartite=0)
                if G.has_edge(user, recipient):
                    G[user][recipient]['weight'] += 1
                else:
                    G.add_edge(user, recipient, weight=1, type="email")
                    
    elif ev["event_type"] == "FILE" and "filename" in ev:
        filename = ev["filename"]
        G.add_node(filename, type="file", bipartite=1)
        if G.has_edge(user, filename):
             G[user][filename]['weight'] += 1
        else:
             G.add_edge(user, filename, weight=1, type="file_access")
             
    elif ev["event_type"] == "USB" and "pc" in ev:
        device = f"{ev['pc']}_USB"
        G.add_node(device, type="device", bipartite=1)
        if G.has_edge(user, device):
             G[user][device]['weight'] += 1
        else:
             G.add_edge(user, device, weight=1, type="usb_connect")

print(f"Graph constructed: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Compute PageRank to find highly centralized nodes
print("Computing Centrality (Risk)...")
pagerank = nx.pagerank(G, weight='weight')
nx.set_node_attributes(G, pagerank, 'risk_score')

# Save graph to a JSON format that D3/React-force-graph can easily consume
data = nx.node_link_data(G)
os.makedirs("graph/data", exist_ok=True)
with open("graph/data/network_graph.json", "w") as f:
    json.dump(data, f)
    
print("✅ Graph data exported to graph/data/network_graph.json")
