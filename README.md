## Data Engineering Take-Home Task

Current Approach - Extract the data from transaction tables incremetally based on the updated at field & for the dimension table we are truncate and loading due to its size


##Data Gaps 
potential data issue not all orderid as present in the order items due to randomness - this casue the pending order item oupt to be null most of the times 
select distinct a.order_id,b.order_id FROM operations.order_items a
right join operations.orders b
on a.order_id=b.order_id


Export Query - 
sample - docker-compose run cli-app --query top_customers --export ,
docker-compose run cli-app --query pending_items --export ,
docker-compose run cli-app --query top_dates --export,
docker-compose run cli-app --query open_orders --export
