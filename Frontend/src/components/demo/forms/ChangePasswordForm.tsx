import { useForm, FormProvider } from 'react-hook-form';

import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import CustomFormField from '@/components/demo/component/CustomFormField';
import { FormFieldType } from '@/components/demo/component/CustomFormField';
import { ChangePasswordValidation } from '@/lib/validations/profile';

// Validation schema for password change


interface ChangePasswordFormProps {
    onSubmit: (data: { oldPassword: string; newPassword: string; confirmPassword: string }) => void;
}

const ChangePasswordForm: React.FC<ChangePasswordFormProps> = ({ onSubmit }) => {
    const formMethods = useForm({
        resolver: zodResolver(ChangePasswordValidation),
        defaultValues: {
            oldPassword: '',
            newPassword: '',
            confirmPassword: '',
        },
    });

    return (
        <FormProvider {...formMethods}>
            <form onSubmit={formMethods.handleSubmit(onSubmit)}>
                <div className="space-y-4">
                    {/* Old Password Field */}
                    <CustomFormField
                        control={formMethods.control}
                        fieldType={FormFieldType.INPUT}
                        name="oldPassword"
                        label="Old Password"
                        placeholder="Enter old password"
                        // iconSrc="/assets/icons/lock.svg"
                        iconAlt="old password"
                    />

                    {/* New Password Field */}
                    <CustomFormField
                        control={formMethods.control}
                        fieldType={FormFieldType.INPUT}
                        name="newPassword"
                        label="New Password"
                        placeholder="Enter new password"
                        // iconSrc="/assets/icons/lock.svg"
                        iconAlt="new password"
                    />

                    {/* Confirm Password Field */}
                    <CustomFormField
                        control={formMethods.control}
                        fieldType={FormFieldType.INPUT}
                        name="confirmPassword"
                        label="Confirm Password"
                        placeholder="Confirm new password"
                        // iconSrc="/assets/icons/lock.svg"
                        iconAlt="confirm password"
                    />
                </div>

                <div className="mt-6">
                    <Button type="submit" className="w-full">
                        Submit
                    </Button>
                </div>
            </form>
        </FormProvider>
    );
};

export default ChangePasswordForm;
