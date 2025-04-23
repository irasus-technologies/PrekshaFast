
import React, { useState } from 'react'
import { E164Number } from "libphonenumber-js/core";
import {

    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Control } from 'react-hook-form'

import Image from 'next/image'
import 'react-phone-number-input/style.css'
import PhoneInput from 'react-phone-number-input'

import ReactDatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectTrigger, SelectValue, SelectContent } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

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
    IMAGE_UPLOAD = "imageUpload"
}

interface CustomProps {

    control: Control<any>,
    fieldType: FormFieldType,
    name: string,
    label?: string,
    placeholder?: string,
    iconSrc?: string,
    iconAlt?: string,
    disabled?: boolean,
    dateFormat?: string,
    showTimeSelect?: boolean,
    children?: React.ReactNode,

    renderSkeleton?: (field: any) => React.ReactNode
    type?: string,
}

const RenderField = ({ field, props }: { field: any; props: CustomProps }) => {
    const [showPassword, setShowPassword] = useState(false);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };
    switch (props.fieldType) {
        case FormFieldType.INPUT:
            const isPasswordField = props.name === "password";
            return (
                <div className="flex rounded-md border border-dark-500 bg-dark-400">
                    {props.iconSrc && (
                        <Image
                            src={props.iconSrc}
                            height={24}
                            width={24}
                            alt={props.iconAlt || "icon"}
                            className="ml-2"
                        />
                    )}
                    <FormControl>
                        <Input
                            placeholder={props.placeholder}
                            {...field}
                            type={isPasswordField && !showPassword ? "password" : "text"} // Toggle input type
                            className="shad-input border-0"
                        />
                    </FormControl>
                    {isPasswordField && (
                        <button type="button" onClick={togglePasswordVisibility} className="p-2">
                            <Image
                                src={showPassword ? "/eye.svg" : "/eye-off.svg"}
                                height={20}
                                width={20}
                                alt={showPassword ? "Hide " : "Show "}
                            />
                        </button>
                    )}
                </div>
            );
        case FormFieldType.TEXTAREA:
            return (
                <FormControl>
                    <Textarea
                        placeholder={props.placeholder}
                        {...field}
                        className="shad-textArea"
                        disabled={props.disabled}
                    />
                </FormControl>
            );
        case FormFieldType.PHONE_INPUT:

            return (
                <FormControl>
                    <PhoneInput
                        defaultCountry="US"
                        placeholder={props.placeholder}
                        international
                        withCountryCallingCode
                        value={field.value as E164Number | undefined}
                        onChange={field.onChange}
                        className="input-phone"
                    />
                </FormControl>
            );
        case FormFieldType.CHECKBOX:
            return (
                <FormControl>
                    <div className="flex items-center gap-4">
                        <Checkbox
                            id={props.name}
                            checked={field.value}
                            onCheckedChange={field.onChange}
                        />
                        <label htmlFor={props.name} className="checkbox-label">
                            {props.label}
                        </label>
                    </div>
                </FormControl>
            );
        case FormFieldType.DATE_PICKER:
            return (
                <div className="flex rounded-md border border-dark-500 bg-dark-400">
                    <Image
                        src="/assets/icons/calendar.svg"
                        height={24}
                        width={24}
                        alt="user"
                        className="ml-2"
                    />
                    <FormControl>
                        <ReactDatePicker
                            showTimeSelect={props.showTimeSelect ?? false}
                            selected={field.value}
                            onChange={(date: Date | null) => field.onChange(date)} // Allow null for date
                            timeInputLabel="Time:"
                            dateFormat={props.dateFormat ?? "MM/dd/yyyy"}
                            wrapperClassName="date-picker"
                        />
                    </FormControl>
                </div>
            );
        case FormFieldType.SELECT:
            return (
                <FormControl>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                            <SelectTrigger className="shad-select-trigger">
                                <SelectValue placeholder={props.placeholder} />
                            </SelectTrigger>
                        </FormControl>
                        <SelectContent className="shad-select-content">
                            {props.children}
                        </SelectContent>
                    </Select>
                </FormControl>
            );
        case FormFieldType.IMAGE_UPLOAD:


            const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const file = e.target.files?.[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        setImagePreview(reader.result as string);
                        field.onChange(file); // Set the file into react-hook-form
                    };
                    reader.readAsDataURL(file);
                }
            };

            return (
                <div className="flex items-center space-x-4">
                    {imagePreview ? (
                        <Image
                            src={imagePreview}
                            alt="Profile Image Preview"
                            width={100}
                            height={100}
                            className="rounded-full border border-dark-500"
                        />
                    ) : (
                        <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                            <span>No Image</span>
                        </div>
                    )}
                    <div className='flex flex-col space-y-2'>
                        <div className="flex justify-center items-center space-x-2 ">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                className="hidden"
                                id="profileImage"
                            />
                            <label htmlFor="profileImage" className="cursor-pointer">
                                <Button
                                    variant='default'
                                    type="button"
                                    onClick={() => {
                                        setImagePreview(null);
                                        field.onChange(null); // Reset image field
                                    }}
                                >
                                    Upload
                                </Button>
                            </label>
                            <Button
                                variant={'destructive'}
                                type="button"
                                onClick={() => {
                                    setImagePreview(null);
                                    field.onChange(null); // Reset image field
                                }}
                            >
                                Remove
                            </Button>
                        </div>
                        <span className="text-sm text-gray-500">
                            Supported Formats: PNG, JPEG, JPG (max: 5MB)
                        </span>
                    </div>
                </div>
            );
        case FormFieldType.SKELETON:
            return props.renderSkeleton ? props.renderSkeleton(field) : null;
        default:
            return null;
    }
};

const CustomFormField = (props: CustomProps) => {
    const { control, fieldType, name, label, placeholder, iconSrc, iconAlt, disabled, dateFormat, showTimeSelect, children, renderSkeleton } = props
    return (
        <FormField
            control={control}
            name={name}
            render={({ field }) => (

                <FormItem className='flex-1'>
                    {fieldType !== FormFieldType.CHECKBOX && label &&
                        (
                            <FormLabel>{label}</FormLabel>
                        )
                    }

                    <RenderField field={field} props={props} />
                    <FormMessage className='shad-error' />
                </FormItem>
            )}
        />
    )
}

export default CustomFormField