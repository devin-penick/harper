#!/usr/bin/env python3

import requests
import time
import json
import psutil
import docker
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HarperWorkflow:
    def __init__(self):
        self.base_url = "http://localhost:9925"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4xMjM="  # base64 encoded admin:admin123
        }
        self.docker_client = docker.from_env()
        self.metrics = []
        self.metrics_dir = "/opt/harperdb/metrics"  # Container's metrics directory

    def validate_container(self) -> bool:
        """Validate that the HarperDB container is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Container validation failed: {e}")
            return False

    def create_schema_and_table(self) -> None:
        """Create a schema and table for our test data."""
        schema_data = {
            "operation": "create_schema",
            "schema": "test_schema"
        }
        table_data = {
            "operation": "create_table",
            "schema": "test_schema",
            "table": "test_table",
            "hash_attribute": "id"
        }
        
        try:
            response = requests.post(f"{self.base_url}", json=schema_data, headers=self.headers)
            response.raise_for_status()
            
            response = requests.post(f"{self.base_url}", json=table_data, headers=self.headers)
            response.raise_for_status()
            logger.info("Schema and table created successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create schema/table: {e}")

    def load_test_data(self) -> None:
        """Load test data into the table using HarperDB API operations."""
        try:
            # First, let's describe the table to understand its structure
            describe_table = {
                "operation": "describe_table",
                "schema": "test_schema",
                "table": "test_table"
            }
            response = requests.post(f"{self.base_url}", json=describe_table, headers=self.headers)
            response.raise_for_status()
            table_info = response.json()
            logger.info(f"Table structure: {table_info}")

            # Generate sample data using the table structure
            sample_data = {
                "operation": "insert",
                "schema": "test_schema",
                "table": "test_table",
                "records": []
            }

            # Generate 10 records with realistic data
            for i in range(1, 11):
                record = {
                    "id": i,
                    "name": f"Product {i}",
                    "value": i * 100,
                    "description": f"Description for product {i}",
                    "category": f"Category {i % 3 + 1}",
                    "price": round(i * 10.99, 2),
                    "in_stock": i % 2 == 0,
                    "created_at": datetime.now().isoformat()
                }
                sample_data["records"].append(record)

            # Insert the data
            response = requests.post(f"{self.base_url}", json=sample_data, headers=self.headers)
            response.raise_for_status()
            logger.info("Test data loaded successfully")

            # Verify the data was inserted
            search_data = {
                "operation": "search_by_value",
                "schema": "test_schema",
                "table": "test_table",
                "search_attribute": "id",
                "search_value": "*",
                "get_attributes": ["*"]
            }
            response = requests.post(f"{self.base_url}", json=search_data, headers=self.headers)
            response.raise_for_status()
            inserted_data = response.json()
            logger.info(f"Successfully inserted {len(inserted_data)} records")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to load test data: {e}")

    def update_data(self) -> None:
        """Update records in the table using HarperDB API operations."""
        try:
            # First, let's find records to update
            search_data = {
                "operation": "search_by_value",
                "schema": "test_schema",
                "table": "test_table",
                "search_attribute": "id",
                "search_value": "*",
                "get_attributes": ["id", "price"]
            }
            response = requests.post(f"{self.base_url}", json=search_data, headers=self.headers)
            response.raise_for_status()
            records = response.json()

            # Update prices for even-numbered IDs
            update_records = []
            for record in records:
                if record["id"] % 2 == 0:
                    update_records.append({
                        "id": record["id"],
                        "price": round(record["price"] * 1.1, 2)  # 10% price increase
                    })

            if update_records:
                update_data = {
                    "operation": "update",
                    "schema": "test_schema",
                    "table": "test_table",
                    "records": update_records
                }
                
                response = requests.post(f"{self.base_url}", json=update_data, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Updated {len(update_records)} records successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update data: {e}")

    def validate_changes(self) -> bool:
        """Validate that the updates were successful using HarperDB API operations."""
        try:
            # Search for updated records
            search_data = {
                "operation": "search_by_value",
                "schema": "test_schema",
                "table": "test_table",
                "search_attribute": "id",
                "search_value": "*",
                "get_attributes": ["id", "price"]
            }
            response = requests.post(f"{self.base_url}", json=search_data, headers=self.headers)
            response.raise_for_status()
            records = response.json()

            # Verify that even-numbered IDs have updated prices
            for record in records:
                if record["id"] % 2 == 0:
                    original_price = (record["id"] * 10.99)
                    updated_price = round(original_price * 1.1, 2)
                    if abs(record["price"] - updated_price) > 0.01:
                        logger.error(f"Price validation failed for record {record['id']}")
                        return False

            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to validate changes: {e}")
            return False

    def test_custom_component(self) -> bool:
        """Test the custom table statistics component."""
        try:
            response = requests.get(
                f"{self.base_url}/table-stats/test_schema/test_table",
                headers=self.headers
            )
            response.raise_for_status()
            stats = response.json()
            
            logger.info("Custom component test results:")
            logger.info(f"Total records: {stats['stats']['total_records']}")
            logger.info(f"Numeric fields: {list(stats['stats']['numeric_fields'].keys())}")
            logger.info(f"String fields: {list(stats['stats']['string_fields'].keys())}")
            
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to test custom component: {e}")
            return False

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect container performance metrics."""
        try:
            container = self.docker_client.containers.get("harperdb")
            stats = container.stats(stream=False)
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": stats["cpu_stats"]["cpu_usage"]["total_usage"],
                "memory_usage": stats["memory_stats"]["usage"],
                "network_io": stats["networks"]["eth0"],
                "disk_io": stats["blkio_stats"]
            }
            
            self.metrics.append(metrics)
            return metrics
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}

    def save_metrics(self) -> None:
        """Save metrics to the container's metrics directory."""
        try:
            # Create metrics directory if it doesn't exist
            os.makedirs(self.metrics_dir, exist_ok=True)
            
            # Save metrics to file
            metrics_file = os.path.join(self.metrics_dir, "workflow_metrics.json")
            with open(metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2)
            
            logger.info(f"Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def run_workflow(self) -> None:
        """Run the complete workflow."""
        logger.info("Starting HarperDB workflow")
        
        # Validate container
        if not self.validate_container():
            logger.error("Container validation failed")
            return
        
        # Create schema and table
        self.create_schema_and_table()
        
        # Collect initial metrics
        self.collect_metrics()
        
        # Load test data
        self.load_test_data()
        
        # Update data
        self.update_data()
        
        # Validate changes
        if not self.validate_changes():
            logger.error("Data validation failed")
            return
        
        # Test custom component
        if not self.test_custom_component():
            logger.error("Custom component test failed")
            return
        
        # Collect final metrics
        self.collect_metrics()
        
        # Save metrics
        self.save_metrics()
        
        logger.info("Workflow completed successfully")

if __name__ == "__main__":
    workflow = HarperWorkflow()
    workflow.run_workflow() 