"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Activity,
    Bell,
    Cable,
    ChevronRight,
    DoorClosed,
    DoorOpen,
    Lock,
    LogOut,
    RefreshCw,
    Shield,
    User,
    Wifi,
    WifiOff,
} from "lucide-react";

/**
 * Owner Dashboard - Next.js / React version
 *
 * Mục tiêu:
 * - Giữ tương thích với hệ thống hiện tại, KHÔNG phá backend cũ.
 * - Vẫn dùng các API cũ:
 *   - /api/system/info
 *   - /api/locks
 * - Vẫn dùng logic auth và websocket hiện có nếu bạn đã có sẵn trên window.
 * - Bổ sung UX tốt hơn: active lock context, system summary, realtime panel rõ ràng.
 *
 * Cách dùng:
 * 1) Thả file này vào app/owner/dashboard/page.tsx hoặc pages/owner/dashboard.tsx
 * 2) Sửa BASE_URL nếu frontend Next.js chạy khác domain backend.
 * 3) Nếu đã có auth util riêng, thay phần localStorage token theo dự án của bạn.
 */

type Me = {
    id?: number;
    full_name?: string;
    email?: string;
};

type LockItem = {
    id: number;
    name: string;
    location?: string | null;
    status?: string | null;
    device_status?: string | null;
    last_seen_at?: string | null;
    member_count?: number | null;
};

type SystemInfo = Record<string, unknown>;

type RealtimeEvent = {
    id: string;
    ts: string;
    level: "info" | "success" | "warning" | "error";
    title: string;
    description?: string;
};

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const navItems = [
    { key: "dashboard", label: "Dashboard", href: "/owner/dashboard", icon: Activity },
    { key: "locks", label: "Locks", href: "/owner/locks", icon: Lock },
    { key: "users", label: "Users", href: "/owner/users", icon: User },
    { key: "enroll", label: "Enroll", href: "/owner/enroll", icon: Shield },
    { key: "logs", label: "Logs", href: "/owner/logs", icon: Bell },
    { key: "settings", label: "Settings", href: "/owner/settings", icon: Cable },
];

function getAuthToken() {
    if (typeof window === "undefined") return "";
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        sessionStorage.getItem("access_token") ||
        ""
    );
}

