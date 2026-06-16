"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import Card from "@/components/ui/Card";

const categories = [
  { value: "finance", label: "💰 مالية" },
  { value: "marketing", label: "📈 تسويق ومبيعات" },
  { value: "operations", label: "⚙️ عمليات" },
  { value: "hr", label: "👥 موارد بشرية" },
  { value: "strategy", label: "🧭 استراتيجية" },
  { value: "legal", label: "⚖️ قانوني" },
  { value: "technical", label: "💻 تقني" },
];

const severityLabels: Record<string, string> = {
  critical: "🚨 حرجة",
  high: "🔴 عالية",
  medium: "🟡 متوسطة",
  low: "🟢 منخفضة",
};

export default function TriagePage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "https://companies-hospital-production.up.railway.app"}/api/v1/cases`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ title, description, category }),
        }
      );

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "فشل إنشاء الحالة");

      setResult(data);
      setTitle("");
      setDescription("");
      setCategory("");
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
          <div className="max-w-3xl mx-auto">
            <Card>
              <h1 className="text-2xl font-bold text-navy mb-2">🩺 استقبال حالة جديدة</h1>
              <p className="text-gray-500 mb-6">
                صف مشكلة شركتك وسيقوم النظام بفرزها وتوجيهها للتخصص المناسب
              </p>

              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    عنوان المشكلة
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    minLength={5}
                    maxLength={300}
                    placeholder="مثال: انخفاض المبيعات في الربع الأخير"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    وصف تفصيلي
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                    minLength={20}
                    placeholder="اشرح المشكلة بالتفصيل... ما الذي يحدث؟ منذ متى؟ ما تأثيره على الشركة؟"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right min-h-[120px] resize-y"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    المجال
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:outline-none focus:border-gold text-right"
                  >
                    <option value="">اختر المجال</option>
                    {categories.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-navy text-white rounded-xl font-bold text-lg hover:bg-navy-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "جاري الفحص..." : "ابدأ التشخيص"}
                </button>
              </form>

              {result && (
                <div className="mt-6 bg-gray-50 rounded-xl p-6">
                  <h3 className="font-bold text-navy mb-3">نتيجة الفرز</h3>
                  <div className="space-y-2 text-sm">
                    <p>
                      <strong>الخطورة:</strong>{" "}
                      <span className="font-semibold">{severityLabels[result.severity]}</span>
                    </p>
                    <p>
                      <strong>الكلمات المفتاحية:</strong>{" "}
                      {result.triage_result?.keywords?.map((k: string) => (
                        <span key={k} className="inline-block bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-xs ml-1">
                          {k}
                        </span>
                      ))}
                    </p>
                    <p>
                      <strong>الخبراء المقترحون:</strong>{" "}
                      {result.triage_result?.suggested_experts?.map((e: string) => (
                        <span key={e} className="inline-block bg-yellow-100 text-yellow-800 px-2 py-1 rounded-lg text-xs ml-1">
                          {e}
                        </span>
                      ))}
                    </p>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
