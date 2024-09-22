# Smart Contract Sorter
A script written in pyhton that fetches and analysis on-chain data from the ethereum chain ran locally


## Architecture and Sorting
* The script utilizes evmos JSON-RPC api in order to fetch on-chain statistics
* The script consists of 5 main methods and 2 sorting methods:
1. `get_block_by_number` method whic retieves block data given the hex number of the block
2. `send_rpc_request` which is a wrapper method for sending any rpc requests
3. `get_balance` which retrieves the balance of a given address
4. `is_contract` method used to check wether an address is a contract or not
5. `count_contract_interactions` the method utlizes all of the on-chain retireving mthods in order to collect all of the data, and process them
### Wallets sorting:
* The code checks if the reciever is not a smart contract
* If the reciever is wallet, the balance of the wallet address is fetched then added into mapping of wallet balances
* The mapping is sorted through normal python sorter
### Contract Sorting
* Each block is fetched
* Loop on each block transaction
* If reciever is a samrt contract, increase numer of interactions by one inside the contracts mapping
* Sort the mapping

## Installation
### 1. Install Evmosv18.1.0
    
    ```bash
    git clone https://github.com/evmos/evmos --branch v18.1.0 --depth 1
    cd evmos
    make install
    ```
    
### 2. Download the database folder:
    
    ```bash
    git clone https://github.com/evmos/challenge_db.git
    mkdir ~/.evmosd
    cp -r challenge_db/* ~/.evmosd
    ```
    
### 3. Run Evmosd to start the Rest-API:
```bash
evmosd start
```
### 4. Install python
[Pyhton Download Page](https://www.python.org/downloads/)

### 5. Clone the repo
```bash 
git clone https://github.com/7ashraf/evmos-task.git
cd task
```

### 6. Run Main
```bash 
python main.py
```

### 7. Run Tests
```bash
python -m unittest test.py 
```



