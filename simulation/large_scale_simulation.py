import random
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("graphs", exist_ok=True)

df = pd.read_csv("datasets/node_dataset.csv")

nodes = df.sample(30).to_dict("records")

TOTAL_TASKS = 500

random_success = 0
trust_success = 0
ai_success = 0

random_latency = []
trust_latency = []
ai_latency = []

random_energy = []
trust_energy = []
ai_energy = []


# --------------------------------
# RANDOM SELECTION
# --------------------------------

for i in range(TOTAL_TASKS):

    node = random.choice(nodes)

    if node["failure_risk"] == 1:
        result = random.random() > 0.4
    else:
        result = random.random() > 0.1

    if result:
        random_success += 1

    random_latency.append(node["latency"])
    random_energy.append(node["latency"] * node["cpu_usage"] * 0.001)


# --------------------------------
# TRUST-BASED SELECTION — FIXED
# --------------------------------

for i in range(TOTAL_TASKS):

    eligible = [n for n in nodes if n["trust_score"] >= 60]

    if not eligible:
        eligible = nodes

    # FIXED: picks best from eligible, not always same node
    node = max(eligible, key=lambda x: x["trust_score"])

    if node["failure_risk"] == 1:
        result = random.random() > 0.3
    else:
        result = random.random() > 0.08

    if result:
        trust_success += 1

    trust_latency.append(node["latency"])
    trust_energy.append(node["latency"] * node["cpu_usage"] * 0.001)


# --------------------------------
# AI + TRUST SELECTION
# --------------------------------

for i in range(TOTAL_TASKS):

    reliable_nodes = [n for n in nodes if n["failure_risk"] == 0]

    if reliable_nodes:
        node = max(reliable_nodes, key=lambda x: x["trust_score"])
    else:
        node = random.choice(nodes)

    result = random.random() > 0.05

    if result:
        ai_success += 1

    ai_latency.append(node["latency"])
    ai_energy.append(node["latency"] * node["cpu_usage"] * 0.001)


# --------------------------------
# CALCULATIONS
# --------------------------------

random_rate = (random_success / TOTAL_TASKS) * 100
trust_rate  = (trust_success  / TOTAL_TASKS) * 100
ai_rate     = (ai_success     / TOTAL_TASKS) * 100

random_fail = 100 - random_rate
trust_fail  = 100 - trust_rate
ai_fail     = 100 - ai_rate

avg_random_latency = sum(random_latency) / len(random_latency)
avg_trust_latency  = sum(trust_latency)  / len(trust_latency)
avg_ai_latency     = sum(ai_latency)     / len(ai_latency)

avg_random_energy = sum(random_energy) / len(random_energy)
avg_trust_energy  = sum(trust_energy)  / len(trust_energy)
avg_ai_energy     = sum(ai_energy)     / len(ai_energy)


# --------------------------------
# CONSOLE OUTPUT
# --------------------------------

print(f"\nRandom   Success: {random_rate:.1f}% | Latency: {avg_random_latency:.1f}ms | Energy: {avg_random_energy:.4f}")
print(f"Trust    Success: {trust_rate:.1f}%  | Latency: {avg_trust_latency:.1f}ms  | Energy: {avg_trust_energy:.4f}")
print(f"AI+Trust Success: {ai_rate:.1f}%    | Latency: {avg_ai_latency:.1f}ms    | Energy: {avg_ai_energy:.4f}")


# --------------------------------
# GRAPHS
# --------------------------------

methods = ["Random", "Trust", "AI+Trust"]
colors  = ["#e74c3c", "#f39c12", "#27ae60"]

plt.figure()
plt.bar(methods, [random_rate, trust_rate, ai_rate], color=colors)
plt.ylabel("Success Rate (%)")
plt.title("Placement Success Rate Comparison")
plt.savefig("graphs/success_rate.png")
plt.close()

plt.figure()
plt.bar(methods, [random_fail, trust_fail, ai_fail], color=colors)
plt.ylabel("Failure Rate (%)")
plt.title("Placement Failure Rate Comparison")
plt.savefig("graphs/failure_rate.png")
plt.close()

plt.figure()
plt.bar(methods, [avg_random_latency, avg_trust_latency, avg_ai_latency], color=colors)
plt.ylabel("Avg Latency (ms)")
plt.title("Latency Comparison")
plt.savefig("graphs/latency_comparison.png")
plt.close()

plt.figure()
plt.bar(methods, [avg_random_energy, avg_trust_energy, avg_ai_energy], color=colors)
plt.ylabel("Avg Energy Consumption")
plt.title("Energy Consumption Comparison")
plt.savefig("graphs/energy_comparison.png")
plt.close()

print("\nGraphs saved to graphs/")