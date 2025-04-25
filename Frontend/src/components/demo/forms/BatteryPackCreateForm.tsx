// src/components/forms/BatteryPackCreateForm.tsx
"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const batterySchema = z.object({
    battery_id: z.string().min(1, "Battery ID is required"),
    capacity_kWh: z.string().min(1, "Capacity is required"),
    manufacturer: z.string(),
});

type BatteryFormData = z.infer<typeof batterySchema>;

export default function BatteryPackCreateForm() {
    const form = useForm<BatteryFormData>({
        resolver: zodResolver(batterySchema),
        defaultValues: {
            battery_id: "",
            capacity_kWh: "",
            manufacturer: "",
        },
    });

    const onSubmit = (data: BatteryFormData) => {
        console.log("Battery Form Submitted:", data);
    };

    return (
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <Input
                {...form.register("battery_id")}
                placeholder="Battery ID"
            />
            <Input
                {...form.register("capacity_kWh")}
                placeholder="Capacity (kWh)"
            />
            <Input
                {...form.register("manufacturer")}
                placeholder="Manufacturer"
            />
            <Button type="submit">Submit Battery Pack</Button>
        </form>
    );
}
