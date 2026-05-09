import random
import pandas as pd
import os
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from components.blockchain import Blockchain
from components.edge_node import EdgeNode
from components.trust_manager import TrustManager
from components.placement_controller import PlacementController
from ai.ai_predictor import ReliabilityPredictor


# --------------------------------
# PATHS
# --------------------------------

DATASET_PATH = "datasets/runtime_dataset.csv"
MODEL_PATH   = "ai/trained_model.pkl"

os.makedirs("datasets", exist_ok=True)
os.makedirs("graphs",   exist_ok=True)


# --------------------------------
# SYSTEM SETUP
# --------------------------------

blockchain          = Blockchain()
trust_manager       = TrustManager()
placement_controller = PlacementController(blockchain)

for v in ["validator1", "validator2", "validator3"]:
    blockchain.add_validator(v)


# --------------------------------
# CREATE EDGE NODES
# --------------------------------

nodes = []

for i in range(6):
    node = EdgeNode(f"node_{i}", initial_trust=random.randint(60, 90))
    node.total_tasks   = random.randint(50, 120)
    node.success_count = int(node.total_tasks * random.uniform(0.80, 0.95))
    node.failure_count = node.total_tasks - node.success_count
    nodes.append(node)


TOTAL_TASKS      = 100
RETRAIN_INTERVAL = 50

runtime_rows = []
last_saved   = 0


# --------------------------------
# ENERGY MODEL
# --------------------------------

def calculate_energy(node):
    """iFogSim-style energy: latency * CPU usage"""
    return node.latency * node.cpu_usage * 0.001


# --------------------------------
# TASK EXECUTION
# --------------------------------

def execute_task(node):

    reliability     = node.success_count / node.total_tasks if node.total_tasks > 0 else 0.5
    trust_factor    = node.trust_score / 100
    cpu_penalty     = node.cpu_usage / 100
    memory_penalty  = node.memory_usage / 100
    latency_penalty = node.latency / 200
    resource_factor = ((1 - cpu_penalty) + (1 - memory_penalty)) / 2

    success_prob = (
        0.35 * trust_factor
        + 0.25 * reliability
        + 0.40 * resource_factor
        - 0.05 * latency_penalty
    )
    success_prob = max(0.05, min(0.95, success_prob))
    result = random.random() < success_prob

    runtime_rows.append({
        "trust_score":  node.trust_score,
        "success_rate": reliability,
        "failures":     node.failure_count,
        "latency":      node.latency,
        "cpu_usage":    node.cpu_usage,
        "memory_usage": node.memory_usage,
        "failure_risk": 0 if result else 1
    })

    return result


# --------------------------------
# PERIODIC RETRAIN  — Fix #6
# --------------------------------

def retrain_model():
    """Save new rows and retrain RandomForest model."""
    global last_saved

    new_rows = runtime_rows[last_saved:]
    if not new_rows:
        return

    df_new = pd.DataFrame(new_rows)

    if os.path.exists(DATASET_PATH):
        old_df       = pd.read_csv(DATASET_PATH)
        df_combined  = pd.concat([old_df, df_new], ignore_index=True)
    else:
        df_combined  = df_new

    df_combined.to_csv(DATASET_PATH, index=False)
    last_saved = len(runtime_rows)

    if len(df_combined) < 20:
        print(f"[RETRAIN] Only {len(df_combined)} samples — skipping.\n")
        return

    try:
        X = df_combined.drop("failure_risk", axis=1)
        y = df_combined["failure_risk"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        joblib.dump(model, MODEL_PATH)

        # Reload predictor in placement controller
        placement_controller.predictor = ReliabilityPredictor()

        accuracy = model.score(X_test, y_test)
        print(f"[RETRAIN] Done — Samples: {len(df_combined)} | Accuracy: {accuracy:.2%}\n")

    except Exception as e:
        print(f"[RETRAIN] Failed: {e}\n")


# --------------------------------
# METHOD 1: RANDOM  — Fix #8
# --------------------------------

print("\n--- Method 1: Random Placement ---")
random_success = 0
random_energy  = 0.0

for t in range(TOTAL_TASKS):

    node = random.choice(nodes)
    node.simulate_runtime_state()
    result         = execute_task(node)
    random_energy += calculate_energy(node)

    # Fix #8: log to blockchain
    blockchain.add_block(
        f"RANDOM | {node.node_id} | {'SUCCESS' if result else 'FAIL'} | Trust:{node.trust_score:.1f}"
    )

    if result:
        random_success += 1

    if (t + 1) % RETRAIN_INTERVAL == 0:
        print(f"  [Task {t+1}] Retrain triggered...")
        retrain_model()


# --------------------------------
# METHOD 2: TRUST-BASED  — Fix #8
# --------------------------------

print("--- Method 2: Trust-Based Placement ---")
trust_success = 0
trust_energy  = 0.0

for t in range(TOTAL_TASKS):

    eligible = [n for n in nodes if n.trust_score >= 60]
    if not eligible:
        continue

    node = max(eligible, key=lambda n: n.trust_score)
    node.simulate_runtime_state()
    result        = execute_task(node)
    trust_manager.update_trust(node, result)
    trust_energy += calculate_energy(node)

    # Fix #8: log to blockchain
    blockchain.add_block(
        f"TRUST | {node.node_id} | {'SUCCESS' if result else 'FAIL'} | Trust:{node.trust_score:.1f}"
    )

    if result:
        trust_success += 1

    if (t + 1) % RETRAIN_INTERVAL == 0:
        print(f"  [Task {t+1}] Retrain triggered...")
        retrain_model()


# --------------------------------
# METHOD 3: AI + TRUST
# --------------------------------

print("--- Method 3: AI+Trust Placement ---")
ai_success = 0
ai_energy  = 0.0

for t in range(TOTAL_TASKS):

    node, msg = placement_controller.request_placement(nodes)

    if node:
        result     = execute_task(node)
        trust_manager.update_trust(node, result)
        ai_energy += calculate_energy(node)

        if result:
            ai_success += 1

    if (t + 1) % RETRAIN_INTERVAL == 0:
        print(f"  [Task {t+1}] Retrain triggered...")
        retrain_model()


# --------------------------------
# FINAL SAVE
# --------------------------------

retrain_model()


# --------------------------------
# RESULTS
# --------------------------------

print("\n========== EXPERIMENT RESULTS ==========\n")
print(f"Total Tasks per Method : {TOTAL_TASKS}")
print(f"Retrain every          : {RETRAIN_INTERVAL} tasks\n")

print(f"{'Method':<15} {'Success':>8} {'Rate':>8} {'Energy':>12}")
print("-" * 48)
print(f"{'Random':<15} {random_success:>8} {random_success/TOTAL_TASKS*100:>7.1f}% {random_energy:>12.3f}")
print(f"{'Trust':<15} {trust_success:>8}  {trust_success/TOTAL_TASKS*100:>7.1f}% {trust_energy:>12.3f}")
print(f"{'AI+Trust':<15} {ai_success:>8}  {ai_success/TOTAL_TASKS*100:>7.1f}% {ai_energy:>12.3f}")

print(f"\nBlockchain Ledger     : {len(blockchain.chain)} blocks")
print(f"Runtime Samples       : {len(runtime_rows)}")
print(f"Dataset Path          : {DATASET_PATH}")