from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import sys

def run_preprocess_job(input_path, output_path):

    spark = SparkSession.builder \
        .appName("DistributedPreprocessing") \
        .getOrCreate()

    df = spark.read.csv(input_path, header=True, inferSchema=True)

    # ---------------------------
    # Missing Value Handling
    # ---------------------------
    for c, t in df.dtypes:
        if t in ("int", "double", "float", "long"):
            df = df.withColumn(c, when(col(c).isNull(), 0).otherwise(col(c)))
        else:
            df = df.withColumn(c, when(col(c).isNull(), "Unknown").otherwise(col(c)))

    # ---------------------------
    # Remove duplicates
    # ---------------------------
    df = df.dropDuplicates()

    # ---------------------------
    # Remove useless columns
    # ---------------------------
    drop_cols = [
        "id","lead_number","prospect_id","mql_id",
        "seller_id","sdr_id","sr_id",
        "sessionid","userid","timestamp","won_date"
    ]

    for c in drop_cols:
        if c in df.columns:
            df = df.drop(c)

    # ---------------------------
    # Save optimized format
    # ---------------------------
    df.write.mode("overwrite").parquet(output_path)

    print("Preprocessing completed ✔")
    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit preprocess.py input.csv output_folder")
    else:
        run_preprocess_job(sys.argv[1], sys.argv[2])