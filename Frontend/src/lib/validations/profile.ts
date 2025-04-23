import { z } from "zod";

export const ProfileFormValidation = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.string(),
  password: z.string().min(8, "Password must be at least 8 characters"),
  profileImage: z
    .instanceof(File)
    .or(z.string().nullable())
    .optional()
    .refine(
      (file) => {
        if (file instanceof File) return file.size <= 5 * 1024 * 1024;
        return true;
      },
      { message: "Image must be less than 5MB" }
    ),
});

export const ChangePasswordValidation = z.object({
    oldPassword: z.string().min(6, 'Old password is required'),
    newPassword: z.string().min(8, 'New password must be at least 8 characters'),
    confirmPassword: z.string().min(8, 'Confirm password must be at least 8 characters'),
}).refine((data) => data.newPassword === data.confirmPassword, {
    path: ['confirmPassword'],
    message: 'Passwords must match',
});