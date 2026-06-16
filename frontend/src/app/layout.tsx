import type { Metadata } from "next";
import { Noto_Sans_Arabic } from "next/font/google";
import "./globals.css";

const notoSansArabic = Noto_Sans_Arabic({
  variable: "--font-noto-sans-arabic",
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "مستشفى الشركات — لوحة التحكم",
  description: "نظام تشغيل ذكي للشركات العربية",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html dir="rtl" lang="ar" className={`${notoSansArabic.variable} h-full`}>
      <body className="min-h-full bg-[#F9FAFB] font-sans">{children}</body>
    </html>
  );
}
