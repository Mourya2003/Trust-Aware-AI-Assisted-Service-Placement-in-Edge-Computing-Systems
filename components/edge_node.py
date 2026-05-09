import time
import random

class EdgeNode:
    """
    Represents a realistic Edge Node in the network.
    Stores node state, resources, workload, and trust metrics.
    """

    def __init__(self, node_id, initial_trust=50):

        self.node_id = node_id

        # -----------------------------
        # TRUST STATE
        # -----------------------------

        self.trust_score = float(initial_trust)

        self.success_count = 0
        self.failure_count = 0
        self.total_tasks = 0

        self.last_activity_time = time.time()

        # -----------------------------
        # RESOURCE STATE
        # -----------------------------

        # Simulated hardware capacity
        self.cpu_capacity = random.randint(4, 8)      # CPU cores
        self.memory_capacity = random.randint(4, 16)  # GB RAM

        # Dynamic runtime state
        self.cpu_usage = random.uniform(20, 60)
        self.memory_usage = random.uniform(20, 60)

        # Simulated network latency (ms)
        self.latency = random.uniform(10, 100)

        # Current workload level
        self.workload = random.uniform(0.1, 0.5)

    # -------------------------------------------------
    # UPDATE NODE RUNTIME CONDITIONS
    # -------------------------------------------------

    def simulate_runtime_state(self):

        """
        Simulates changing runtime conditions
        like CPU load, memory pressure, and latency.
        """

        self.cpu_usage += random.uniform(-10, 10)
        self.memory_usage += random.uniform(-8, 8)
        self.latency += random.uniform(-5, 5)
        self.workload += random.uniform(-0.1, 0.1)

        # Bound values safely

        self.cpu_usage = max(5, min(95, self.cpu_usage))
        self.memory_usage = max(5, min(95, self.memory_usage))
        self.latency = max(5, min(200, self.latency))
        self.workload = max(0.0, min(1.0, self.workload))

    # -------------------------------------------------
    # RESOURCE SCORE
    # -------------------------------------------------

    def get_resource_score(self):

        """
        Higher score means node has more free resources.
        """

        cpu_factor = 1 - (self.cpu_usage / 100)
        memory_factor = 1 - (self.memory_usage / 100)
        workload_factor = 1 - self.workload

        score = (
            0.4 * cpu_factor
            + 0.4 * memory_factor
            + 0.2 * workload_factor
        )

        return max(0.0, min(1.0, score))