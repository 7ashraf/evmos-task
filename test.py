import unittest
from unittest.mock import patch, MagicMock
import requests
import json

# Import your main module here. For example, if your code is in a file named `interaction_tracker.py`, uncomment the line below.
from main import *

class TestBlockchainInteractions(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost:8545"

    @patch('requests.post')
    def test_send_rpc_request(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'jsonrpc': '2.0', 'result': 'some_result', 'id': 1}
        mock_post.return_value = mock_response

        result = send_rpc_request("eth_getBlockByNumber", ["0x64", True])
        self.assertEqual(result['result'], 'some_result')
        mock_post.assert_called_once_with(self.url, json={'jsonrpc': '2.0', 'method': 'eth_getBlockByNumber', 'params': ['0x64', True], 'id': 1})

    @patch('requests.post')
    def test_get_block_by_number(self, mock_post):
        block_data = {
            'jsonrpc': '2.0',
            'result': {
                'transactions': [{'from': '0xabc', 'to': '0xdef'}]
            },
            'id': 1
        }
        mock_response = MagicMock()
        mock_response.json.return_value = block_data
        mock_post.return_value = mock_response

        result = get_block_by_number(100)
        self.assertEqual(len(result['transactions']), 1)
        self.assertEqual(result['transactions'][0]['from'], '0xabc')

    @patch('requests.post')
    def test_is_contract(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'jsonrpc': '2.0', 'result': '0x1234'}
        mock_post.return_value = mock_response

        result = is_contract('0xabc')
        self.assertTrue(result)

        mock_response.json.return_value = {'jsonrpc': '2.0', 'result': '0x'}
        result = is_contract('0xabc')
        self.assertFalse(result)

    @patch('requests.post')
    def test_get_balance(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'jsonrpc': '2.0', 'result': '0x2faf080'}
        mock_post.return_value = mock_response

        balance = get_balance('0xabc')
        self.assertEqual(balance, 1000000000.0)  # 0x2faf080 = 1000000000 in decimal

    @patch('requests.post')
    def test_count_contract_interactions(self, mock_post):
        block_data = {
            'jsonrpc': '2.0',
            'result': {
                'transactions': [
                    {'from': '0xabc', 'to': '0xdef'},
                    {'from': '0x123', 'to': None},  # New contract creation
                    {'from': '0x456', 'to': '0xabc'},  # Interaction with contract
                ]
            },
            'id': 1
        }
        mock_response = MagicMock()
        mock_response.json.return_value = block_data
        mock_post.return_value = mock_response

        interactions, wallets = count_contract_interactions(100, 100)
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions['0xabc'], 1)  # Contract interactions count
        self.assertEqual(len(wallets), 3)  # Unique wallets count

    @patch('requests.post')
    def test_save_to_csv(self, mock_post):
        sorted_wallets = [('0xabc', 1.0), ('0xdef', 0.5)]
        filename = "test_wallet_balances.csv"
        save_to_csv(sorted_wallets, filename)

        with open(filename, 'r') as file:
            lines = file.readlines()
            self.assertEqual(lines[0].strip(), "Wallet Address,Balance (ETH)")
            self.assertEqual(lines[1].strip(), "0xabc,1.0")
            self.assertEqual(lines[2].strip(), "0xdef,0.5")

    @patch('requests.post')
    def test_save_interaction_counts_to_csv(self, mock_post):
        interactions = {'0xabc': 1, '0xdef': 3}
        filename = "test_contract_interactions.csv"
        save_interaction_counts_to_csv(interactions, filename)

        with open(filename, 'r') as file:
            lines = file.readlines()
            self.assertEqual(lines[0].strip(), "Contract Address,Interaction Count")
            self.assertEqual(lines[1].strip(), "0xabc,1")
            self.assertEqual(lines[2].strip(), "0xdef,3")

if __name__ == '__main__':
    unittest.main()
