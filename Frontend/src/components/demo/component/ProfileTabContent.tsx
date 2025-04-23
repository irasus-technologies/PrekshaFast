"use client";

import { useState, useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ProfileFormValidation } from "@/lib/validations/profile";
import CustomFormField from '@/components/demo/component/CustomFormField'// adjust path
import SubmitButton from "@/components/demo/component/SubmitButton";
import Modal from "@/components/ui/modal";
import ChangePasswordForm from "@/components/demo/forms/ChangePasswordForm";
import { useUser } from "@/lib/useUser";
import { SelectItem } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

export enum FormFieldType {
    INPUT = "input",
    TEXTAREA = "textarea",
    PHONE_INPUT = "phoneInput",
    CHECKBOX = "checkbox",
    DATE_PICKER = "datePicker",
    SELECT = "select",
    RADIO = "radio",
    CHECKBOX_GROUP = "checkbox_group",
    SKELETON = "skeleton",
    IMAGE_UPLOAD = "imageUpload",
}

export default function ProfileTabContent() {
    const { user, loading } = useUser();
    const [isModalOpen, setModalOpen] = useState(false);

    const form = useForm<z.infer<typeof ProfileFormValidation>>({
        resolver: zodResolver(ProfileFormValidation),
        defaultValues: {
            username: "",
            email: "",
            role: "User",
            password: "",
            profileImage: null,
        },
    });

    useEffect(() => {
        if (user && !loading) {
            form.reset({
                username: user.name ?? "",
                email: user.email ?? "",
                role: user.role ?? "User",
                password: "",
                profileImage: null,
            });
        }
    }, [user, loading, form]);

    const onSubmit = (data: z.infer<typeof ProfileFormValidation>) => {
        console.log("Form submitted:", data);
    };

    const handlePasswordChange = (data: {
        oldPassword: string;
        newPassword: string;
        confirmPassword: string;
    }) => {
        console.log("Password change submitted:", data);
        setModalOpen(false);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <FormProvider {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="bg-white rounded-md p-6">
                    <CustomFormField
                        control={form.control}
                        fieldType={FormFieldType.IMAGE_UPLOAD}
                        name="profileImage"
                        label="Profile Image"
                    />
                </div>

                <div className="bg-white rounded-md p-6 space-y-4">
                    <CustomFormField
                        control={form.control}
                        fieldType={FormFieldType.INPUT}
                        name="username"
                        label="Username"
                        placeholder="John Doe"
                    />

                    <CustomFormField
                        control={form.control}
                        fieldType={FormFieldType.INPUT}
                        name="email"
                        label="Email"
                        placeholder="johndoe@example.com"
                    />

                    <CustomFormField
                        control={form.control}
                        fieldType={FormFieldType.SELECT}
                        name="role"
                        label="Role"
                        placeholder="Select role"
                    >
                        <SelectItem value="Super Admin">Super Admin</SelectItem>
                        <SelectItem value="Admin">Admin</SelectItem>
                        <SelectItem value="User">User</SelectItem>
                    </CustomFormField>

                    <CustomFormField
                        control={form.control}
                        fieldType={FormFieldType.INPUT}
                        name="password"
                        label="Password"
                        placeholder="********"
                    />

                    <Button type="button" variant="ghost" onClick={() => setModalOpen(true)}>
                        Change Password
                    </Button>
                </div>

                <SubmitButton>Save Changes</SubmitButton>

                <Modal
                    isOpen={isModalOpen}
                    onClose={() => setModalOpen(false)}
                    title="Change Password"
                >
                    <ChangePasswordForm onSubmit={handlePasswordChange} />
                </Modal>
            </form>
        </FormProvider>
    );
}
