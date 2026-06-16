"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import Card from "@/components/ui/Card";

export default function RegisterCompanyPage() {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [size, setSize] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);

    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "https://companies-hospital-production.up.railway.app"}/api/v1/companies`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ name, industry, size, email }),
        }
      );

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "فشل تسجيل الشركة");

      setSuccess(true);
      setName("");
      setIndustry("");
      setSize("");
      setEmail("");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          <div className="max-w-2xl mx-auto">
            <Card>
              <h1 className="text-2xl font-bold text-navy mb-2">🏢 تسجيل شركة جديدة</h1>
              <p className="text-gray-500 mb-6">أضف شركتك للنظام لتتمكن من استخدام خدمات المستشفى</p>

              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm">
                  {error}
                </div>
              )}

              {success && (
                <div className="bg-green-50 text-green-600 p-4 rounded-xl mb-6 text-sm">
                  تم تسجيل الشركة بنجاح!
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    اسم الشركة
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="مثال: شركة الأفق للتقنية"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      القطاع
                    </label>
                    <select
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      required
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                    >
                      <option value="">اختر القطاع</option>
                      <option value="technology">تقنية</option>
                      <option value="finance">مالية</option>
                      <option value="healthcare">صحة</option>
                      <option value="education">تعليم</option>
                      <option value="retail">تجزئة</option>
                      <option value="manufacturing">تصنيع</option>
                      <option value="other">أخرى</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      الحجم
                    </label>
                    <select
                      value={size}
                      onChange={(e) => setSize(e.target.value)}
                      required
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                    >
                      <option value="">اختر الحجم</option>
                      <option value="startup">شركة ناشئة (1-10)</option>
                      <option value="small">صغيرة (11-50)</option>
                      <option value="medium">متوسطة (51-200)</option>
                      <option value="large">كبيرة (201-1000)</option>
                      <option value="enterprise">مؤسسة (1000+)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    البريد الإلكتروني للشركة
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="info@company.com"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-navy text-white rounded-xl font-bold text-lg hover:bg-navy-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "جاري التسجيل..." : "تسجيل الشركة"}
                </button>
              </form>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
