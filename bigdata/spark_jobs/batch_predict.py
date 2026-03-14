from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf, struct
from pyspark.sql.types import DoubleType, IntegerType, StringType
import pandas as pd
import joblib
import sys

# ---------------------------
# Batch Prediction Function
# ---------------------------
def run_batch_prediction(input_path, output_path, model_path):

    spark = SparkSession.builder \
        .appName("DistributedEnsemblePredict") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()

    sc = spark.sparkContext

    # Load + broadcast model
    model = joblib.load(model_path)
    broadcast_model = sc.broadcast(model)

    # Load data
    df = spark.read.parquet(input_path)

    # Get model feature order
    if hasattr(model, "feature_names_in_"):
        model_cols = list(model.feature_names_in_)
    else:
        model_cols = df.columns

    # Add missing columns
    for c in model_cols:
        if c not in df.columns:
            df = df.withColumn(c, df[df.columns[0]] * 0)

    # Keep only model columns in correct order
    df = df.select(model_cols)

    # ---------------------------
    # UDF: probability
    # ---------------------------
    @pandas_udf(DoubleType())
    def predict_prob(*cols):
        model = broadcast_model.value
        pdf = pd.concat(cols, axis=1)
        pdf.columns = model_cols
        return pd.Series(model.predict_proba(pdf)[:, 1])

    # ---------------------------
    # UDF: class
    # ---------------------------
    @pandas_udf(IntegerType())
    def predict_class(*cols):
        model = broadcast_model.value
        pdf = pd.concat(cols, axis=1)
        pdf.columns = model_cols
        return pd.Series(model.predict(pdf))

    # Apply predictions
    df = df.withColumn(
        "Conversion_Probability",
        predict_prob(*[df[c] for c in model_cols])
    )

    df = df.withColumn(
        "Converted_Prediction",
        predict_class(*[df[c] for c in model_cols])
    )

    # Decision logic
    df = df.withColumn(
        "Decision",
        (
            (df.Conversion_Probability > 0.8).cast("int")
        )
    )

    # Save
    df.write.mode("overwrite").parquet(output_path)

    print("Distributed prediction completed ✔")
    spark.stop()


# ---------------------------
# CLI Runner
# ---------------------------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: spark-submit batch_predict.py input_path output_path model.pkl")
    else:
        run_batch_prediction(sys.argv[1], sys.argv[2], sys.argv[3])