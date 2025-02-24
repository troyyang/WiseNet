from neo4j import GraphDatabase
from core.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# create a Neo4j driver
client = GraphDatabase.driver(
    uri=NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# test case
def test_neo4j_connection():
    try:
        # try to connect to Neo4j
        with client.session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 1")
            assert result is not None
            print("connection success:", result)
    except Exception as e:
        print("connection failed:", e)


def main():
    test_neo4j_connection()

if __name__ == '__main__':
    main()
