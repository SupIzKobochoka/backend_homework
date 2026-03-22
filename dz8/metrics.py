from prometheus_client import Counter, Histogram


PREDICTIONS_TOTAL = Counter(
    "predictions_total",
    "Total number of predictions",
    ["result"]
)

PREDICTION_DURATION_SECONDS = Histogram(
    "prediction_duration_seconds",
    "Time spent on ML model inference",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

PREDICTION_ERRORS_TOTAL = Counter(
    "prediction_errors_total",
    "Total number of prediction errors",
    ["error_type"],
)

DB_QUERY_DURATION_SECONDS = Histogram(
    "db_query_duration_seconds",
    "Time spent executing DB queries",
    ["query_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

MODEL_PREDICTION_PROBABILITY = Histogram(
    "model_prediction_probability",
    "Distribution of model violation probability",
    buckets=[i / 20 for i in range(0, 21)]
)
