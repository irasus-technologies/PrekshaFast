"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
// import axios from "axios";
// Using chadcn components for Tabs, Button, etc.
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

import { Button } from "@/components/ui/button";
import ProfileTabContent from "../component/ProfileTabContent";
// import ProfileForm from "./Forms/ProfileForm";
// import BrandingForm from "./Forms/BrandingForm";
// import ActivityLog from "./Tables/ActivityLog";
// import ContactPage from "./Forms/ContactPage";
// import { useAuth } from "@/context/AuthContext";
// import CompanyPage from "./CompanyPage";
// import { useUserStore } from "@/context/useUserStore";

// export function useFetchActivityLog() {
//     const { isAuthenticated, token } = useAuth(); // Assuming useAuth provides token and authentication state
//     const [data, setData] = useState(null);
//     const [loading, setLoading] = useState(true);
//     const [error, setError] = useState<string | null>(null);

//     useEffect(() => {
//         const fetchActivityLog = async () => {
//             if (!isAuthenticated || !token) {
//                 console.error("User is not authenticated or token is missing.");
//                 setError("Unauthorized");
//                 setLoading(false);
//                 return;
//             }

//             try {
//                 // Call the internal API route
//                 const response = await axios.get('/api/activity_log/', {
//                     headers: {
//                         Authorization: `Bearer ${token}`, // Pass token to API route
//                     },
//                 });

//                 setData(response.data.data); // Update state with the fetched data
//                 console.log(response)

//                 setLoading(false);
//             } catch (err) {
//                 console.error('Error fetching activity log:', err);
//                 setError('Failed to load data');
//                 setLoading(false);
//             }
//         };

//         fetchActivityLog();
//     }, [isAuthenticated, token]);

//     return { "data": data, loading, error };
// }

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState("profile");

    // const { isAuthenticated, token } = useAuth();

    // useEffect(() => {
    //     const fetchActivityLog = async () => {
    //         try {
    //             // Call the internal Next.js API route
    //             const response = await axios.get('/api/activity_log', {
    //                 headers: {
    //                     Authorization: `Bearer ${token}`, // Pass the token if required
    //                 },
    //             });
    //             setData(response.data);
    //         } catch (err) {
    //             console.error('Error fetching activity log:', err);
    //             setError('Failed to load data');
    //         } finally {
    //             setLoading(false);
    //         }
    //     };

    //     fetchActivityLog();
    // }, [token]);

    // const { data, loading, error } = useFetchActivityLog();
    // console.log(data, loading, error)
    return (
        <div className="max-w-7xl mx-auto py-8 ">
            <Link href="/dashboard" className="text-base text-primary hover:underline">
                &larr; Back to Dashboard
            </Link>

            <h1 className="text-2xl font-bold my-4">Settings</h1>
            <p className="text-sm text-muted">Manage profile, notifications, security, and account settings</p>

            <Tabs
                value={activeTab}
                onValueChange={(tab: any) => setActiveTab(tab)}
                className="space-y-6 mt-4"
            >
                <TabsList className="text-base">
                    <TabsTrigger value="profile">My Profile</TabsTrigger>
                    <TabsTrigger value="company">Company</TabsTrigger>
                    <TabsTrigger value="branding">Branding</TabsTrigger>
                    <TabsTrigger value="activity">Activity Log</TabsTrigger>
                    <TabsTrigger value="support">Support</TabsTrigger>
                </TabsList>

                <TabsContent value="profile">
                    <ProfileTabContent />
                </TabsContent>
                <TabsContent value="company">
                    {/* <CompanyPage /> */}
                </TabsContent>
                <TabsContent value="branding">
                    {/* <BrandingForm /> */}
                </TabsContent>
                <TabsContent value="activity">
                    {/* <ActivityLog data={data} loading={loading} error={error} /> */}
                </TabsContent>
                <TabsContent value="support">
                    {/* <ContactPage /> */}
                </TabsContent>
            </Tabs>

            {/* <Button className="mt-8 bg-blue-600 hover:bg-blue-700 text-white">
                Save Changes
            </Button> */}
        </div>
    );
}

// export function ProfileTabContent() {
//     const [profileImage, setProfileImage] = useState("/profile-placeholder.jpg"); // Placeholder image
//     const user = useUserStore((state) => state.user);
//     console.log(user)
//     const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
//         const file = e.target.files?.[0];
//         if (file) {
//             const imageUrl = URL.createObjectURL(file);
//             setProfileImage(imageUrl); // Preview the uploaded image
//         }
//     };

//     return (
//         <div className="space-y-8  p-4">
//             {/* Save Changes Button */}
//             <ProfileForm />
//         </div>
//     );
// }
