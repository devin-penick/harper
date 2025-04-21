#!/usr/bin/env python3

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HarperDBTester:
    def __init__(self):
        self.base_url = "http://localhost:9925"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4xMjM="  # base64 encoded admin:admin123
        }

    def test_health(self):
        """Test if the service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            response.raise_for_status()
            logger.info("Health check passed")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    def test_schema_operations(self):
        """Test schema creation and description"""
        try:
            # Create a test schema
            schema_data = {
                "operation": "create_schema",
                "schema": "test_schema"
            }
            response = requests.post(self.base_url, json=schema_data, headers=self.headers)
            
            # Check if schema already exists
            if response.status_code == 400 and "already exists" in response.json().get("error", ""):
                logger.info("Schema already exists, continuing with existing schema")
            else:
                response.raise_for_status()
                logger.info("Schema created successfully")

            # Describe the schema
            describe_schema = {
                "operation": "describe_schema",
                "schema": "test_schema"
            }
            response = requests.post(self.base_url, json=describe_schema, headers=self.headers)
            response.raise_for_status()
            schema_info = response.json()
            logger.info(f"Schema description: {json.dumps(schema_info, indent=2)}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Schema operations failed: {e}")
            return False

    def test_table_operations(self):
        """Test table creation and data operations"""
        try:
            # Create a table
            table_data = {
                "operation": "create_table",
                "schema": "test_schema",
                "table": "test_table",
                "hash_attribute": "id"
            }
            response = requests.post(self.base_url, json=table_data, headers=self.headers)
            
            # Check if table already exists
            if response.status_code == 400 and "already exists" in response.json().get("error", ""):
                logger.info("Table already exists, continuing with existing table")
            else:
                response.raise_for_status()
                logger.info("Table created successfully")

            # Describe the table
            describe_table = {
                "operation": "describe_table",
                "schema": "test_schema",
                "table": "test_table"
            }
            response = requests.post(self.base_url, json=describe_table, headers=self.headers)
            response.raise_for_status()
            table_info = response.json()
            logger.info(f"Table description: {json.dumps(table_info, indent=2)}")

            # Clear existing data
            delete_data = {
                "operation": "delete",
                "schema": "test_schema",
                "table": "test_table",
                "hash_values": ["*"]
            }
            response = requests.post(self.base_url, json=delete_data, headers=self.headers)
            response.raise_for_status()
            logger.info("Existing data cleared")

            # Insert test data
            insert_data = {
                "operation": "insert",
                "schema": "test_schema",
                "table": "test_table",
                "records": [
                    {"id": 1, "name": "Test 1", "value": 100},
                    {"id": 2, "name": "Test 2", "value": 200}
                ]
            }
            response = requests.post(self.base_url, json=insert_data, headers=self.headers)
            response.raise_for_status()
            logger.info("Data inserted successfully")

            # Query the data
            query_data = {
                "operation": "search_by_value",
                "schema": "test_schema",
                "table": "test_table",
                "search_attribute": "id",
                "search_value": "*",
                "get_attributes": ["*"]
            }
            response = requests.post(self.base_url, json=query_data, headers=self.headers)
            response.raise_for_status()
            results = response.json()
            logger.info(f"Query results: {json.dumps(results, indent=2)}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Table operations failed: {e}")
            return False

    def test_custom_component(self):
        """Test the custom table statistics component"""
        try:
            response = requests.get(
                f"{self.base_url}/table-stats/test_schema/test_table",
                headers=self.headers
            )
            response.raise_for_status()
            stats = response.json()
            logger.info(f"Custom component stats: {json.dumps(stats, indent=2)}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Custom component test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        logger.info("Starting HarperDB service tests...")
        
        tests = [
            ("Health Check", self.test_health),
            ("Schema Operations", self.test_schema_operations),
            ("Table Operations", self.test_table_operations),
            ("Custom Component", self.test_custom_component)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\nRunning {test_name}...")
            result = test_func()
            results.append((test_name, result))
            logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
        
        # Print summary
        logger.info("\nTest Summary:")
        for test_name, result in results:
            logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
        
        return all(result for _, result in results)

if __name__ == "__main__":
    tester = HarperDBTester()
    tester.run_all_tests() 