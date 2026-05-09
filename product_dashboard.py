import time
import random
import os
from components.blockchain import Blockchain
from components.edge_node import EdgeNode
from components.trust_manager import TrustManager   # FIXED: added import


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


print("Initializing EdgeGuard 10-Node Cluster...")

bc = Blockchain()
trust_manager = TrustManager()   # FIXED: create instance

for v in ["Admin_01", "ISP_Gateway", "Council_Node"]:
    bc.add_validator(v)

nodes = []

for i in range(1, 6):
    n = EdgeNode(f"Node-{i}")
    n.trust_score = random.randint(75, 90)
    nodes.append(n)

nodes.append(EdgeNode("Node-6"));  nodes[-1].trust_score = 30
nodes.append(EdgeNode("Node-7"));  nodes[-1].trust_score = 55
nodes.append(EdgeNode("Node-8"));  nodes[-1].trust_score = 50
nodes.append(EdgeNode("Node-9"));  nodes[-1].trust_score = 40
nodes.append(EdgeNode("Node-10")); nodes[-1].trust_score = 85

while True:
    clear_screen()
    print("=" * 60)
    print(f" EDGEGUARD CLUSTER STATUS | {len(nodes)} NODES ONLINE")
    print("=" * 60)
    print(f"{'ID':<10} | {'Trust':<6} | {'Status':<15}")
    print("-" * 40)

    for n in nodes:
        status = "SECURE" if n.trust_score >= 60 else "BLOCKED"
        print(f"{n.node_id:<10} | {n.trust_score:<6.0f} | {status}")

    print("-" * 40)
    print("\n1. Simulate Traffic (Random Node)")
    print("2. Deploy Service")
    print("3. View Ledger")
    print("4. Exit")

    choice = input("\nSelect: ")

    if choice == '1':
        target = random.choice(nodes)
        success = True if target.trust_score > 50 else random.choice([True, False])
        trust_manager.update_trust(target, success)   # FIXED: correct call
        bc.add_block(
            f"Task: {target.node_id} - {'Success' if success else 'Fail'}"
        )
        print(f"\n> Update: {target.node_id} Trust is now {target.trust_score:.1f}")
        input("Continue...")

    elif choice == '2':
        eligible = [n for n in nodes if n.trust_score >= 60]
        if eligible:
            best = max(eligible, key=lambda x: x.trust_score)
            print(f"\n> DEPLOYING TO: {best.node_id} (Score: {best.trust_score})")
            bc.add_block(f"DEPLOY: {best.node_id}")
        else:
            print("\n> FAILED: No secure nodes.")
        input("Continue...")

    elif choice == '3':
        for b in bc.chain:
            print(f"[{b.index}] {b.hash[:15]}... | {b.data}")
        input("Continue...")

    elif choice == '4':
        break