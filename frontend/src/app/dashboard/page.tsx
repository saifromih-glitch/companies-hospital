"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import StatCard from "@/components/ui/StatCard";
import Card from "@/components/ui/Card";
import { useAuth } from "@/hooks/useAuth";
import { getRecentCases, getDashboardStats, Case, DashboardStats } from "@/lib/api";

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

export default function DashboardPage() {
  const { user, token, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    Promise.all([getDashboardStats(token), getRecentCases(token)])
      .then(([statsData, casesData]) => {
        setStats(statsData);
        setCases(casesData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

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
            <div className="mb-8 bg-gradient-to-l from-navy to-navy-light rounded-2xl p-8 text-white">
              <h1 className="text-3xl font-bold mb-2">
                &#x645;&#x631;&#x62D;&#x628;&#x627; &#x628;&#x643; &#x641;&#x64A; &#x645;&#x633;&#x62A;&#x634;&#x641;&#x649; &#x627;&#x644;&#x634;&#x631;&#x643;&#x627;&#x62A;
              </h1>
              <p className="text-gold-light text-lg font-semibold">
                &#x627;&#x644;&#x645;&#x646;&#x635;&#x629; &#x627;&#x644;&#x631;&#x626;&#x64A;&#x633;&#x64A;&#x629; &#x644;&#x644;&#x62A;&#x634;&#x62E;&#x64A;&#x635; &#x627;&#x644;&#x630;&#x643;&#x64A; &#x639;&#x644;&#x649; &#x627;&#x644;&#x62D;&#x627;&#x644;&#x627;&#x62A; &#x627;&#x644;&#x639;&#x631;&#x628;&#x64A;&#x629;
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="إجمالي الحالات"
                value={stats?.total_cases || 0}
                icon="📋"
                change="+5 حالات هذا الأسبوع"
                changeType="positive"
              />
              <StatCard
                title="الحالات النشطة"
                value={stats?.active_cases || 0}
                icon="🔄"
                change="3 حالات تحتاج متابعة"
                changeType="neutral"
              />
              <StatCard
                title="الشركات المسجلة"
                value={stats?.total_companies || 0}
                icon="🏢"
                change="+2 شركات جديدة"
                changeType="positive"
              />
              <StatCard
                title="الحالات الحرجة"
                value={stats?.cases_by_severity?.critical || 0}
                icon="🚨"
                change="تحتاج تدخل فوري"
                changeType="negative"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <Card className="lg:col-span-2">
                <h2 className="text-lg font-bold text-navy mb-4">الحالات الأخيرة</h2>
                {cases.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">لا توجد حالات بعد</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-100">
                          <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">العنوان</th>
                          <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">المجال</th>
                          <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">الخطورة</th>
                          <th className="text-right py-3 px-4 text-sm font-semibold text-gray-500">التاريخ</th>
                        </tr>
                      </thead>
                      <tbody>
                        {cases.map((c) => (
                          <tr key={c.id} className="border-b border-gray-50 hover:bg-gray-50">
                            <td className="py-3 px-4 text-sm font-medium text-gray-900">{c.title}</td>
                            <td className="py-3 px-4 text-sm text-gray-500">{c.category}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${severityColors[c.severity]}`}>
                                {severityLabels[c.severity]}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-500">
                              {new Date(c.created_at).toLocaleDateString("ar-SA")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>

              <Card>
                <h2 className="text-lg font-bold text-navy mb-4">إجراءات سريعة</h2>
                <div className="space-y-3">
                  <Link
                    href="/triage"
                    className="block w-full py-3 px-4 bg-navy text-white rounded-xl text-center font-semibold hover:bg-navy-light transition-colors"
                  >
                    🩺 حالة جديدة
                  </Link>
                  <Link
                    href="/register-company"
                    className="block w-full py-3 px-4 bg-white border-2 border-navy text-navy rounded-xl text-center font-semibold hover:bg-gray-50 transition-colors"
                  >
                    🏢 تسجيل شركة
                  </Link>
                  <Link
                    href="/cases"
                    className="block w-full py-3 px-4 bg-white border-2 border-gray-200 text-gray-700 rounded-xl text-center font-semibold hover:bg-gray-50 transition-colors"
                  >
                    📋 عرض كل الحالات
                  </Link>
                </div>
              </Card>
            </div>

            <Card>
              <h2 className="text-lg font-bold text-navy mb-4">التوزيع حسب الخطورة</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "حرجة", count: stats?.cases_by_severity?.critical || 0, color: "bg-red-500" },
                  { label: "عالية", count: stats?.cases_by_severity?.high || 0, color: "bg-orange-500" },
                  { label: "متوسطة", count: stats?.cases_by_severity?.medium || 0, color: "bg-blue-500" },
                  { label: "منخفضة", count: stats?.cases_by_severity?.low || 0, color: "bg-gray-400" },
                ].map((item) => (
                  <div key={item.label} className="text-center">
                    <div className={`w-16 h-16 ${item.color} rounded-full mx-auto mb-2 flex items-center justify-center`}>
                      <span className="text-white text-xl font-bold">{item.count}</span>
                    </div>
                    <p className="text-sm font-semibold text-gray-700">{item.label}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
