# hespress-comments-analysis

# Initila commands

## Start zookeeper server

```bash
systemctl start zookeeper
```

## Start kafka server

```bash
systemctl start kafka
```

## Create a topic

```bash
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 --partitions 1 \
    --topic hespress_comments
```

## Start a producer

```bash