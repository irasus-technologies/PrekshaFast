"use client";

import Link from "next/link";
import Image from "next/image";
import { PanelsTopLeft } from "lucide-react";
import { ArrowRightIcon, GitHubLogoIcon } from "@radix-ui/react-icons";

import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/mode-toggle";
import { useUser } from "@/lib/useUser";
import { useRouter } from "next/navigation";
import { useEffect } from 'react';

export default function HomePage() {
  const { user, loading } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-lg font-medium">Checking authentication...</p>
      </main>
    </div>
  );
}
