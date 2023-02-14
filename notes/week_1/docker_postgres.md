# Docker

* Provides software without having to install in local machine
* Software is installed in isolated containers

**Docker Image**
* An executable package of software that includes everything needed to run an application.

## Why should we care about Docker?
* Reproducibility - Same enviromnment used - No reason to say "It worked on my machine :)"
* Local Experiments - Without having to install the applications / software in local computer
* Integration tests (CI/CD, use e.g. github actions, not covered in this course)
* Running pipelines on the cloud (AWS Batch, Kubernetes jobs)
* Serverless (usefull for processing data, one record at a time; AWS Lamda, Google functions)

## Examples using Docker

* docker run -it ubuntu bash
    * runs the image ubuntu in an interactive mode and executes the bash
* docker run -it python:3.9
    * starts the image python 3.9
    * can be used for python

* We can specifiy all the steps we want to have in our container within a **DockerFile** 
* We use the ```docker build``` command to build an image from a Dockerfile. e.g :
    * ```docker build -t test:myapp .``` (The ```.``` means that the image should be built in the folder where the dockerfile exists)
* To Run a docker image : ```docker run -it test:myapp ``` (```-it``` in the docker run command means the app should be ran in an interractive session. This allows interacting with the app (e.g if python you can type in some python scripts))
* To pass arguments - Include after the image name and before the . ->  ```docker run -it test:pandas 2023-01-13```

## Practice SQL with postgres

Step 1: pull the PostgreSQL docker image that we will use throughout the zoomcamp.
```docker pull postgres:13 ```
Step 2: Connect to postgres and create an empty database
	```docker run -it \
      -e POSTGRES_USER="root" \
      -e POSTGRES_PASSWORD="root" \
      -e POSTGRES_DB="ny_taxi" \
      -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \ # allows us to preserve the changes in our database, i.e. they are not deleted, when we stop the container
      -p 5432:5432 \ # specify the port, map a port on our host machine to a port of the conatiner
      postgres:13  # Postgres Docker Image
    ```
Step 3: After running the container postgres use pgcli to connect to postgres
* ``` pgcli -h localhost -p 5432 -U root -d ny_taxi ```
	* -p: port, -U: user, -d: database (set in the docker code above)
* If connection is successful - Run ```\dt``` to check if there are tables. Our database is empty because we have not updated any files.

Step 4: download the NYC taxi dataset
``` wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet ```

Convert the parquet file to csv

```
parquet_file = './yellow_tripdata_2021-01.parquet'
df = pd.read_parquet(parquet_file, engine = 'pyarrow')
df.to_csv(parquet_file.replace('parquet', 'csv'), index=False)
```

Step 5: Ingest the data to Postgres using Jupyter Notebook;
If all is successful use \dt in pgcli to list the tables, and \d yellow_taxi_data to describe the table yellow_taxi_data.
Check if the table has data: 

``` SELECT count(1) FROM yellow_taxi_data 
SELECT max(tpep_pickup_datetime), min(tpep_pickup_datetime), max(total_amount) FROM yellow_taxi_data
```

## Using PGADMIN
* pgcli is a command line interface for a quick look at the data, but not very comfortable
* Use webapplication pgAdmin which is a feature rich Open Source administration and development platform for PostgreSQL
* There is a docker image for pgAdmin
```
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    dpage/pgadmin4

```

We now have 2 containers: 1 for postgres and 1 for pgadmin4 but the two cannot communicate since they are in separate docker containers.

## Connecting Postgres with PGAdmin

We need to connect them so they can communicate.

Step 1: Create a network: 
```docker create pg-network```

Step 2: When we run postgres, we have to specify that this container runs in this network 
```
docker run -it \
    -e POSTGRES_USER="root" \     # environmental configurations
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi \     # name of the database
    -v ny_taxi_postgres_data:"./ny_taxi_postgres_data:/var/lib/postgresql/data:rw" 
	-p 5432:5432 \ 
    --network=pgnetwork
    --name pg database
    postgres:13
```
Step 3. Run pgAdmin in the same network

```
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name=admin
    dpage/pgadmin4 
```

Step 4: Access PgAdmin via "localhost:8080" in the browser
	* pgadmin should open
	* Login with: email: admin@admin.com, password: root
	* Create a new server and configure

## Put Commands from the Notebook to a Script 

* put the commands from the jupyter notebook into a script called pipeline.py
* In order to do that use jupyter:
	```jupyter nbconvert --to=script upload-data.ipynb```
* Rename script to "ingest_data.py"
	* Clean the script
	* Add argparse and change specific names with parameters
* run the script:
	```
	URL="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv"
	python ingest_data.py \
	--user=root \
	--password=root \
	--host=localhost \
	--port=5432 \
	--db=ny_taxi \
	--table_name=yellow_taxi_trips \
	--url=${URL}
	```

## Now use this in Docker
* write Dockerfile
* Build the image: ```docker build -t taxi_ingest:001 .```
* Run it:
	``` 
	docker run -it \ 
	--network=pg-network \
	taxi_ingest:001 \
	--user=root \
	--password=root \
	--host=pg-database \
	--port=5432 \
	--db=ny_taxi \
	--table_name=yellow_taxi_trips \
	--url=${URL}
	```

## Docker compose
* Specify 1 yaml file with configurations of the two above container
* In general the configurations of multiple configurations are put in one file
```
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw" # host path:container path:mode(read-write)
    ports:
      - "5432:5432" # local port:container port
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"
```
* The two containers are then automatically part of one network
* Run ```docker-compose up``` in the terminal
* Run ```docker-compose down``` to end it
* It can be run in detached mode, i.e. after execution, we can use the terminal : ```docker-compose up -d```

## SQL
* data: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* upload the data to postgres: upload-taxi-zone-data.ipynb
* call the table "zones"
* When running docker-compose, we can select the "Query" tool and use SQL queries to access the data, e.g.:
```SELECT * FROM zones;``` 



