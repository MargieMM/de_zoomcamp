## Week 1 Homework

## Question 1. Knowing docker tags
```
docker build --help
```
``` --iidfile string ``` -  Write the image ID to the file

## Question 2. Understanding docker first run 
```
import os
os.system("pip list")
```
How many python packages/modules are installed? -- 3
```
Package     Version
----------  -------
pip         22.0.4
setuptools  58.1.0
wheel       0.38.4
```

# Prepare Postgres

I reused the ingest_data.py file from learning docker and made changes to be able to ingest the green taxi trips. 

```
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v c:/users/rombo/de_zoomcamp/homework/week1/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name=pg-database \
    postgres:13
```
```
 python ingest_green_taxi_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=green_taxi_trips \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz"
```

To ingest the taxi zone data I used the taxi_zones.py file
```
python taxi_zones.py 
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=taxi_zone_lookup 
```
## Question 3. Count records 

How many taxi trips were totally made on January 15?

Query

```sql
SELECT 
    date(lpep_pickup_datetime) AS pickup_date,
    date(lpep_dropoff_datetime) AS dropoff_date,
    COUNT(*) AS number_of_trips
FROM green_taxi_trips
WHERE date(lpep_pickup_datetime)='2019-01-15' 
    AND date(lpep_dropoff_datetime)='2019-01-15'
GROUP BY date(lpep_pickup_datetime), date(lpep_dropoff_datetime)
```
Output:

```
pickup_date     dropoff_date    number_of_trips
----------      ------------    ---------------
"2019-01-15"	"2019-01-15"	20530
```

## Question 4. Largest trip for each day

Which was the day with the largest trip distance
```sql
SELECT 
	DATE(lpep_pickup_datetime) AS pickup_date,
	MAX(trip_distance) AS largest_trip_distance
FROM green_taxi_trips
GROUP BY date(lpep_pickup_datetime)
ORDER BY largest_trip DESC
LIMIT 1
```

Output:

```
pickup_date     largest_trip_distance
----------      ---------------------
2019-01-15  	117.99
```

## Question 5. The number of passengers

In 2019-01-01 how many trips had 2 and 3 passengers?

```sql
SELECT 
	passenger_count,
	COUNT(1) AS Num_trips
FROM green_taxi_trips
WHERE date(lpep_pickup_datetime)='2019-01-01' AND passenger_count  in (2,3)
GROUP BY passenger_count
```

Output:

```
passenger_count     Num_trips
---------------     ---------
2             	    1282
3             	    254
```
## Question 6. Largest tip

For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip?
We want the name of the zone, not the id.

```sql
SELECT
	do_zone."Zone" AS drop_off_zone,
	MAX(tip_amount) AS largest_tip
FROM green_taxi_trips gtt
LEFT JOIN taxi_zone_lookup  pu_zone ON gtt."PULocationID" = pu_zone."LocationID"
LEFT JOIN taxi_zone_lookup  do_zone ON gtt."DOLocationID" = do_zone."LocationID"
WHERE pu_zone."Zone" = 'Astoria'
GROUP BY drop_off_zone
ORDER BY largest_tip DESC
LIMIT 1
```

Output:

```
drop_off_zone                              largest_tip
---------------                            ---------
Long Island City/Queens Plaza              88
```