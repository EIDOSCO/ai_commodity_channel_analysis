from dotenv import load_dotenv
import os
import pandas as pd
from openai import OpenAI
from neo4j import GraphDatabase
import uuid
import json

load_dotenv()



NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")  

# Initialize Neo4j driver
try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    print("Neo4j Connected")
except Exception as e:
    print("Neo4j Connection Failed:", str(e))


def get_current_database(tx):
    query = "CALL db.info() YIELD name"
    result = tx.run(query)
    return result.single()


# Function to test the connection
def check_connection():
    try:
        with neo4j_driver.session() as session:
            record = session.execute_read(get_current_database)
            if record:
                print("Connected to database:", record["name"])
            else:
                print("Could not retrieve database name.")
            result = session.run("RETURN 'Connection successful' AS message")
            for record in result:
                print(record)
    except Exception as e:
        print("Connection test failed:", str(e))
    finally:
        neo4j_driver.close()



check_connection()
