"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, Mail, Lock, User, Building, Eye, EyeOff } from "lucide-react";
import toast from "react-hot-toast";
import { authAPI } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [form, setForm] = useState({ email: "", password: "", full_name: "", company: "" });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      const res = await authAPI.register(form);
      setAuth(res.data.user, res.data.access_token);
      toast.success("Account created! Welcome to A2 Sentinel 🛡️");
      router.push("/scanner");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8"
      style={{ background: "var(--bg-primary)" }}>
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
            style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)" }}>
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Create your account</h1>
          <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
            Free forever • 10 scans/month • No credit card
          </p>
        </div>

        {/* Form */}
        <div className="p-8 rounded-2xl" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
                <input type="text" value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  placeholder="Abbas Khan"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none transition-all focus:border-indigo-500"
                  style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
                />
              </div>
            </div>

            {/* Company */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Company <span style={{ color: "var(--text-muted)" }}>(optional)</span>
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
                <input type="text" value={form.company}
                  onChange={(e) => setForm({ ...form, company: e.target.value })}
                  placeholder="Your company"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none"
                  style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
                <input type="email" required value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="you@company.com"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none focus:border-indigo-500"
                  style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
                <input type={showPass ? "text" : "password"} required value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder="Min 8 characters"
                  className="w-full pl-10 pr-10 py-3 rounded-xl text-sm outline-none focus:border-indigo-500"
                  style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }}>
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-xl font-semibold text-sm transition-all hover:opacity-90 disabled:opacity-50 mt-2"
              style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
              {loading ? "Creating account..." : "Create Free Account"}
            </button>
          </form>

          <p className="text-center mt-6 text-sm" style={{ color: "var(--text-muted)" }}>
            Already have an account?{" "}
            <Link href="/login" className="font-medium hover:text-indigo-400" style={{ color: "var(--accent)" }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
