from dotenv import load_dotenv
import os

# query the path of the current file
root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# the path of the .env file
env_path = os.path.join(root_path, '.env')

# Check if the .env file exists
if not os.path.exists(env_path):
    env_path = os.path.join(root_path, '../', '.env')

if os.path.exists(env_path):
    # Load environment variables from the .env file
    load_dotenv(env_path)

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
API_ENV: str = os.getenv('API_ENV', 'dev')
SECRET_KEY: str = os.getenv('SECRET_KEY')
# ---------------------------API CONFIG----------------------------
API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
API_PORT: int = int(os.getenv('API_PORT', 8088))
# the json key in request and response data will be converted to camelCase
IS_CAMEL_CASE: bool = os.getenv('IS_CAMEL_CASE', True)
# ---------------------------NEO4J CONFIG----------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
# ---------------------------postgres CONFIG----------------------------
POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT', 5436))
POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'wisenet')
POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'wisenet')
POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'wisenet')
# ---------------------------LLM CONFIG----------------------------
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_1_5_PRO_32K_MODEL: str = os.getenv("DOUBAO_1_5_PRO_32K_MODEL", "")
DOUBAO_1_5_PRO_256K_MODEL: str = os.getenv("DOUBAO_1_5_PRO_256K_MODEL", "")
DOUBAO_1_5_LITE_32K_MODEL: str = os.getenv("DOUBAO_1_5_LITE_32K_MODEL", "")
DOUBAO_PRO_32K_MODEL: str = os.getenv("DOUBAO_PRO_32K_MODEL", "")
DOUBAO_API_ENDPOINT: str = os.getenv("DOUBAO_API_ENDPOINT", "https://ark.cn-beijing.volces.com/api")
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY")
OLLAMA_ENDPOINT: str = os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434")
DEFAULT_LLM_NAME: str = os.getenv("DEFAULT_LLM_NAME", "llama3.1")
LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", 60.0))
#--------------------------graph config-------------------------------
DEEP_LIMIT:int = int(os.getenv("DEEP_LIMIT", 10))
# default genereate quetions count
DEFAULT_GENERATE_QUESTIONS_COUNT:int = int(os.getenv("DEFAULT_GENERATE_QUESTIONS_COUNT", 3))
# default genereate prompts count
DEFAULT_GENERATE_PROMPTS_COUNT:int = int(os.getenv("DEFAULT_GENERATE_PROMPTS_COUNT", 3))
# UPLOAD_DIR
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/upload")
# MAX_FILE_SIZE
MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 5242880))
# The number of concurrent queries per knowledge base
GDS_CONCURRENT_QUERIES: int = int(os.getenv("GDS_CONCURRENT_QUERIES", 10))
# Get the number of nodes most similar to the user input
GDS_TOP_K: int = int(os.getenv("GDS_TOP_K", 10))
# Similarity cutoff, Filter out from the list of K-nearest neighbors nodes with similarity below this threshold.
GDS_SIMILARITY_CUTOFF: float = float(os.getenv("GDS_SIMILARITY_CUTOFF", 0.5))
# Get the number of nodes most similar to the user input
TOP_K: int = int(os.getenv("TOP_K", 30))
# Similarity cutoff
SIMILARITY_CUTOFF = float(os.getenv("SIMILARITY_CUTOFF", 0.75))
# max workers for analyze graph
MAX_WORKERS:int = int(os.getenv("MAX_WORKERS", 1))