# list_battery_packs.py

import logging
from app.db import get_db_connection, release_db_connection
from typing import List, Dict, Any
import json

BATTERY_PACK_QUERY = """
WITH battery_assets AS (
  SELECT
    a.asset_tag,
    a.model_id,
    a.status_id,
    a.company_id,
    a.location_id,
    a.warranty_months,
    a._snipeit_battery_cell_chemistry_18 AS battery_cell_chemistry,
    a._snipeit_battery_cell_temperatures_54 AS battery_cell_temperatures,
    a._snipeit_battery_cell_type_24 AS battery_cell_type,
    a._snipeit_battery_cell_voltages_53 AS battery_cell_voltages,
    a._snipeit_battery_pack_casing_25 AS battery_pack_casing,
    a._snipeit_battery_pack_nominal_charge_capacity_22 AS battery_pack_nominal_charge_capacity,
    a._snipeit_battery_pack_nominal_voltage_21 AS battery_pack_nominal_voltage,
    a._snipeit_bms_type_23 AS bms_type
  FROM "snipe-it".assets a
  WHERE a.model_id = 7
),
asset_details AS (
  SELECT
    ba.*,
    m.name AS model,
    sl.name AS status_label,
    c.name AS company_name,
    l.name AS location
  FROM battery_assets ba
  LEFT JOIN "snipe-it".models m ON ba.model_id = m.id
  LEFT JOIN "snipe-it".status_labels sl ON ba.status_id = sl.id
  LEFT JOIN "snipe-it".companies c ON ba.company_id = c.id
  LEFT JOIN "snipe-it".locations l ON ba.location_id = l.id
),
matched_tracker AS (
  SELECT
    ad.asset_tag,
    td.uniqueid AS position_tracker_id,
    td.attributes
  FROM asset_details ad
  LEFT JOIN traccar.tc_devices td ON EXISTS (
    SELECT 1
    FROM jsonb_array_elements(CAST(td.attributes AS jsonb)->'battery_pack') AS bp
    WHERE bp->>'asset_tag' = ad.asset_tag
  )
),
latest_measurements AS (
  SELECT DISTINCT ON (sm.master_identifier)
    sm.master_identifier,
    sm.master_battery_pack_voltage,
    sm.master_battery_pack_current,
    sm."SoC",
    sm."SoH",
    sm.battery_pack_state,
    sm."RCC",
    sm."SoCS",
    sm."SoDS",
    sm."CoC",
    sm.timestamp AS electrical_data_updatedAt
  FROM goodenough.battery_pack__standard_measurements sm
  ORDER BY sm.master_identifier, sm.timestamp DESC
)
SELECT jsonb_pretty(jsonb_build_object(
  'asset_tag', ad.asset_tag,
  'status_label', ad.status_label,
  'model', ad.model,
  'company_name', ad.company_name,
  'warranty_duration', COALESCE(ad.warranty_months, 0),
  'location', COALESCE(ad.location, ''),
  'battery_pack', jsonb_build_object(
    'battery_cell_chemistry', COALESCE(ad.battery_cell_chemistry, ''),
    'battery_cell_temperatures', COALESCE(ad.battery_cell_temperatures, '""'),
    'battery_cell_type', COALESCE(ad.battery_cell_type, ''),
    'battery_cell_voltages', COALESCE(ad.battery_cell_voltages, '""'),
    'battery_pack_casing', COALESCE(ad.battery_pack_casing, ''),
    'battery_pack_nominal_charge_capacity', COALESCE(ad.battery_pack_nominal_charge_capacity::numeric, 0),
    'battery_pack_nominal_voltage', COALESCE(ad.battery_pack_nominal_voltage::numeric, 0),
    'battery_pack_state', COALESCE(lm.battery_pack_state, ''),
    'bms_manufacturer_name', 'Jiabaida',
    'bms_type', COALESCE(ad.bms_type, ''),
    'CoC', COALESCE(lm."CoC", 0),
    'electrical_data_updatedAt', COALESCE(to_char(lm.electrical_data_updatedAt, 'YYYY-MM-DD"T"HH24:MI:SS+00:00'), ''),
    'master_battery_pack_current', COALESCE(lm.master_battery_pack_current, 0),
    'master_battery_pack_voltage', COALESCE(lm.master_battery_pack_voltage, 0),
    'RCC', COALESCE(lm."RCC", 0),
    'SoC', COALESCE(lm."SoC", 0),
    'SoCS', COALESCE(lm."SoCS", ''),
    'SoDS', COALESCE(lm."SoDS", ''),
    'SoH', COALESCE(lm."SoH", 0)
  ),
  'set', jsonb_build_object(
    'battery_pack', jsonb_build_array(jsonb_build_object('asset_tag', ad.asset_tag)),
    'position_tracker', CASE WHEN mt.position_tracker_id IS NOT NULL
                             THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.position_tracker_id))
                             ELSE '[]'::jsonb END,
    'sim_card', CASE WHEN mt.attributes::jsonb ? 'SIM_card'
                     THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.attributes::jsonb->>'SIM_card'))
                     ELSE '[]'::jsonb END,
    'vehicle', CASE WHEN mt.attributes::jsonb ? 'vehicle'
                    THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.attributes::jsonb->>'vehicle'))
                    ELSE '[]'::jsonb END
  )
)) AS result
FROM asset_details ad
LEFT JOIN matched_tracker mt ON ad.asset_tag = mt.asset_tag
LEFT JOIN latest_measurements lm ON lm.master_identifier = CAST(mt.position_tracker_id AS int8);
"""


