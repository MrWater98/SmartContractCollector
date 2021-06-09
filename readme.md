## Introduction

* A small script for collecting smart contract to MongoDB.

## prerequisite

* Python 3.8 
* requests
* bs4
* etherscan-python
* lxml
* MongoDB (port: 27017)

## Approach

* Because `etherscan` has very strict access restriction, this script collect contract address from https://etherchain.org.
* After collecting contract address, we can collect verified smart contract by using Etherscan API.
