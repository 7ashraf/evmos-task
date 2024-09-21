package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"math/big"
	"net/http"
	"os"
)

const (
	nodeURL    = "http://localhost:8545"
	startBlock = 100
	endBlock   = 200
)

// JSON-RPC request structure
type RPCRequest struct {
	JSONRPC string        `json:"jsonrpc"`
	Method  string        `json:"method"`
	Params  []interface{} `json:"params"`
	ID      int           `json:"id"`
}

// JSON-RPC response structure
type RPCResponse struct {
	Result json.RawMessage `json:"result"`
	Error  interface{}     `json:"error"`
	ID     int             `json:"id"`
}

// Function to send JSON-RPC requests
func sendRPCRequest(method string, params []interface{}) (*RPCResponse, error) {
	request := RPCRequest{
		JSONRPC: "2.0",
		Method:  method,
		Params:  params,
		ID:      1,
	}

	requestBody, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(nodeURL, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var rpcResp RPCResponse
	if err := json.NewDecoder(resp.Body).Decode(&rpcResp); err != nil {
		return nil, err
	}

	return &rpcResp, nil
}

// Function to get block data
func getBlockByNumber(blockNumber int) (json.RawMessage, error) {
	blockHex := fmt.Sprintf("0x%x", blockNumber)
	response, err := sendRPCRequest("eth_getBlockByNumber", []interface{}{blockHex, true})
	return response.Result, err
}

// Function to get balance of an address in Ether
func getBalance(address string) (float64, error) {
	response, err := sendRPCRequest("eth_getBalance", []interface{}{address, "latest"})
	if err != nil {
		return 0, err
	}

	var balanceHex string
	if err := json.Unmarshal(response.Result, &balanceHex); err != nil {
		return 0, err
	}

	balanceWei := new(big.Int)
	balanceWei.SetString(balanceHex[2:], 16)                                                  // Remove '0x' prefix
	balanceEther := new(big.Float).Quo(new(big.Float).SetInt(balanceWei), big.NewFloat(1e18)) // Convert Wei to Ether

	// Return the float64 value
	return balanceEther.Float64(), nil
}

// Function to find interacting wallets
func findInteractingWallets() (map[string]struct{}, error) {
	wallets := make(map[string]struct{})

	for i := startBlock; i <= endBlock; i++ {
		blockData, err := getBlockByNumber(i)
		if err != nil {
			return nil, err
		}

		var block struct {
			Transactions []struct {
				From string `json:"from"`
				To   string `json:"to"`
			} `json:"transactions"`
		}
		if err := json.Unmarshal(blockData, &block); err != nil {
			return nil, err
		}

		for _, tx := range block.Transactions {
			wallets[tx.From] = struct{}{} // Add sender
			if tx.To != "" {
				wallets[tx.To] = struct{}{} // Add recipient
			}
		}
	}

	return wallets, nil
}

// Function to save wallet balances to CSV
func saveToCSV(walletBalances map[string]float64, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header
	writer.Write([]string{"Wallet Address", "Balance (ETH)"})

	// Write wallet balances
	for wallet, balance := range walletBalances {
		writer.Write([]string{wallet, fmt.Sprintf("%f", balance)})
	}

	return nil
}

func main() {
	wallets, err := findInteractingWallets()
	if err != nil {
		fmt.Println("Error finding interacting wallets:", err)
		return
	}

	walletBalances := make(map[string]float64)
	for wallet := range wallets {
		balance, err := getBalance(wallet)
		if err == nil {
			walletBalances[wallet] = balance
		}
	}

	// Save to CSV
	if err := saveToCSV(walletBalances, "wallet_balances.csv"); err != nil {
		fmt.Println("Error saving to CSV:", err)
		return
	}

	fmt.Println("Wallet balances saved to 'wallet_balances.csv'")
}
