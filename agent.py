import psycopg2
import json
import subprocess
from typing import Dict, List, Any
from google.adk.agents import Agent

class PostgresStrategyAgent:
    def __init__(self):
        # Configure these values based on your Minikube setup
        self.db_config = {
            "host": "postgres.strategy.svc.cluster.local",  # Kubernetes service DNS
            "port": "5432",
            "database": "strategydb",
            "user": "user",
            "password": "password"
        }
        
        self.strategy_service_url = "http://strategy-service.strategy.svc.cluster.local/strategy"

    def get_db_connection(self):
        """Establish connection to PostgreSQL in Minikube"""
        return psycopg2.connect(**self.db_config)

    def fetch_strategy_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch strategy data from PostgreSQL
        Args:
            limit: Maximum number of records to return
        Returns:
            Dictionary with status and either data or error message
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT id, parameter, value, timestamp FROM strategy_data LIMIT %s"
            cursor.execute(query, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return {
                "status": "success",
                "data": results,
                "message": f"Retrieved {len(results)} records"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Database error: {str(e)}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def send_to_strategy_service(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send data to the Python strategy service in Minikube
        Args:
            data: List of dictionaries containing strategy data
        Returns:
            Dictionary with status and either response or error message
        """
        try:
            # Prepare the request data
            request_data = json.dumps({"data": data})
            
            # Call the strategy service using curl (you could use requests library instead)
            cmd = [
                "curl", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-d", request_data,
                self.strategy_service_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "response": json.loads(result.stdout)
                }
            else:
                return {
                    "status": "error",
                    "error_message": result.stderr
                }
                
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error_message": f"JSON decode error: {str(e)}"
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error_message": "Strategy service timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Service call error: {str(e)}"
            }

    def execute_analysis(self, limit: int = 100) -> Dict[str, Any]:
        """
        Complete workflow: fetch data from PostgreSQL and send to strategy service
        Args:
            limit: Maximum number of records to process
        Returns:
            Combined results from database and strategy service
        """
        # Step 1: Get data from PostgreSQL
        db_result = self.fetch_strategy_data(limit)
        if db_result["status"] != "success":
            return db_result
        
        # Step 2: Send to strategy service
        service_result = self.send_to_strategy_service(db_result["data"])
        
        # Return combined results
        return {
            "database_result": db_result,
            "strategy_result": service_result
        }

# Create the ADK agent
strategy_agent = Agent(
    name="postgres_strategy_agent",
    model="gemini-2.0-flash",
    description="Agent that reads from PostgreSQL in Minikube and sends data to strategy service",
    instruction=(
        "You are a data analysis agent that can fetch strategy data from PostgreSQL "
        "running in Minikube and send it to a Python strategy service for processing. "
        "You can specify how many records to fetch using the 'limit' parameter."
    ),
    tools=[PostgresStrategyAgent().execute_analysis],
)