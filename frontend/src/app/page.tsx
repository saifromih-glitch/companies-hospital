"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F9FAFB]">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-gray-200 border-t-gold rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-500">جاري التحميل...</p>
      </div>
    </div>
  );
}
