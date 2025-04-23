"use client";

import Link from "next/link";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/demo/tables/DataTable";

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
        <ContentLayout title="Vehicles">
            <Breadcrumb>
                <BreadcrumbList>
                    <BreadcrumbItem>
                        <BreadcrumbLink asChild>
                            <Link href="/dashboard">Dashboard</Link>
                        </BreadcrumbLink>
                    </BreadcrumbItem>
                    <BreadcrumbSeparator />
                    <BreadcrumbItem>
                        <BreadcrumbPage>Vehicles</BreadcrumbPage>
                    </BreadcrumbItem>
                </BreadcrumbList>
            </Breadcrumb>

            <div className="max-w-7xl mx-auto py-8">
                <h1 className="text-2xl font-bold mb-4">Vehicles</h1>

                <DataTable
                    columns={vehiclesColumns}
                    data={demoVehicles}
                    loading={false}
                    enableSearch
                    enableMultiSelect
                    enableColumnToggle
                    enableRowActions
                    visibleCols={[
                        "asset_tag",
                        "category_name",
                        "company",
                        "model",
                        "serial",
                        "status_label",
                    ]}
                />
            </div>
        </ContentLayout>
    );
}
