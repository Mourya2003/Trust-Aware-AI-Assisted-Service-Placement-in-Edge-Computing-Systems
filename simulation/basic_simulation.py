import random

from components.blockchain import Blockchain
from components.edge_node import EdgeNode
from components.trust_manager import TrustManager
from components.placement_controller import PlacementController


# --------------------------------
# CREATE SYSTEM
# --------------------------------

blockchain = Blockchain()

trust_manager = TrustManager()

placement_controller = PlacementController(blockchain)

validators = ["validator1", "validator2", "validator3"]

for v in validators:
    blockchain.add_validator(v)


# --------------------------------
# CREATE EDGE NODES
# --------------------------------

nodes = []

for i in range(6):

    node = EdgeNode(
        f"node_{i}",
        initial_trust=random.randint(60, 90)
    )

    node.total_tasks = random.randint(50, 120)

    node.success_count = int(
        node.total_tasks * random.uniform(0.80, 0.95)
    )

    node.failure_count = (
        node.total_tasks - node.success_count
    )

    nodes.append(node)


TOTAL_TASKS = 50


# --------------------------------
# REALISTIC TASK EXECUTION MODEL
# --------------------------------

def execute_task(node):

    """
    Simulates realistic task execution behavior.
    """

    reliability = (
        node.success_count / node.total_tasks
        if node.total_tasks > 0 else 0.5
    )

    cpu_penalty = node.cpu_usage / 100
    memory_penalty = node.memory_usage / 100
    latency_penalty = node.latency / 200

    trust_factor = node.trust_score / 100

    # --------------------------------
    # RESOURCE AWARENESS
    # --------------------------------

    resource_factor = (
        (1 - cpu_penalty)
        + (1 - memory_penalty)
    ) / 2

    # --------------------------------
    # SUCCESS PROBABILITY
    # --------------------------------

    success_probability = (
        0.35 * trust_factor
        + 0.25 * reliability
        + 0.40 * resource_factor
    )

    # Mild latency penalty

    success_probability -= (
        0.05 * latency_penalty
    )

    success_probability = max(
        0.05,
        min(0.95, success_probability)
    )

    return random.random() < success_probability


# --------------------------------
# METHOD 1 RANDOM
# --------------------------------

random_success = 0

for t in range(TOTAL_TASKS):

    node = random.choice(nodes)

    node.simulate_runtime_state()

    result = execute_task(node)

    if result:
        random_success += 1


# --------------------------------
# METHOD 2 TRUST ONLY
# --------------------------------

trust_success = 0

for t in range(TOTAL_TASKS):

    eligible = [
        n for n in nodes
        if n.trust_score >= 60
    ]

    if not eligible:
        continue

    node = max(
        eligible,
        key=lambda n: n.trust_score
    )

    node.simulate_runtime_state()

    result = execute_task(node)

    trust_manager.update_trust(node, result)

    if result:
        trust_success += 1


# --------------------------------
# METHOD 3 AI + TRUST
# --------------------------------

ai_success = 0

for t in range(TOTAL_TASKS):

    node, msg = placement_controller.request_placement(nodes)

    if node:

        result = execute_task(node)

        trust_manager.update_trust(node, result)

        if result:
            ai_success += 1


# --------------------------------
# RESULTS
# --------------------------------

print("\n------ EXPERIMENT RESULTS ------\n")

print("Total Tasks:", TOTAL_TASKS)

print("\nRandom Placement Success:", random_success)

print("Trust Placement Success:", trust_success)

print("AI + Trust Placement Success:", ai_success)

print("\nSuccess Rates")

print(
    "Random:",
    round(random_success / TOTAL_TASKS * 100, 2),
    "%"
)

print(
    "Trust:",
    round(trust_success / TOTAL_TASKS * 100, 2),
    "%"
)

print(
    "AI + Trust:",
    round(ai_success / TOTAL_TASKS * 100, 2),
    "%"
)

# --------------------------------
# BLOCKCHAIN SIZE
# --------------------------------

print("\nBlockchain Size:", len(blockchain.chain))

print("\nLatest Block Data:")

print(blockchain.chain[-1].data)