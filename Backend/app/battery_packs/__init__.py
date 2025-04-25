# battery_pack_router.py

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.battery_packs.list_battery_packs import get_battery_pack_data
from .models import BatteryPackResponse
import json

router = APIRouter(prefix="/battery_packs")


@router.get("/battery_packs", response_model=BatteryPackResponse)
async def list_battery_packs():
    try:
        # Call the function to get the battery pack data
        result = await get_battery_pack_data()  # Get data from the database

        # Ensure result has the correct status
        if result["status"] != "fetched":
            raise HTTPException(
                status_code=500, detail="Error fetching battery packs data"
            )

        # Extract the result from the response
        battery_packs = result["result"]

        # Parse the 'structured_output' field if it exists
        parsed_result = []
        for item in battery_packs:
            # Check if 'structured_output' exists
            if "structured_output" in item:
                try:
                    # Ensure the structured_output is a valid JSON string and parse it
                    structured_output = json.loads(item["structured_output"])
                    item["structured_output"] = (
                        structured_output  # Replace the string with the parsed object
                    )
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON: {e}")
                    item["structured_output"] = {}  # Set an empty dict if parsing fails
            parsed_result.append(item)

        # Return a response with status and result
        return JSONResponse(
            content={
                "status": "fetched",  # You can change it to "success" if you prefer
                "result": {"results": parsed_result},
            }
        )

    except Exception as e:
        # Log error if something goes wrong
        logging.error(f"Error fetching battery packs data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.get("/battery_packs", response_model=BatteryPackResponse)
# async def list_battery_packs():
#     try:
#         # Call the function to get the battery pack data
#         result = await get_battery_pack_data()  # Get data from the database

#         # Ensure result has the correct status
#         if result["status"] != "fetched":
#             raise HTTPException(
#                 status_code=500, detail="Error fetching battery packs data"
#             )

#         # Extract the result from the response
#         battery_packs = result["result"]

#         # Parse the 'structured_output' field if it exists
#         parsed_result = []
#         for item in battery_packs:
#             # Check if 'structured_output' exists
#             if "structured_output" in item:
#                 try:
#                     # Ensure the structured_output is a valid JSON string and parse it
#                     structured_output = json.loads(item["structured_output"])
#                     item["structured_output"] = (
#                         structured_output  # Replace the string with the parsed object
#                     )
#                 except json.JSONDecodeError as e:
#                     logging.error(f"Error decoding JSON: {e}")
#                     item["structured_output"] = {}  # Set an empty dict if parsing fails
#             parsed_result.append(item)

#         return JSONResponse(
#             content=parsed_result  # Return the properly parsed data as JSON response
#         )

#     except Exception as e:
#         # Log error if something goes wrong
#         logging.error(f"Error fetching battery packs data: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
