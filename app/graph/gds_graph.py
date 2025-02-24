import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.extends_logger import logger
from core.i18n import _
from graph import graph


class GdsGraph:
    """
    Represents a Graph Data Science (GDS) graph in the Neo4j database. This class handles the creation, deletion,
    and querying of GDS graphs, as well as their properties and metadata.
    """

    # Default graph names for GDS operations
    graph_name = "gds_graph"
    test_graph_name = "test_gds_graph"

    def __init__(self,
                 graphName: str,
                 database: str,
                 databaseLocation: str,
                 configuration: Dict[str, Any],
                 nodeCount: int,
                 relationshipCount: int,
                 schema: Dict[str, Any],
                 schemaWithOrientation: Dict[str, Any],
                 degreeDistribution: Dict[str, Any],
                 density: float,
                 creationTime: datetime,
                 modificationTime: datetime,
                 sizeInBytes: int,
                 memoryUsage: str):
        """
        Initializes a GdsGraph instance with the provided attributes.

        Args:
            graphName (str): The name of the GDS graph.
            database (str): The database where the graph is stored.
            databaseLocation (str): The location of the database.
            configuration (Dict[str, Any]): Configuration settings for the graph.
            nodeCount (int): The number of nodes in the graph.
            relationshipCount (int): The number of relationships in the graph.
            schema (Dict[str, Any]): The schema of the graph.
            schemaWithOrientation (Dict[str, Any]): The schema with orientation information.
            degreeDistribution (Dict[str, Any]): The degree distribution of the graph.
            density (float): The density of the graph.
            creationTime (datetime): The creation time of the graph.
            modificationTime (datetime): The last modification time of the graph.
            sizeInBytes (int): The size of the graph in bytes.
            memoryUsage (str): The memory usage of the graph.
        """
        self.graphName = graphName
        self.database = database
        self.databaseLocation = databaseLocation
        self.configuration = configuration
        self.nodeCount = nodeCount
        self.relationshipCount = relationshipCount
        self.schema = schema
        self.schemaWithOrientation = schemaWithOrientation
        self.degreeDistribution = degreeDistribution
        self.density = density
        self.creationTime = creationTime
        self.modificationTime = modificationTime
        self.sizeInBytes = sizeInBytes
        self.memoryUsage = memoryUsage

    def __repr__(self):
        """
        Returns a string representation of the GdsGraph instance.

        Returns:
            str: A string representation of the GdsGraph.
        """
        return (f"GdsGraph(graphName={self.graphName}, database={self.database}, "
                f"nodeCount={self.nodeCount}, relationshipCount={self.relationshipCount}, "
                f"density={self.density}, creationTime={self.creationTime}, "
                f"modificationTime={self.modificationTime}, sizeInBytes={self.sizeInBytes}, "
                f"memoryUsage={self.memoryUsage})")

    @classmethod
    def list_gds_graph(cls) -> List["GdsGraph"]:
        """
        Lists all GDS graphs in the database.

        Returns:
            List[GdsGraph]: A list of GdsGraph instances representing the graphs.

        Raises:
            ValueError: If the query fails or no results are returned.
        """
        try:
            query = """
            CALL gds.graph.list(
            $gds_graph_name
            ) YIELD
            graphName,
            database,
            databaseLocation,
            configuration,
            nodeCount,
            relationshipCount,
            schema,
            schemaWithOrientation,
            degreeDistribution,
            density,
            creationTime,
            modificationTime,
            sizeInBytes,
            memoryUsage
            """
            params = {
                "gds_graph_name": cls.graph_name
            }
            query_result = graph.query(query, params=params)

            if not query_result:
                logger.error("Failed to list GDS graph: No result returned from the database.")
                raise ValueError(_("Failed to list GDS graph: No result returned from the database."))

            result = []
            for gds_graph in query_result:
                # Parse JSON fields
                gds_graph["configuration"] = json.loads(gds_graph["configuration"])
                gds_graph["schema"] = json.loads(gds_graph["schema"])
                gds_graph["schemaWithOrientation"] = json.loads(gds_graph["schemaWithOrientation"])
                gds_graph["degreeDistribution"] = json.loads(gds_graph["degreeDistribution"])
                result.append(GdsGraph(**gds_graph))
            return result
        except Exception as e:
            logger.error(f"Failed to list GDS graph: {e}")
            raise ValueError(_("Failed to list GDS graph."))

    @classmethod
    def create_gds_graph(cls, gds_graph_name: str) -> Dict[str, Any]:
        """
        Creates a new GDS graph in the database.

        Args:
            gds_graph_name (str): The name of the GDS graph to create.

        Returns:
            Dict[str, Any]: A dictionary containing the graph name, node count, and relationship count.

        Raises:
            ValueError: If the graph creation fails.
        """
        try:
            query = """
            MATCH (source)
            OPTIONAL MATCH (source)-[r]->(target)
            WITH gds.graph.project(
            $gds_graph_name,
            source,
            target,
            {
                sourceNodeProperties: source {
                    title_vector: coalesce(source.title_vector, [0.0]),
                    content_vector: coalesce(source.content_vector, [0.0])
                },
                targetNodeProperties: target{
                    title_vector: coalesce(target.title_vector, [0.0]),
                    content_vector: coalesce(target.content_vector, [0.0])
                }
            }
            ,
            {undirectedRelationshipTypes: ['*']}
            ) AS g
            RETURN g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels
            """
            params = {
                "gds_graph_name": gds_graph_name
            }
            query_result = graph.query(query, params=params)
            if not query_result:
                logger.error("Failed to create GDS graph: No result returned from the database.")
                raise ValueError(_("Failed to create GDS graph: No result returned from the database."))

            return query_result[0]
        except Exception as e:
            logger.error(f"Failed to create GDS graph: {e}")
            raise ValueError(_("Failed to create GDS graph."))

    @classmethod
    def delete_gds_graph(cls, gds_graph_name: str):
        """
        Deletes a GDS graph from the database.

        Args:
            gds_graph_name (str): The name of the GDS graph to delete.

        Raises:
            ValueError: If the graph deletion fails.
        """
        try:
            query = """
            CALL gds.graph.drop($gds_graph_name)
            """
            params = {
                "gds_graph_name": gds_graph_name
            }
            graph.query(query, params=params)
        except Exception as e:
            logger.error(f"Failed to delete GDS graph: {e}")
            raise ValueError(_("Failed to delete GDS graph."))

    @classmethod
    def check_gds_graph(cls, gds_graph_name: str) -> bool:
        """
        Checks if a GDS graph exists in the database.

        Args:
            gds_graph_name (str): The name of the GDS graph to check.

        Returns:
            bool: True if the graph exists, otherwise False.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = """
            CALL gds.graph.exists($gds_graph_name) YIELD
            graphName,
            exists
            """
            params = {
                "gds_graph_name": gds_graph_name
            }
            query_result = graph.query(query, params=params)
            if not query_result:
                logger.error("Failed to check GDS graph: No result returned from the database.")
                raise ValueError(_("Failed to check GDS graph: No result returned from the database."))

            return query_result[0]["exists"]
        except Exception as e:
            logger.error(f"Failed to check GDS graph: {e}")
            raise ValueError(_("Failed to check GDS graph."))