# Hespress Comment Sentiment Analysis

This project performs sentiment analysis on comments scraped from Hespress articles. It uses a big data pipeline
consisting of Apache Kafka, Apache Spark, HDFS, and MongoDB to process and store the data.

## Architecture

The project follows a hybrid batch and real-time processing architecture:

1. **Data Source (Hesspress):** Comments are scraped from Hespress articles using a custom scraper.

2. **Data Ingestion (Kafka):** Scraped comments are streamed into a Kafka topic.

3. **Batch Processing (Spark):**
    - Spark reads comments from the Kafka topic in batches.
    - Preprocessing steps (cleaning, normalization) are applied.
    - Sentiment is predicted using a pre-trained deep learning model.
    - Processed comments, including sentiment, are stored in MongoDB.

4. **Real-time Processing (Spark Streaming):**
    - Spark Streaming consumes comments from the same Kafka topic in real time.
    - Preprocessing and sentiment prediction are performed similarly to the batch layer.
    - Real-time sentiment results are stored in MongoDB.

5. **Storage (MongoDB):** MongoDB stores both batch and real-time processed comments.

6. **Persistent Storage (HDFS):** The raw comments ingested from Kafka are stored on HDFS for data durability and
   potential replay/reprocessing.

## Project Structure

```
hespress-comments-analysis/
├── config/             # Configuration files
│   ├── kafka_config.py
│   └── mongodb_config.py
├── models/            # Data models
│   └── comment.py
├── processors/         # Data processing logic
│   ├── batch_processor.py
│   └── spark_processor.py
├── storage/           # Data storage handlers
│   ├── hdfs_handler.py
│   ├── kafka_handler.py
│   └── mongodb_handler.py
├── utils/              # Utility functions
│   └── scrapper.py
│   └── sentiments_processor.py
├── model/      # Sentiment Analysis Model files
│   ├── sentiment_model.h5
│   ├── tokenizer.json
│   └── label_encoder.pkl
└── main.py             # Main application entry point
└── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Getting Started

### Prerequisites

* **Python 3.7+:** Make sure you have a compatible Python version installed.
* **Java:** Required for Kafka and Spark.
* **Hadoop and HDFS:** Install and configure Hadoop and HDFS.
* **Apache Kafka:** Install and configure Kafka.
* **Apache Spark:** Install and configure Spark.
* **MongoDB:** Install and run MongoDB.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abdellatif-laghjaj/hespress-comments-analysis.git
   cd hespress-comments-analysis
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Model Files:** Make sure to include the pre-trained model files (`sentiment_model.h5`, `tokenizer.json`, and
   `label_encoder.pkl`) in the `model/` directory.

5. **Configuration:**
    - Update `config/kafka_config.py` with your Kafka bootstrap servers and topic information.
    - Update `config/mongodb_config.py` with your MongoDB connection details.
    - Update HDFS details in your `main.py` and `hdfs_handler.py`.

### Running the Application

1. **Start ZooKeeper and Kafka:** Use the appropriate commands to start your ZooKeeper and Kafka servers.

```bash
sudo systemctl start zookeeper
```

```bash
sudo systemctl start kafka
```

2. **Start MongoDB:** Make sure your MongoDB server is running.

```bash
sudo systemctl start mongod
```

3. **Start HDFS:** Ensure your Hadoop and HDFS services are running.

```bash
start-all.sh
```

4. **Run the main application:**

```bash
python main.py
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.