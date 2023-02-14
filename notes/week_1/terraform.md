# Terraform
* What is Terraform?
	* open source by HashiCorp
	* used for provisioning infrastructure (e.g. virtual machines, storage, networking resources, ...) resources
	* Provides a consistent CLI workflow to manage hundreds of cloud services  
	* Supports DevOps best practices, with IaC approach
	* Manages configuration files in source control to maintain an ideal provisioning state for testing and production environments
* What is IaC
	* Infrastructure-as-code
	* A framework, that allows you to build, change, and manage your infrastructure in a safe, consistent and repeatable way by defining resource configurations that you can version, reuse, and share
	* As a git version control, but for infrastructure
* Some Advantages
	* Infrastructure lifecycle management
	* version control commits
	* Very usefull for stack-based deployments, and with cloud providers such as AWS, GCP, Azure, K8S,...
	* State-based approach to track resource changes throughout deployments

## Local Setup for Terraform and GCP
### Terraform 
* Installation: [https://www.terraform.io/downloads](https://www.terraform.io/downloads)

### GCP

For this course the free version (up to 300 Euro credis) is used.

1. Create an account with your Google E-mail ID
2. Setup your first project, e.g. "DTC DE Course", and note down the project ID
	* Make the project ID unique
	* The project ID can be changed py pressing the refresh button
	* Go to this project
	* Go to IAM & Admin -> Service Accounts
	* "Service Accounts" is an account for services

3. Setup service account & authentification for this project, and downloaded auth-keys:
![Service Account](gcp_1.png "service account")

	* Use role "Viewer" to begin
	* When pressing "done":

![keys](gcp_2.png "keys")

	* There are no keys generated yet
	* Go to actions -> Manage keys -> ADD KEY
	* keep json
	* Download the generated .json
4. Download SDK for local setup
	* Check if gcloud is already installed: ```gcloud -v```
	* If not install it: [SDK](cloud.google.com/sdk/docs/quickstart)
5. Set environment variable to point to your downloaded GCP auth-keys:
	* Go to the folder containing the downloaded key

	```
	export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"

	# Refresh token, and verfy authetification
	gcloud auth application-default login
	```

	* This is need, so that Google knows that is is your key
	* This will open the browser to authenticate

When this is done the local computer can interact with the cloud!


### Create infrastructure for our project with Terraform

Create two resourses in the Google environment: 
**Project infrastructure for our project with Terraform**
* Google Cloud Storage (GCS): Data Lake
	* In a "Data Lake" all the raw data is stored
	* In an organized way
* BigQuery: Data Warehouse
	* Data is more structured (e.g. tables,...)

Add permissions for your service account
![permissions](gcp_3.png "add permissions")

* In a real production these permissions would be restricted to a particular bucket
* In production the roles will be customized
* enable API to interact between local environment and the cloud environment
	* https://console.cloud.google.com/apis/library/iam.googleapis.com
	* https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

# Creating GCP Structure with Terraform

* How to define resources in terraform?
	* main.tf
	* to start, you need a terraform resource (terraform {}), which contains:
		* terraform version
		* backend, in this example "local", in prduction you use your cloud environment
		* required prividers, this is optional (think of it as in Python importing a library)
	* provider section
		* terraform relies on pluggins called providers, to interact with cloud providers
		* adds a set of predefined resourse data sources
	* resource
		* contains arguments to configure the resource
	* the main.tf file contains variables from the variables.tf file, written as "var."
		* variables.tf
			* contains "locals", which are constants
			* variables are generally passed at run-time
			* variables that contain "default" are optional run-time variables
			* variables without "default" are mandantory
* Terraform has only few execution commands:
	1. terraform init: initialize and install
	2. terraform plan: Match changes against the prviouos state (if you e.g. add another resource)
	3. terraform apply: Apply changes to the cloud
	4. terraform destroy: Remove your stack from the cloud (usually it is advisable to destroy your resourses, until you need them next time)
		* The next time you use "terraform apply" you will have back your state
		* This is a great advantage of using terraform, which has a state file
* After running "terraform init" some more files are in the folder
	* .terraform: like any package manager, manages all packages
	* .terraform-version
	* .terraform-lock.hcl 
* When running "terraform plan" you need to type the project id, because this is a variable where no default was set
	* ```terraform plan -var="project=<project-id>"```
* Then two new resources are created
	* BigQuery
	* Bucket
* Then in "terraform apply" you have to confirm the changes and then the new resources are created
	* To confirm: 1. type the project id,, 2. type "yes"

# How to set up an Environment in Google Cloud
**Setup an Instance in Google Cloud**

* Go to the project
* On the left-hand side menu select: Compute Engine -> VM Instances (when you do this the first time the API needs to be activated)
* Generate SSH key:
	* https://cloud.google.com/compute/docs/connect/create-ssh-keys
	* cd .ssh
	* ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USER -b 2048 
	* This creates a public and a private key
	* Put the public key to Google Cloud
	* On the left-habd sided pannel choose "Metadata"
	* Choose "SSH KEYS" -> "ADD SSH KEY" -> add public key there -> "SAVE"
* Create an instance
	* On the left-hand sided pannel move to "VM instances"
	* Click on "CREATE INSTANCE" 
	* Set configurations: Choose Name, Region, Zone
	* Then we already see an estimate of the monthly costs
	* Choose instance type: "e2-standard-4"
	* Optional: change Boot disk to "Ubuntu", 20.04 LTS, size: 30GB
	* "CREATE" (you can also see how to create it from command line: "EQIVALENT COMMAND LINE")
	* Now you can ssh to the instance using the external IP:
		* Move to home directory
		* ssh -i  ~/.ssh/gcp <username>@<external-ip> (ssh-i ~/.ssh/gcp froukje@external-ip)
* Configure the instance
	* On the instance nothing is installed, excep gcloud (e.g. ```gcloud -v```)
	* Install Anaconda
		* Download Anaconda: https://www.anaconda.com/products/distribution
		* Version for Linux: 64-Bit (x86), copy link
		* In terminal, that is connected to gcp: ```wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh```
		* ```bash Anaconda3-2022.10-Linux-x86_64.sh```
* In folder .ssh create a config file: ```touch config```:
	```Host de-zoomcamp
    HostName 34.88.152.223
    User froukje
    IdentityFile /home/frauke/.ssh/gcp```
	* Then we can use ```ssh de-zoomcamp```
* Install Docker
	* ```sudo apt-get update```
	* ```sudo apt-get install docker.io```
	* give permissions to run docker without sudo: https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md
	* ```sudo groupadd docker```
	* ```sudo gpasswd -a $USER docker```
	* ```sudo service docker restart```
	* logout and in again
* Install docker compose:
	* go to github: https://github.com/docker/compose/
	* select release on the right hand side (e.g. latest release)
	* choose "docker-compose-linux-x86 64" and copy link
	* in our VM: create folder: ```mkdir bin``` and move there
	* ```wget https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -O docker-compose```
	* Make the file executable: ```chmod +x docker-compose```
	* Make it visible/executable from everywhere -> add to bin-directory to PATH variable to .bashrc
		* open .bashrc and add at the end:
		* ```export PATH="${HOME}/bin:${PATH}"```
* Configure vs code to access the VM
	* Install extension remote SSH
	* "connect to host": choose above created config file
* Clone course repo:
	* ```git clone https://github.com/DataTalksClub/data-engineering-zoomcamp.git``` 	
* Now we can move to the directory: data-engineering-zoomcamp/week_1_basics_n_setup/2_docker_sql and run docker-compose:
	* ```docker-compose up -d```
* Install pgcli: ```pip install pgcli```
	* We can the use: ```pgcli -h localhost -U root -d ny_taxi``` (pw: root)
	* Use e.g. ```dt```
	* Alternatively: Install with conda: ```conda install -c conda-forge pgcli```  (before ```pip uninstall pgcli```)
		* Additionally install: ```pip install -U mycli```
* Forward postgres port (5432) to our local machine	
	* In VS code open terminal (connected to GCP) -> go to tap "PORTS" -> "Forward a Port"
	* Add 5432
	* Now we are able to access this port from our local machine
	* open new terminal and execute ```pgcli -h localhost -U root -d ny_taxi```
	* Add port 8080
	* We can then access postgres via locahost:8080 (login: admin@admin.com, password: root)
* Start Jupyter from GCP
	* In terminal type: ```jupyter-notebook &```
	* Forward port 8888 (as before)
	* copy link (e.g.: http://localhost:8888/?token=68cabc42701839c0de3ecc8e0e367f3504868ce0b012db24) and open in browser
	* Alternative: login from new terminal and forward the port: ```ssh -L localhost:8888:localhost:8888 froukje@<external ip>```
	* Note: a specific port can be chosen by starting ```jupyter-notebook -p 8888```
	* Then in the browser type: ```localhost:8888/tree```, if needed copy the token to access jupyter notebooks
* Install terraform:
	* move to directory "bin"
	* https://developer.hashicorp.com/terraform/downloads
	* ```wget https://releases.hashicorp.com/terraform/1.3.7/terraform_1.3.7_linux_amd64.zip```
	* ```sudo apt-get install unzip```
	* ```unzip terraform_1.3.7_linux_amd64.zip```
	* ```rm terraform_1.3.7_linux_amd64.zip```	
	* To use terraform we need to get our gcp credentials to the VM:
		* copy the file with e.g. sftp
		* ```sftp de-zoomcamp```
		* cd to folder where it should be stored
		* ```put stoked-mode-375206-e914d123bc05.json```
	* setup google envirenmental credential variable:
		* ```export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/stoked-mode-375206-e914d123bc05.json```
	* Use this .json file to authenticate our cli
		* ```bash
		gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS```
		```		
	* Now we can use ```terraform init```, ```terraform plan ...```
* To stop the instance:
	* From the website: click "stop"
	* From the terminal: ```sudo shutdown now```	
	