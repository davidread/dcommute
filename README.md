# D Commute

This is a journey planner for D's commute.

## Setup

1. Python setup

```sh
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. For getting traffic info from Google Directions API, setup and download the Google Service Account token, with the appropriate permissions:

* Go to Google Cloud Console
* Create a new project
* Enable the Google Directions API
* Create a service account
* Download the service account key JSON file and save as `~/.gcloud/dcommute-service-account-key.json`

3. Get a BODS API key from https://data.bus-data.dft.gov.uk/account/settings/ and save it in `.bods_key`


## Run

```
. venv/bin/activate
python3 plan.py
```
