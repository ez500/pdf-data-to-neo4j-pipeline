import csv
import glob
import os
from datetime import datetime

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
env_var = "/home/Neo4j/.env"
load_dotenv(env_var)

# Neo4j configuration
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_DATABASE = "fox_knowledge_graph"

# File location for CSVs
file_location = './out'


# Utility functions to create nodes/relationships in the Neo4j database
def create_node(session, label, properties):
    query = f"CREATE (n:{label} $properties)"
    session.run(query, properties=properties)


def create_relationship(session, from_label, from_properties, to_label, to_properties, rel_type):
    query = (
        f"MATCH (a:{from_label} $from_properties), (b:{to_label} $to_properties) "
        f"MERGE (a)-[r:{rel_type}]->(b)"
    )
    session.run(query, from_properties=from_properties, to_properties=to_properties)


# Ingest CSV into Neo4j
def ingest_csv_neo4j(csv_file):
    driver = GraphDatabase.driver(NEO4J_URI, database=NEO4J_DATABASE, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                subject = row.get('subject')
                relation = row.get('relation')
                object_ = row.get('object')

                if not (subject and relation and object_):
                    print(f'Skipping incomplete row in {csv_file}: {row}')
                    continue

                session.execute_write(create_node, 'Subject', {'name': subject})
                session.execute_write(create_node, 'Object', {'name': object_})
                session.execute_write(create_relationship,
                                      'Subject', {'name': subject}, 'Object', {'name': object_}, relation)

                print(f'Processed row: {subject} | {relation} | {object_}')

    print(f'Imported {csv_file} into Neo4j')
    driver.close()


# Parse PDFs and ingest into Neo4j
if __name__ == '__main__':
    csv_files = glob.glob(file_location + '/*.csv')
    print(f'{len(csv_files)} CSVs found')

    start_time = datetime.now()

    for csv_file in csv_files:
        ingest_csv_neo4j(csv_file)

    print(f'Total time: {datetime.now() - start_time}')
