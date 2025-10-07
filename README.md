# Patstat Searcher / - Compute Block

This software enables users to automate a search request on the internal PATSTAT database. Only SELECT statements are allowed.
The intended use case is as a compute block in the scstream environment.

## Usage
Make sure you are using the university VPN or are in the university.

Enter your Query in the SearchQuery.txt. Make sure it is a SELECT statement and does not contain keywords that alter the database. It will not work otherwise.

## Docker
The docker container can be started be using this shell command:
`docker compose up -d --build` 

## Output

The output is a CSV File