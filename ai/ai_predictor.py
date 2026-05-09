import joblib
import pandas as pd


class ReliabilityPredictor:

    def __init__(self):

        self.model = joblib.load("ai/trained_model.pkl")

    def predict(
        self,
        trust,
        success_rate,
        failures,
        latency=50,
        cpu_usage=50,
        memory_usage=50
    ):

        data = pd.DataFrame([{
            "trust_score": trust,
            "success_rate": success_rate,
            "failures": failures,
            "latency": latency,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage
        }])

        prediction = self.model.predict(data)[0]

        return prediction