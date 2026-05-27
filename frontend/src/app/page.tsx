"use client";

import Link from "next/link";
import { Shield, Zap, Bug, Lock, ArrowRight, Terminal, CheckCircle } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--bg-primary)" }}>

      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 pt-20 pb-16 overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full opacity-10"
            style={{ background: "radial-gradient(circle, #6366f1 0%, transparent 70%)" }} />
        </div>

        {/* Badge */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full text-sm mb-8 animate-fade-in"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          AI-Powered Security Scanner — Free to Start
        </div>

        {/* Heading */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight animate-fade-in">
          Find Vulnerabilities
          <br />
          <span className="gradient-text">Before Hackers Do</span>
        </h1>

        <p className="text-xl md:text-2xl mb-10 max-w-2xl animate-fade-in"
          style={{ color: "var(--text-secondary)" }}>
          Paste your code. AI thinks like a hacker.
          Get instant vulnerability report with attack simulation and auto-fix.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 animate-fade-in">
          <Link href="/scanner"
            className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:opacity-90 hover:scale-105"
            style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
            <Zap className="w-5 h-5" />
            Scan Your Code Free
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link href="/register"
            className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:border-indigo-500"
            style={{ border: "1px solid var(--border)", color: "var(--text-primary)", background: "var(--bg-card)" }}>
            Create Free Account
          </Link>
        </div>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 mt-16 animate-fade-in">
          {[
            { label: "OWASP Top 10", value: "Covered" },
            { label: "Scan Time", value: "< 5 sec" },
            { label: "Free Scans", value: "10/month" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold gradient-text">{stat.value}</div>
              <div className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything a hacker would look for
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: Bug,
              title: "AI Vulnerability Scan",
              desc: "Deep code analysis using AI + OWASP rules. Finds SQL injection, XSS, command injection, and 15+ more.",
              color: "#6366f1",
            },
            {
              icon: Terminal,
              title: "Attack Simulation",
              desc: "See exactly how a hacker would exploit your code. Real payloads, step-by-step attack walkthrough, CVSS score.",
              color: "#a855f7",
            },
            {
              icon: Zap,
              title: "Auto Fix",
              desc: "AI generates secure, production-ready patched code. Understand what changed and why.",
              color: "#ec4899",
            },
          ].map((feature) => (
            <div key={feature.title}
              className="p-6 rounded-xl transition-all hover:scale-105 cursor-default"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                style={{ background: `${feature.color}20`, border: `1px solid ${feature.color}40` }}>
                <feature.icon className="w-6 h-6" style={{ color: feature.color }} />
              </div>
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CLI Section - For Hackers */}
      <section className="max-w-4xl mx-auto px-4 py-16">
        <div className="p-8 rounded-2xl" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2 mb-2">
            <Terminal className="w-5 h-5" style={{ color: "var(--accent)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--accent)" }}>For Hackers & Developers</span>
          </div>
          <h2 className="text-2xl font-bold mb-6">Use via API or CLI</h2>
          <div className="p-4 rounded-xl font-mono text-sm overflow-x-auto"
            style={{ background: "var(--bg-primary)", border: "1px solid var(--border)" }}>
            <div style={{ color: "var(--text-muted)" }}># Scan via API</div>
            <div className="mt-2">
              <span style={{ color: "#a855f7" }}>curl</span>
              <span style={{ color: "var(--text-secondary)" }}> -X POST https://api.a2sentinel.com/api/scan \</span>
            </div>
            <div style={{ color: "var(--text-secondary)" }}>
              {"  "}<span style={{ color: "#6366f1" }}>-H</span> "X-API-Key: your_key" \
            </div>
            <div style={{ color: "var(--text-secondary)" }}>
              {"  "}<span style={{ color: "#6366f1" }}>-d</span> {"'{"}"code": "your_code", "language": "python"{"}'"} 
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-4">Simple Pricing</h2>
        <p className="text-center mb-12" style={{ color: "var(--text-secondary)" }}>
          Start free. Scale as you grow.
        </p>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              name: "Free",
              price: "$0",
              period: "forever",
              features: ["10 scans/month", "Vulnerability scan", "OWASP Top 10", "Basic report"],
              cta: "Start Free",
              href: "/register",
              highlight: false,
            },
            {
              name: "Pro",
              price: "$29",
              period: "per month",
              features: ["500 scans/month", "Attack simulation", "Auto fix", "API access", "Priority support"],
              cta: "Get Pro",
              href: "/register",
              highlight: true,
            },
            {
              name: "Team",
              price: "$99",
              period: "per month",
              features: ["2000 scans/month", "Everything in Pro", "Team dashboard", "GitHub integration", "Slack alerts"],
              cta: "Get Team",
              href: "/register",
              highlight: false,
            },
          ].map((plan) => (
            <div key={plan.name}
              className={`p-6 rounded-xl relative ${plan.highlight ? "gradient-border" : ""}`}
              style={{
                background: "var(--bg-card)",
                border: plan.highlight ? "none" : "1px solid var(--border)",
              }}>
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-medium text-white"
                  style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)" }}>
                  Most Popular
                </div>
              )}
              <h3 className="font-semibold text-lg mb-1">{plan.name}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-sm ml-2" style={{ color: "var(--text-muted)" }}>/{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                    <CheckCircle className="w-4 h-4 flex-shrink-0" style={{ color: "#6366f1" }} />
                    {f}
                  </li>
                ))}
              </ul>
              <Link href={plan.href}
                className="block text-center py-2.5 rounded-lg font-medium text-sm transition-all"
                style={{
                  background: plan.highlight ? "linear-gradient(135deg, #6366f1, #a855f7)" : "var(--bg-hover)",
                  color: plan.highlight ? "white" : "var(--text-primary)",
                  border: plan.highlight ? "none" : "1px solid var(--border)",
                }}>
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t mt-8 py-8 text-center text-sm"
        style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}>
        <div className="flex items-center justify-center gap-2 mb-2">
          <Shield className="w-4 h-4" style={{ color: "var(--accent)" }} />
          <span className="font-semibold" style={{ color: "var(--text-secondary)" }}>A2 Sentinel</span>
        </div>
        <p>AI-powered security scanning © 2026</p>
      </footer>
    </div>
  );
}
