from ai.ai_predictor import ReliabilityPredictor


class PlacementController:

    def __init__(self, blockchain):

        self.blockchain = blockchain
        self.trust_threshold = 60.0

        self.w1 = 0.30
        self.w2 = 0.20
        self.w3 = 0.15
        self.w4 = 0.35

        self.predictor = ReliabilityPredictor()

    def request_placement(self, nodes):

        # --------------------------------
        # 1. FILTER UNTRUSTED NODES
        # --------------------------------

        eligible_nodes = [
            n for n in nodes
            if n.trust_score >= self.trust_threshold
        ]

        if not eligible_nodes:
            self.blockchain.add_block(
                "PLACEMENT_FAILURE: No trusted nodes available."
            )
            return None, "CRITICAL FAILURE: All nodes are untrusted (<60)."

        # --------------------------------
        # 2. RANK NODES
        # --------------------------------

        ranked_nodes = []

        for node in eligible_nodes:

            node.simulate_runtime_state()

            reliability = (
                node.success_count / node.total_tasks
                if node.total_tasks > 0 else 0
            )

            resource_score = node.get_resource_score()

            failures = node.failure_count

            # FIXED: passing all 6 features to AI predictor
            prediction = self.predictor.predict(
                node.trust_score,
                reliability,
                failures,
                node.latency,
                node.cpu_usage,
                node.memory_usage
            )

            predicted_reliability = 1 - prediction

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

        self.blockchain.add_block(
            f"AI_DEPLOY | {best_node.node_id} | Score:{final_score:.2f} | Trust:{best_node.trust_score:.1f}"
        )

        return best_node, f"Service Deployed to {best_node.node_id}"