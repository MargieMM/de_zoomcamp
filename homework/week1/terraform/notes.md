## GCP AND TERRAFORM
https://console.cloud.google.com/
# Exporting enviroment variables for GCP

```
export PROJECT_NAME = 'enter gcp project name here'

export $GOOGLE_APPLICATION_CREDENTIALS = 'PATH where .json file is'

gcloud auth application-default set-quota-project ${PROJECT_NAME}

gcloud auth application-default login
```

Enable API's to interact between local environment and the cloud environment- Make sure you have selected the correct project

https://console.cloud.google.com/apis/library/iam.googleapis.com
https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

## Terraform Configuration
.terraform-version - File that contains the version
Configuration of resources  - Variables.tf
```
terraform {
    required_version= ">=1.0"
    backend = "local" {} # Change to gcs (google) or s3 (aws)
    required_providers {
        google = {
            source = "hashicorp/google
        }
    }
}

Terraform relies on providers to interact with cloud resources- Adds pre-defined resources that terraform can manage

e.g Cloud Storage = Datalake | Bigquery
```
