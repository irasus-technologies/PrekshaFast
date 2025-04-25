// src/app/(demo)/[asset]/create/page.tsx
"use client";

import { useParams } from "next/navigation";
import VehicleCreateForm from "@/components/demo/forms/VehicleCreateForm"; // Replace with actual form component import for each asset type.
import BatteryPackCreateForm from "@/components/demo/forms/BatteryPackCreateForm";
import NotFound from "@/components/common/NotFound"; // fallback if needed

export default function AssetCreatePage() {
    const { asset } = useParams<{ asset: string }>();

    const renderForm = () => {
        switch (asset) {
            case "vehicles":
                return <VehicleCreateForm />;
            case "battery-pack":
                return <BatteryPackCreateForm />;
            default:
                return <NotFound message={`No form configured for "${asset}"`} />;
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <h1 className="text-2xl font-bold capitalize">{asset} - Create</h1>
            {renderForm()}
        </div>
    );
}
