import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions
import json

# Initialize client outside function (singleton pattern)
connection_string = os.getenv("AzureResumeConnectionString")
cosmos_client = CosmosClient.from_connection_string(connection_string)
database = cosmos_client.get_database_client("AzureResume")
container = database.get_container_client("Counter")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="getCVCounter")

def getCVCounter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # Read the current counter from Cosmos DB
        counter_item = container.read_item(item="1", partition_key="1")

        # Update counter with immutable pattern
        updated_counter = {
            **counter_item,
            "count": counter_item["count"] + 1
        }

        # Replace the updated counter in Cosmos DB
        container.replace_item(item=updated_counter["id"], body=updated_counter)

        # Return the updated counter
        return func.HttpResponse(
            body=json.dumps(updated_counter),
            status_code=200,
            mimetype="application/json"
        )
    except exceptions.CosmosResourceNotFoundError:
        logging.error("Counter item not found in Cosmos DB.")
        return func.HttpResponse(
            body=json.dumps({"message": "Counter item not found."}),
            status_code=404,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            body=json.dumps({"message": "An error occurred processing your request."}),
            status_code=500,
            mimetype="application/json"
        )