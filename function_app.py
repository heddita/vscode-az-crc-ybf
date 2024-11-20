import azure.functions as func
import logging
from azure.cosmos import CosmosClient, PartitionKey
import os

# Initialize Cosmos DB client (singleton pattern)
endpoint = os.environ['AzureResumeCosmosEndpoint']
key = os.environ['AzureResumeConnectionString']
client = CosmosClient(endpoint, key)

# Get database and container
database_name = 'AzureResume'
container_name = 'Counter'
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="getCVCounter")
def getCVCounter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # Read the current counter from Cosmos DB
        counter = container.read_item(item='1', partition_key='1')
        
        # Update counter with immutable pattern
        updated_counter = counter.copy()
        updated_counter['count'] += 1
        
        # Replace the updated counter in Cosmos DB
        container.replace_item(item=updated_counter, partition_key='1')
        
        # Return the updated counter
        return func.HttpResponse(
            body=str(updated_counter),
            status_code=200,
            headers={
                'Content-Type': 'application/json'
            }
        )
    
    except Exception as error:
        logging.error(f'Error processing request: {str(error)}')
        return func.HttpResponse(
            body=str({'message': 'An error occurred processing your request.'}),
            status_code=500,
            headers={
                'Content-Type': 'application/json'
            }
        )