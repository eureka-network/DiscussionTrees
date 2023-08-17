# Discussion Trees

## dev environment

let's use mamba.
- If you are using an Anaconda distribution, you can install Mamba using the command: `conda install mamba -c conda-forge`.
- If you are not using Anaconda, refer to the official Mamba documentation for installation instructions: https://mamba.readthedocs.io/en/latest/getting_started.html.

then run
```
mamba env create -f environment.yml
```

## starting the builder

copy `.env.example` to `.env` and fill out the needed parameters, then run
```
./scripts/dtree.sh build
```

### scraping data into neo4j (old, for discourse forums)

In the mamba environment, from the root of the project
```
cd discourse_forum
scrapy crawl discourse
```
This is currently hard-coded to scrape the posts and threads from https://forum.safe.global.

### viewing the DB

with neo4j runnning in the docker container, on your browser go to http://localhost:7474 and you can find the username and password in the docker-compose.yml file.
