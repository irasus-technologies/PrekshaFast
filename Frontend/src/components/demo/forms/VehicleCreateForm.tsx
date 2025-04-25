// src/components/forms/VehicleCreateForm.tsx
"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const vehicleSchema = z.object({
    asset_tag: z.string().min(1, "Asset tag is required"),
    model: z.string().min(1, "Model is required"),
    company: z.string().min(1, "Company is required"),
    status: z.string(),
});

type VehicleFormData = z.infer<typeof vehicleSchema>;

export default function VehicleCreateForm() {
    const form = useForm<VehicleFormData>({
        resolver: zodResolver(vehicleSchema),
        defaultValues: {
            asset_tag: "",
            model: "",
            company: "",
            status: "Available",
        },
    });

    const onSubmit = (data: VehicleFormData) => {
        console.log("Vehicle Form Submitted:", data);
    };

    return (
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <Input
                {...form.register("asset_tag")}
                placeholder="Asset Tag"
            />
            <Input
                {...form.register("model")}
                placeholder="Model"
            />
            <Input
                {...form.register("company")}
                placeholder="Company"
            />
            <Input
                {...form.register("status")}
                placeholder="Status"
            />
            <Button type="submit">Submit Vehicle</Button>
        </form>
    );
}
