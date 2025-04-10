#!/bin/bash
queries=("open_orders" "top_dates" "pending_items" "top_customers")
for query in "${queries[@]}"; do
    docker-compose run cli-app --query "$query"
    docker-compose run cli-app --query "$query" --export
done