async function apiFetch<T>(path: string): Promise<T> {
    const token = getAuthToken();
    const res = await fetch(`${BASE_URL}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        cache: "no-store",
    });

    if (res.status === 401) {
        if (typeof window !== "undefined") {
            window.location.href = "http://localhost:8000/owner/login.html";
        }
        throw new Error("Unauthorized");
    }

    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
    }

    return res.json();
}

function formatDateTime(value?: string | null) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat("vi-VN", {
        dateStyle: "short",
        timeStyle: "short",
    }).format(date);
}

function statusTone(status?: string | null) {
    const s = (status || "").toLowerCase();
    if (["online", "connected", "ready", "active"].includes(s)) {
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
    }
    if (["offline", "disconnected", "down"].includes(s)) {
        return "bg-rose-50 text-rose-700 border-rose-200";
    }
    if (["warning", "degraded"].includes(s)) {
        return "bg-amber-50 text-amber-700 border-amber-200";
    }
    return "bg-slate-50 text-slate-700 border-slate-200";
}

function eventTone(level: RealtimeEvent["level"]) {
    switch (level) {
        case "success":
            return "border-emerald-200 bg-emerald-50";
        case "warning":
            return "border-amber-200 bg-amber-50";
        case "error":
            return "border-rose-200 bg-rose-50";
        default:
            return "border-slate-200 bg-slate-50";
    }
}

export default function OwnerDashboardPage() {
    const [me, setMe] = useState<Me | null>(null);
    const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
    const [locks, setLocks] = useState<LockItem[]>([]);
    const [activeLockId, setActiveLockId] = useState<number | null>(null);
    const [events, setEvents] = useState<RealtimeEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [joining, setJoining] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [wsState, setWsState] = useState<"idle" | "connected" | "disconnected">("idle");
    const [error, setError] = useState<string>("");

    const activeLock = useMemo(
        () => locks.find((item) => item.id === activeLockId) || null,
        [locks, activeLockId]
    );

    async function loadDashboard() {
        setError("");
        const [meData, infoData, lockData] = await Promise.all([
            apiFetch<Me>("/api/auth/me").catch(() => ({ full_name: "Owner", email: "owner@example.com" })),
            apiFetch<SystemInfo>("/api/system/info"),
            apiFetch<LockItem[]>("/api/locks"),
        ]);

        setMe(meData);
        setSystemInfo(infoData);
        setLocks(lockData || []);

        if ((lockData || []).length > 0) {
            setActiveLockId((prev) => prev ?? lockData[0].id);
        }
    }

    useEffect(() => {
        let mounted = true;
        (async () => {
            try {
                setLoading(true);
                await loadDashboard();
            } catch (err) {
                if (mounted) {
                    setError(err instanceof Error ? err.message : "Không tải được dashboard.");
                }
            } finally {
                if (mounted) setLoading(false);
            }
        })();
        return () => {
            mounted = false;
        };
    }, []);

    async function handleRefresh() {
        try {
            setRefreshing(true);
            await loadDashboard();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Làm mới thất bại.");
        } finally {
            setRefreshing(false);
        }
    }

    function pushEvent(event: Omit<RealtimeEvent, "id">) {
        setEvents((prev) => [
            {
                ...event,
                id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
            },
            ...prev,
        ].slice(0, 50));
    }

    function connectWs(lockId: number) {
        setJoining(true);
        setError("");

        try {
            const existing = (window as any).__ownerWs as WebSocket | undefined;
            if (existing && existing.readyState === WebSocket.OPEN) {
                existing.close();
            }

            const token = getAuthToken();
            const protocol = BASE_URL.startsWith("https") ? "wss" : "ws";
            const host = BASE_URL.replace(/^https?:\/\//, "");
            const wsUrl = `${protocol}://${host}/ws?lock_id=${lockId}${token ? `&token=${encodeURIComponent(token)}` : ""}`;

            const ws = new WebSocket(wsUrl);
            (window as any).__ownerWs = ws;

            ws.onopen = () => {
                setWsState("connected");
                setJoining(false);
                pushEvent({
                    ts: new Date().toISOString(),
                    level: "success",
                    title: `Đã tham gia realtime của lock #${lockId}`,
                    description: "Kết nối WebSocket thành công.",
                });
            };

            ws.onmessage = (message) => {
                try {
                    const data = JSON.parse(message.data);
                    pushEvent({
                        ts: new Date().toISOString(),
                        level: data.level || "info",
                        title: data.title || data.event || "Realtime event",
                        description: data.description || JSON.stringify(data),
                    });
                } catch {
                    pushEvent({
                        ts: new Date().toISOString(),
                        level: "info",
                        title: "Realtime message",
                        description: String(message.data),
                    });
                }
            };

            ws.onerror = () => {
                setWsState("disconnected");
                setJoining(false);
                setError("Kết nối realtime thất bại. Kiểm tra endpoint /ws và token.");
            };

            ws.onclose = () => {
                setWsState("disconnected");
                setJoining(false);
            };
        } catch (err) {
            setJoining(false);
            setWsState("disconnected");
            setError(err instanceof Error ? err.message : "Không thể kết nối realtime.");
        }
    }

    function logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token");
        sessionStorage.removeItem("access_token");
        window.location.href = "/owner/login";
    }

    const summary = useMemo(() => {
        const total = locks.length;
        const online = locks.filter((item) => {
            const s = (item.device_status || item.status || "").toLowerCase();
            return ["online", "connected", "active", "ready"].includes(s);
        }).length;
        const offline = Math.max(total - online, 0);
        const totalMembers = locks.reduce((acc, item) => acc + Number(item.member_count || 0), 0);
        return { total, online, offline, totalMembers };
    }, [locks]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
                <div className="rounded-3xl border border-slate-200 bg-white px-6 py-5 shadow-sm text-slate-700">
                    Đang tải dashboard...
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900">
            <div className="flex min-h-screen">
                <aside className="hidden lg:flex w-72 flex-col border-r border-slate-200 bg-white px-5 py-6">
                    <div className="mb-8">
                        <div className="text-lg font-semibold tracking-tight">Smart Lock Face Pro</div>
                        <div className="text-sm text-slate-500">Owner Console</div>
                    </div>

                    <nav className="space-y-1.5">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const active = item.key === "dashboard";
                            return (
                                <a
                                    key={item.key}
                                    href={item.href}
                                    className={`flex items-center justify-between rounded-2xl px-3 py-3 text-sm transition ${active
                                            ? "bg-slate-900 text-white shadow-sm"
                                            : "text-slate-700 hover:bg-slate-50"
                                        }`}
                                >
                                    <span className="flex items-center gap-3">
                                        <Icon className="h-4 w-4" />
                                        {item.label}
                                    </span>
                                    <ChevronRight className="h-4 w-4 opacity-70" />
                                </a>
                            );
                        })}
                    </nav>

                    <div className="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-4">
                        <div className="text-sm font-semibold">Phiên làm việc</div>
                        <div className="mt-2 text-sm text-slate-600">
                            {me?.full_name || "Owner"}
                        </div>
                        <div className="text-xs text-slate-500 break-all">{me?.email || "—"}</div>
                    </div>

                    <button
                        onClick={logout}
                        className="mt-auto inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                    >
                        <LogOut className="h-4 w-4" />
                        Logout
                    </button>
                </aside>

                <main className="flex-1 p-4 md:p-6 lg:p-8">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                        <div>
                            <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Dashboard</h1>
                            <p className="mt-1 text-sm text-slate-500">
                                Theo dõi lock, device và realtime event trong một màn hình rõ ràng hơn.
                            </p>
                        </div>

                        <div className="flex flex-wrap items-center gap-3">
                            <span
                                className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${wsState === "connected"
                                        ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                                        : wsState === "disconnected"
                                            ? "border-rose-200 bg-rose-50 text-rose-700"
                                            : "border-slate-200 bg-white text-slate-700"
                                    }`}
                            >
                                {wsState === "connected" ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
                                {wsState === "connected"
                                    ? "Realtime connected"
                                    : wsState === "disconnected"
                                        ? "Realtime disconnected"
                                        : "Realtime idle"}
                            </span>

                            <button
                                onClick={handleRefresh}
                                disabled={refreshing}
                                className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                            >
                                <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                                Refresh
                            </button>
                        </div>
                    </div>

                    {error ? (
                        <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                            {error}
                        </div>
                    ) : null}

                    <section className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                        <SummaryCard title="Tổng số lock" value={summary.total} icon={<Lock className="h-5 w-5" />} />
                        <SummaryCard title="Lock online" value={summary.online} icon={<Wifi className="h-5 w-5" />} />
                        <SummaryCard title="Lock offline" value={summary.offline} icon={<WifiOff className="h-5 w-5" />} />
                        <SummaryCard title="Member đã gán" value={summary.totalMembers} icon={<User className="h-5 w-5" />} />
                    </section>

                    <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-12">
                        <div className="xl:col-span-7 space-y-6">
                            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                                    <div>
                                        <div className="text-lg font-semibold">Lock context</div>
                                        <div className="text-sm text-slate-500">
                                            Chọn lock để theo dõi realtime. Việc chọn ở đây không làm hỏng các chức năng khác.
                                        </div>
                                    </div>

                                    <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row">
                                        <select
                                            value={activeLockId ?? ""}
                                            onChange={(e) => setActiveLockId(Number(e.target.value))}
                                            className="min-w-[240px] rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none ring-0"
                                        >
                                            {locks.map((item) => (
                                                <option key={item.id} value={item.id}>
                                                    {item.name} (#{item.id})
                                                </option>
                                            ))}
                                        </select>

                                        <button
                                            onClick={() => activeLockId && connectWs(activeLockId)}
                                            disabled={!activeLockId || joining}
                                            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-60"
                                        >
                                            <Activity className="h-4 w-4" />
                                            {joining ? "Đang kết nối..." : "Join realtime"}
                                        </button>
                                    </div>
                                </div>

                                {activeLock ? (
                                    <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
                                        <InfoBox label="Tên lock" value={activeLock.name} />
                                        <InfoBox label="Vị trí" value={activeLock.location || "Chưa có"} />
                                        <InfoBox
                                            label="Trạng thái"
                                            value={activeLock.status || "Unknown"}
                                            badgeClass={statusTone(activeLock.status)}
                                            asBadge
                                        />
                                        <InfoBox
                                            label="Device"
                                            value={activeLock.device_status || "Unknown"}
                                            badgeClass={statusTone(activeLock.device_status)}
                                            asBadge
                                        />
                                        <InfoBox label="Lần cuối thấy device" value={formatDateTime(activeLock.last_seen_at)} />
                                        <InfoBox label="Số member" value={String(activeLock.member_count ?? 0)} />
                                    </div>
                                ) : (
                                    <div className="mt-4 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
                                        Chưa có lock nào để hiển thị.
                                    </div>
                                )}
                            </div>

                            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                                <div className="mb-4 flex items-center justify-between">
                                    <div>
                                        <div className="text-lg font-semibold">Realtime event panel</div>
                                        <div className="text-sm text-slate-500">Sự kiện mới nhất của lock đang chọn.</div>
                                    </div>
                                </div>

                                <div className="max-h-[420px] space-y-3 overflow-auto pr-1">
                                    {events.length === 0 ? (
                                        <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
                                            Chưa có sự kiện realtime. Hãy chọn lock và bấm Join realtime.
                                        </div>
                                    ) : (
                                        events.map((event) => (
                                            <div
                                                key={event.id}
                                                className={`rounded-2xl border px-4 py-3 ${eventTone(event.level)}`}
                                            >
                                                <div className="flex items-start justify-between gap-4">
                                                    <div>
                                                        <div className="font-medium">{event.title}</div>
                                                        {event.description ? (
                                                            <div className="mt-1 text-sm text-slate-600 break-words">
                                                                {event.description}
                                                            </div>
                                                        ) : null}
                                                    </div>
                                                    <div className="shrink-0 text-xs text-slate-500">
                                                        {formatDateTime(event.ts)}
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="xl:col-span-5 space-y-6">
                            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                                <div className="text-lg font-semibold">System info</div>
                                <div className="mt-1 text-sm text-slate-500">
                                    Dành cho giám sát và debug, không phải nơi bắt buộc để hệ thống hoạt động.
                                </div>
                                <pre className="mt-4 max-h-[360px] overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                                    {JSON.stringify(systemInfo, null, 2)}
                                </pre>
                            </div>

                            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                                <div className="text-lg font-semibold">Danh sách lock</div>
                                <div className="mt-1 text-sm text-slate-500">
                                    Nhìn nhanh trạng thái toàn bộ lock thay vì chỉ một dropdown trống rỗng.
                                </div>

                                <div className="mt-4 space-y-3">
                                    {locks.length === 0 ? (
                                        <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
                                            Chưa có lock nào.
                                        </div>
                                    ) : (
                                        locks.map((item) => {
                                            const isActive = item.id === activeLockId;
                                            const online = [item.device_status, item.status]
                                                .some((s) => ["online", "connected", "active", "ready"].includes(String(s || "").toLowerCase()));

                                            return (
                                                <button
                                                    key={item.id}
                                                    onClick={() => setActiveLockId(item.id)}
                                                    className={`w-full rounded-2xl border p-4 text-left transition ${isActive
                                                            ? "border-slate-900 bg-slate-900 text-white"
                                                            : "border-slate-200 bg-white hover:bg-slate-50"
                                                        }`}
                                                >
                                                    <div className="flex items-start justify-between gap-3">
                                                        <div>
                                                            <div className="font-semibold">{item.name}</div>
                                                            <div className={`mt-1 text-sm ${isActive ? "text-slate-300" : "text-slate-500"}`}>
                                                                {item.location || "Chưa có vị trí"}
                                                            </div>
                                                        </div>

                                                        <div className={`inline-flex items-center gap-2 rounded-full px-2.5 py-1 text-xs font-medium ${isActive
                                                                ? "bg-white/10 text-white"
                                                                : online
                                                                    ? "bg-emerald-50 text-emerald-700"
                                                                    : "bg-rose-50 text-rose-700"
                                                            }`}>
                                                            {online ? <DoorOpen className="h-3.5 w-3.5" /> : <DoorClosed className="h-3.5 w-3.5" />}
                                                            {online ? "Online" : "Offline"}
                                                        </div>
                                                    </div>

                                                    <div className={`mt-3 grid grid-cols-2 gap-3 text-xs ${isActive ? "text-slate-200" : "text-slate-500"}`}>
                                                        <div>Members: {item.member_count ?? 0}</div>
                                                        <div>Last seen: {formatDateTime(item.last_seen_at)}</div>
                                                    </div>
                                                </button>
                                            );
                                        })
                                    )}
                                </div>
                            </div>
                        </div>
                    </section>
                </main>
            </div>
        </div>
    );
}

function SummaryCard({
    title,
    value,
    icon,
}: {
    title: string;
    value: string | number;
    icon: React.ReactNode;
}) {
    return (
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
                <div className="text-sm text-slate-500">{title}</div>
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-700">{icon}</div>
            </div>
            <div className="mt-4 text-3xl font-semibold tracking-tight">{value}</div>
        </div>
    );
}

function InfoBox({
    label,
    value,
    asBadge = false,
    badgeClass = "",
}: {
    label: string;
    value: string;
    asBadge?: boolean;
    badgeClass?: string;
}) {
    return (
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
            {asBadge ? (
                <div className={`mt-2 inline-flex rounded-full border px-2.5 py-1 text-sm font-medium ${badgeClass}`}>
                    {value}
                </div>
            ) : (
                <div className="mt-2 text-sm font-medium text-slate-900">{value}</div>
            )}
        </div>
    );
}
