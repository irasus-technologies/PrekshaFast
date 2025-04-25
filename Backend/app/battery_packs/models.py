# models.py

from pydantic import BaseModel
from typing import List, Optional


class BatteryPack(BaseModel):
    battery_cell_chemistry: str
    battery_cell_temperatures: str
    battery_cell_type: str
    battery_cell_voltages: str
    battery_pack_casing: str
    battery_pack_nominal_charge_capacity: int
    battery_pack_nominal_voltage: int
    battery_pack_state: str
    bms_manufacturer_name: str
    bms_type: str
    CoC: int
    electrical_data_updatedAt: str
    master_battery_pack_current: int
    master_battery_pack_voltage: float
    RCC: int
    SoC: int
    SoCS: str
    SoDS: str
    SoH: int


class Set(BaseModel):
    battery_pack: List[dict]
    position_tracker: List[dict]
    sim_card: List[dict]
    vehicle: List[dict]


class BatteryPackItem(BaseModel):
    asset_tag: str
    status_label: str
    model: str
    company_name: str
    warranty_duration: int
    location: str
    battery_pack: BatteryPack
    set: Set


class BatteryPackResponse(BaseModel):
    __root__: List[BatteryPackItem]