async def get_battery_pack_data() -> Dict[str, Any]:
    conn = await get_db_connection()
    try:
        result = await conn.fetch(BATTERY_PACK_QUERY)

        # Debug: Log the actual result to inspect its structure
        logging.debug(f"Query result: {result}")

        # Check if the result is in the expected format
        if result:
            # Parse the JSON string in the 'result' field
            parsed_result = []
            for record in result:
                # Load the JSON string into a dictionary
                try:
                    # Parse the result from JSON string to dictionary
                    record_data = json.loads(record["result"])

                    # Build the final structure
                    structured_result = {
                        "asset_tag": record_data["asset_tag"],
                        "status_label": record_data["status_label"],
                        "model": record_data["model"],
                        "company_name": record_data["company_name"],
                        "warranty_duration": record_data["warranty_duration"],
                        "location": record_data["location"],
                        "battery_pack": {
                            "battery_cell_chemistry": record_data["battery_pack"][
                                "battery_cell_chemistry"
                            ],
                            "battery_cell_temperatures": record_data["battery_pack"][
                                "battery_cell_temperatures"
                            ],
                            "battery_cell_type": record_data["battery_pack"][
                                "battery_cell_type"
                            ],
                            "battery_cell_voltages": record_data["battery_pack"][
                                "battery_cell_voltages"
                            ],
                            "battery_pack_casing": record_data["battery_pack"][
                                "battery_pack_casing"
                            ],
                            "battery_pack_nominal_charge_capacity": record_data[
                                "battery_pack"
                            ]["battery_pack_nominal_charge_capacity"],
                            "battery_pack_nominal_voltage": record_data["battery_pack"][
                                "battery_pack_nominal_voltage"
                            ],
                            "battery_pack_state": record_data["battery_pack"][
                                "battery_pack_state"
                            ],
                            "bms_manufacturer_name": record_data["battery_pack"][
                                "bms_manufacturer_name"
                            ],
                            "bms_type": record_data["battery_pack"]["bms_type"],
                            "CoC": record_data["battery_pack"]["CoC"],
                            "electrical_data_updatedAt": record_data["battery_pack"][
                                "electrical_data_updatedAt"
                            ],
                            "master_battery_pack_current": record_data["battery_pack"][
                                "master_battery_pack_current"
                            ],
                            "master_battery_pack_voltage": record_data["battery_pack"][
                                "master_battery_pack_voltage"
                            ],
                            "RCC": record_data["battery_pack"]["RCC"],
                            "SoC": record_data["battery_pack"]["SoC"],
                            "SoCS": record_data["battery_pack"]["SoCS"],
                            "SoDS": record_data["battery_pack"]["SoDS"],
                            "SoH": record_data["battery_pack"]["SoH"],
                        },
                        "set": {
                            "battery_pack": [{"asset_tag": record_data["asset_tag"]}],
                            "position_tracker": (
                                [{"asset_tag": record_data["asset_tag"]}]
                                if "position_tracker" in record_data
                                else []
                            ),
                            "sim_card": (
                                [{"asset_tag": record_data["asset_tag"]}]
                                if "sim_card" in record_data
                                else []
                            ),
                            "vehicle": (
                                [{"asset_tag": record_data["asset_tag"]}]
                                if "vehicle" in record_data
                                else []
                            ),
                        },
                    }

                    parsed_result.append(structured_result)
                except json.JSONDecodeError as e:
                    logging.error(f"Error parsing JSON: {e}")
                    return {"status": "error", "message": f"Error parsing JSON: {e}"}

            return {"status": "fetched", "result": parsed_result}
        else:
            return {"status": "error", "message": "No data fetched from the database"}
    except Exception as e:
        logging.error(f"Error fetching battery packs data: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        await release_db_connection(conn)


# import logging
# from ..db import get_db_connection, release_db_connection
# from asyncpg import Record

# # Query as a string
# BATTERY_PACK_QUERY = """
# WITH battery_assets AS (
#   SELECT
#     a.asset_tag,
#     a.model_id,
#     a.status_id,
#     a.company_id,
#     a.location_id,
#     a.warranty_months,
#     a._snipeit_battery_cell_chemistry_18 AS battery_cell_chemistry,
#     a._snipeit_battery_cell_temperatures_54 AS battery_cell_temperatures,
#     a._snipeit_battery_cell_type_24 AS battery_cell_type,
#     a._snipeit_battery_cell_voltages_53 AS battery_cell_voltages,
#     a._snipeit_battery_pack_casing_25 AS battery_pack_casing,
#     a._snipeit_battery_pack_nominal_charge_capacity_22 AS battery_pack_nominal_charge_capacity,
#     a._snipeit_battery_pack_nominal_voltage_21 AS battery_pack_nominal_voltage,
#     a._snipeit_bms_type_23 AS bms_type
#   FROM "snipe-it".assets a
#   WHERE a.model_id = 7
# ),
# asset_details AS (
#   SELECT
#     ba.*,
#     m.name AS model,
#     sl.name AS status_label,
#     c.name AS company_name,
#     l.name AS location
#   FROM battery_assets ba
#   LEFT JOIN "snipe-it".models m ON ba.model_id = m.id
#   LEFT JOIN "snipe-it".status_labels sl ON ba.status_id = sl.id
#   LEFT JOIN "snipe-it".companies c ON ba.company_id = c.id
#   LEFT JOIN "snipe-it".locations l ON ba.location_id = l.id
# ),
# matched_tracker AS (
#   SELECT
#     ad.asset_tag,
#     td.uniqueid AS position_tracker_id,
#     td.attributes
#   FROM asset_details ad
#   LEFT JOIN traccar.tc_devices td ON EXISTS (
#     SELECT 1
#     FROM jsonb_array_elements(CAST(td.attributes AS jsonb)->'battery_pack') AS bp
#     WHERE bp->>'asset_tag' = ad.asset_tag
#   )
# ),
# latest_measurements AS (
#   SELECT DISTINCT ON (sm.master_identifier)
#     sm.master_identifier,
#     sm.master_battery_pack_voltage,
#     sm.master_battery_pack_current,
#     sm."SoC",
#     sm."SoH",
#     sm.battery_pack_state,
#     sm."RCC",
#     sm."SoCS",
#     sm."SoDS",
#     sm."CoC",
#     sm.timestamp AS electrical_data_updatedAt
#   FROM goodenough.battery_pack__standard_measurements sm
#   ORDER BY sm.master_identifier, sm.timestamp DESC
# )
# SELECT jsonb_pretty(jsonb_build_object(
#   'asset_tag', ad.asset_tag,
#   'status_label', ad.status_label,
#   'model', ad.model,
#   'company_name', ad.company_name,
#   'warranty_duration', COALESCE(ad.warranty_months, 0),
#   'location', COALESCE(ad.location, ''),
#   'battery_pack', jsonb_build_object(
#     'battery_cell_chemistry', COALESCE(ad.battery_cell_chemistry, ''),
#     'battery_cell_temperatures', COALESCE(ad.battery_cell_temperatures, '""'),
#     'battery_cell_type', COALESCE(ad.battery_cell_type, ''),
#     'battery_cell_voltages', COALESCE(ad.battery_cell_voltages, '""'),
#     'battery_pack_casing', COALESCE(ad.battery_pack_casing, ''),
#     'battery_pack_nominal_charge_capacity', COALESCE(ad.battery_pack_nominal_charge_capacity::numeric, 0),
#     'battery_pack_nominal_voltage', COALESCE(ad.battery_pack_nominal_voltage::numeric, 0),
#     'battery_pack_state', COALESCE(lm.battery_pack_state, ''),
#     'bms_manufacturer_name', 'Jiabaida',
#     'bms_type', COALESCE(ad.bms_type, ''),
#     'CoC', COALESCE(lm."CoC", 0),
#     'electrical_data_updatedAt', COALESCE(to_char(lm.electrical_data_updatedAt, 'YYYY-MM-DD"T"HH24:MI:SS+00:00'), ''),
#     'master_battery_pack_current', COALESCE(lm.master_battery_pack_current, 0),
#     'master_battery_pack_voltage', COALESCE(lm.master_battery_pack_voltage, 0),
#     'RCC', COALESCE(lm."RCC", 0),
#     'SoC', COALESCE(lm."SoC", 0),
#     'SoCS', COALESCE(lm."SoCS", ''),
#     'SoDS', COALESCE(lm."SoDS", ''),
#     'SoH', COALESCE(lm."SoH", 0)
#   ),
#   'set', jsonb_build_object(
#     'battery_pack', jsonb_build_array(jsonb_build_object('asset_tag', ad.asset_tag)),
#     'position_tracker', CASE WHEN mt.position_tracker_id IS NOT NULL
#                              THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.position_tracker_id))
#                              ELSE '[]'::jsonb END,
#     'sim_card', CASE WHEN mt.attributes::jsonb ? 'SIM_card'
#                      THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.attributes::jsonb->>'SIM_card'))
#                      ELSE '[]'::jsonb END,
#     'vehicle', CASE WHEN mt.attributes::jsonb ? 'vehicle'
#                     THEN jsonb_build_array(jsonb_build_object('asset_tag', mt.attributes::jsonb->>'vehicle'))
#                     ELSE '[]'::jsonb END
#   )
# )) AS structured_output
# FROM asset_details ad
# LEFT JOIN matched_tracker mt ON ad.asset_tag = mt.asset_tag
# LEFT JOIN latest_measurements lm ON lm.master_identifier = CAST(mt.position_tracker_id AS int8);
# """


# async def get_battery_pack_data():
#     conn = await get_db_connection()  # Get a connection from the pool
#     try:
#         result = await conn.fetch(BATTERY_PACK_QUERY)  # Fetch the data
#         formatted_result = [
#             dict(record) for record in result
#         ]  # Convert the result to a list of dictionaries
#         return formatted_result
#     finally:
#         await release_db_connection(conn)  # Release the connection a
