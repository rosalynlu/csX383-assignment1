import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import os

# -------------------------
# DB CONNECTION (matches  utils/db.py env vars)
# -------------------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "grocery_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

# -------------------------
# LOAD LATENCY DATA
# -------------------------
def load_latency_data():
    query = """
        SELECT request_type, total_duration_ms, start_time
        FROM analytics
        WHERE total_duration_ms IS NOT NULL
        ORDER BY start_time;
    """

    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    return df

# -------------------------
# HISTOGRAM
# -------------------------
def plot_histogram(df):
    plt.figure()
    plt.hist(df["total_duration_ms"], bins=20)
    plt.title("Latency Distribution (All Requests)")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.savefig("latency_histogram.png")
    plt.close()

# -------------------------
# BOXPLOT BY REQUEST TYPE
# -------------------------
def plot_boxplot(df):
    plt.figure()
    df.boxplot(column="total_duration_ms", by="request_type")
    plt.title("Latency by Request Type")
    plt.suptitle("")
    plt.ylabel("Latency (ms)")
    plt.savefig("latency_boxplot.png")
    plt.close()

# -------------------------
# SUMMARY STATS 
# -------------------------
def write_summary(df):
    summary = df.groupby("request_type")["total_duration_ms"].describe()

    with open("latency_summary.txt", "w") as f:
        f.write("Latency Summary Statistics\n\n")
        f.write(str(summary))

# -------------------------
# MAIN
# -------------------------
def main():
    print("Loading latency data from database...")
    df = load_latency_data()

    if df.empty:
        print("No latency data found in analytics table.")
        return

    print("Generating plots...")
    plot_histogram(df)
    plot_boxplot(df)
    write_summary(df)

    print("Done!")
    print("Generated:")
    print(" - latency_histogram.png")
    print(" - latency_boxplot.png")
    print(" - latency_summary.txt")

if __name__ == "__main__":
    main()
