"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import Card from "@/components/ui/Card";
import { useAuth } from "@/hooks/useAuth";
import { getRecentCases, Case } from "@/lib/api";

const severityLabels: Record<string, string> = {
  critical: "🚨 حرجة",
  high: "🔴 عالية",
  medium: "🟡 متوسطة",
  low: "🟢 منخفضة",
};

const severityColors: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-blue-100 text-blue-700",
  low: "bg-gray-100 text-gray-700",
};

export default function CasesPage() {
  const { token, loading: authLoading } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!token) return;

    getRecentCases(token)
      .then(setCases)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  const filteredCases = cases.filter((c) => {
    if (filter === "all") return true;
    return c.severity === filter;
  });

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-gold rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-navy mb-2">📋 الحالات</h1>
              <p className="text-gray-500">جميع الحالات المسجلة في النظام</p>
            </div>

            <div className="flex gap-3 mb-6">
              {[
                { value: "all", label: "الكل" },
                { value: "critical", label: "حرجة" },
                { value: "high", label: "عالية" },
                { value: "medium", label: "متوسطة" },
                { value: "low", label: "منخفضة" },
              ].map((f) => (
                <button
                  key={f.value}
                  onClick={() => setFilter(f.value)}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
                    filter === f.value
                      ? "bg-navy text-white"
                      : "bg-white text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            <Card>
              {filteredCases.length === 0 ? (
                <p className="text-gray-500 text-center py-12">لا توجد حالات</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">العنوان</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">المجال</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">الخطورة</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">الكلمات المفتاحية</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">التاريخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredCases.map((c) => (
                        <tr key={c.id} className="border-b border-gray-50 hover:bg-gray-50">
                          <td className="py-4 px-4">
                            <p className="text-sm font-medium text-gray-900">{c.title}</p>
                            <p className="text-xs text-gray-500 mt-1 line-clamp-1">{c.description}</p>
                          </td>
                          <td className="py-4 px-4 text-sm text-gray-500">{c.category}</td>
                          <td className="py-4 px-4">
                            <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${severityColors[c.severity]}`}>
                              {severityLabels[c.severity]}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <div className="flex flex-wrap gap-1">
                              {c.triage_result?.keywords?.slice(0, 3).map((k) => (
                                <span key={k} className="inline-block bg-gray-100 text-gray-600 px-2 py-1 rounded-lg text-xs">
                                  {k}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="py-4 px-4 text-sm text-gray-500">
                            {new Date(c.created_at).toLocaleDateString("ar-SA")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
