"use client";

import { ColumnDef } from "@tanstack/react-table";
import { AssetTablePage } from "@/components/demo/pages/AssetTablePage";

interface Vehicle {
    asset_tag: string;
    category_name: string;
    company: string;
    model: string;
    serial: string;
    status_label: string;
    created_at: string;
    updated_at: string;
    vehicle_registration_number: string | null;
    last_checkin: string | null;
    last_checkout: string | null;
}

const demoVehicles: Vehicle[] = [
    {
        asset_tag: "VH-1001",
        category_name: "SUV",
        company: "Toyota",
        model: "Highlander",
        serial: "SN-12345",
        status_label: "Available",
        created_at: "2024-01-10",
        updated_at: "2024-04-10",
        vehicle_registration_number: "TX-7890",
        last_checkin: "2024-04-10",
        last_checkout: "2024-04-01",
    },
    {
        asset_tag: "VH-1002",
        category_name: "Truck",
        company: "Ford",
        model: "F-150",
        serial: "SN-67890",
        status_label: "In Maintenance",
        created_at: "2023-11-15",
        updated_at: "2024-03-20",
        vehicle_registration_number: "CA-4567",
        last_checkin: "2024-03-15",
        last_checkout: "2024-03-01",
    },
    {
        asset_tag: "VH-1003",
        category_name: "Sedan",
        company: "Honda",
        model: "Civic",
        serial: "SN-54321",
        status_label: "Checked Out",
        created_at: "2024-02-01",
        updated_at: "2024-04-18",
        vehicle_registration_number: "NY-3210",
        last_checkin: null,
        last_checkout: "2024-04-18",
    },
    {
        asset_tag: "VH-1004",
        category_name: "Hatchback",
        company: "Hyundai",
        model: "i20",
        serial: "SN-11223",
        status_label: "Available",
        created_at: "2024-01-20",
        updated_at: "2024-04-01",
        vehicle_registration_number: "FL-1111",
        last_checkin: "2024-04-01",
        last_checkout: "2024-03-25",
    },
    {
        asset_tag: "VH-1005",
        category_name: "Electric",
        company: "Tesla",
        model: "Model 3",
        serial: "SN-33445",
        status_label: "Charging",
        created_at: "2023-12-10",
        updated_at: "2024-04-11",
        vehicle_registration_number: "NV-9999",
        last_checkin: "2024-04-10",
        last_checkout: "2024-03-30",
    },
    {
        asset_tag: "VH-1006",
        category_name: "SUV",
        company: "Kia",
        model: "Seltos",
        serial: "SN-55667",
        status_label: "Available",
        created_at: "2023-10-01",
        updated_at: "2024-02-15",
        vehicle_registration_number: "TX-2222",
        last_checkin: "2024-02-14",
        last_checkout: "2024-02-01",
    },
    {
        asset_tag: "VH-1007",
        category_name: "Pickup",
        company: "Chevrolet",
        model: "Colorado",
        serial: "SN-99887",
        status_label: "Available",
        created_at: "2024-03-10",
        updated_at: "2024-04-09",
        vehicle_registration_number: "AZ-7788",
        last_checkin: "2024-04-09",
        last_checkout: "2024-03-25",
    },
    {
        asset_tag: "VH-1008",
        category_name: "Sedan",
        company: "Nissan",
        model: "Altima",
        serial: "SN-44556",
        status_label: "In Maintenance",
        created_at: "2023-09-12",
        updated_at: "2024-04-12",
        vehicle_registration_number: "IL-2233",
        last_checkin: "2024-04-11",
        last_checkout: "2024-03-28",
    },
    {
        asset_tag: "VH-1009",
        category_name: "Van",
        company: "Mercedes",
        model: "Sprinter",
        serial: "SN-77441",
        status_label: "Checked Out",
        created_at: "2024-01-05",
        updated_at: "2024-04-08",
        vehicle_registration_number: "WA-8877",
        last_checkin: null,
        last_checkout: "2024-04-07",
    },
    {
        asset_tag: "VH-1010",
        category_name: "Electric",
        company: "Rivian",
        model: "R1T",
        serial: "SN-66889",
        status_label: "Available",
        created_at: "2024-02-18",
        updated_at: "2024-04-13",
        vehicle_registration_number: "CO-3344",
        last_checkin: "2024-04-13",
        last_checkout: "2024-03-29",
    },
];

const vehiclesColumns: ColumnDef<Vehicle>[] = [
    { accessorKey: "asset_tag", header: "Asset Tag" },
    { accessorKey: "category_name", header: "Category" },
    { accessorKey: "company", header: "Company" },
    { accessorKey: "model", header: "Model" },
    { accessorKey: "serial", header: "Serial" },
    { accessorKey: "status_label", header: "Status" },
    { accessorKey: "vehicle_registration_number", header: "Registration Number" },
    { accessorKey: "last_checkin", header: "Last Check-In" },
    { accessorKey: "last_checkout", header: "Last Check-Out" },
    { accessorKey: "created_at", header: "Created At" },
    { accessorKey: "updated_at", header: "Updated At" },
];

export default function VehiclesDemoPage() {
    return (
        <AssetTablePage
            title="Vehicles"
            header="Vehicle Management"
            subtitle="Monitor and control vehicle assets efficiently"
            columns={vehiclesColumns}
            data={demoVehicles}
            visibleCols={[
                "asset_tag",
                "category_name",
                "company",
                "model",
                "serial",
                "status_label",
            ]}
            breadcrumbs={[
                { label: "Dashboard", href: "/dashboard" },
                { label: "Vehicles" },
            ]}
            bulkActions={[
                { label: "Bulk Create", href: "/vehicles/bulk-create" },
                { label: "Bulk Edit", href: "/vehicles/bulk-edit" },
            ]}
            clickableColumns={["asset_tag", "company"]}
        />
    );
}
