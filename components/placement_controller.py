import time
from ai.ai_predictor import ReliabilityPredictor


class PlacementController:
    """
    Implements the Service Placement Logic.
    Process: Filter -> Rank -> Select -> Record
    """

    def __init__(self, blockchain):

        self.blockchain = blockchain
        self.trust_threshold = 60.0

        # Placement weights
        self.w1 = 0.30   # Trust
        self.w2 = 0.20   # Reliability
        self.w3 = 0.15   # Resources
        self.w4 = 0.35   # AI prediction

        # AI predictor
        self.predictor = ReliabilityPredictor()

    def request_placement(self, nodes):

        """
        Selects the best node for a service.
        Returns: (Selected_Node, Success_Message)
        """

        # --------------------------------
        # 1. FILTER UNTRUSTED NODES
        # --------------------------------

        eligible_nodes = [n for n in nodes if n.trust_score >= self.trust_threshold]

        if not eligible_nodes:

            self.blockchain.add_block("PLACEMENT_FAILURE: No trusted nodes available.")

            return None, "CRITICAL FAILURE: All nodes are untrusted (<60)."

        # --------------------------------
        # 2. RANK NODES
        # --------------------------------

        ranked_nodes = []

        for node in eligible_nodes:

            # Simulate dynamic runtime conditions
            node.simulate_runtime_state()

            # Reliability
            reliability = (
                node.success_count / node.total_tasks
                if node.total_tasks > 0 else 0
            )

            # Dynamic resource score
            resource_score = node.get_resource_score()

            # Failure history
            failures = node.failure_count

            # AI prediction
            # (0 = reliable, 1 = likely failure)
            prediction = self.predictor.predict(
                node.trust_score,
                reliability,
                failures
            )

            predicted_reliability = 1 - prediction

            # --------------------------------
            # FINAL PLACEMENT SCORE
            # --------------------------------

            score = (
                self.w1 * (node.trust_score / 100.0)
                + self.w2 * reliability
                + self.w3 * resource_score
                + self.w4 * predicted_reliability
            )

            ranked_nodes.append((node, score))

        # --------------------------------
        # 3. SELECT BEST NODE
        # --------------------------------

        ranked_nodes.sort(key=lambda x: x[1], reverse=True)

        best_node, final_score = ranked_nodes[0]

        # --------------------------------
        # 4. RECORD ON BLOCKCHAIN
        # --------------------------------

        txn_data = (
            f"DEPLOY_SUCCESS: Assigned to "
            f"{best_node.node_id} "
            f"(Score: {final_score:.2f})"
        )

        self.blockchain.add_block(txn_data)

        return best_node, f"Service Deployed to {best_node.node_id}"