import { useEffect, useState } from "react";
import { Gift, RefreshCcw, Shield } from "lucide-react";

import { getMyMembership, getUsers, grantRole } from "../services/membershipService";
import { getToken, getUser } from "../services/authService";

export default function MembershipPage() {
  const [me, setMe] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("gift");
  const [message, setMessage] = useState("");

  const user = getUser();
  const loggedIn = Boolean(getToken());
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    load();
  }, []);

  async function load() {
    if (!loggedIn) return;

    try {
      const data = await getMyMembership();
      setMe(data);

      if (isAdmin) {
        const userList = await getUsers();
        setUsers(userList);
      }
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Üyelik bilgisi alınamadı");
    }
  }

  async function handleGrant() {
    setMessage("");

    try {
      const result = await grantRole({ email, role });
      setMessage(result.message);
      setEmail("");
      await load();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Yetki verilemedi");
    }
  }

  if (!loggedIn) {
    return (
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-10 text-center">
        <h2 className="text-2xl font-bold">Üyelik</h2>
        <p className="mt-2 text-slate-400">
          Üyelik bilgilerini görmek için giriş yapmalısın.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">Üyelik & Erişim</h2>
        <p className="mt-1 text-slate-400">
          Bot erişimi admin, ücretli ve hediye kullanıcılar için açıktır.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        <Card label="Email" value={user?.email || "-"} />
        <Card label="Rol" value={me?.role || user?.role || "-"} />
        <Card label="Plan" value={me?.plan_name || "-"} />
        <Card label="Bot Erişimi" value={me?.can_use_bots ? "Açık" : "Kapalı"} />
      </section>

      {isAdmin && (
        <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <Gift size={20} />
            Kullanıcıya Yetki Ver
          </h3>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_180px_160px]">
            <input
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3"
              placeholder="kullanici@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <select
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="gift">gift</option>
              <option value="paid">paid</option>
              <option value="free">free</option>
              <option value="admin">admin</option>
            </select>

            <button
              onClick={handleGrant}
              className="rounded-xl bg-cyan-500 px-4 py-3 font-bold text-black"
            >
              Yetki Ver
            </button>
          </div>

          {message && (
            <p className="mt-4 rounded-xl border border-white/10 bg-white/5 p-3 text-sm">
              {message}
            </p>
          )}
        </section>
      )}

      {isAdmin && (
        <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-xl font-bold">
              <Shield size={20} />
              Kullanıcılar
            </h3>

            <button
              onClick={load}
              className="flex items-center gap-2 rounded-xl bg-white/5 px-4 py-2 text-sm"
            >
              <RefreshCcw size={16} />
              Yenile
            </button>
          </div>

          <div className="max-h-[520px] overflow-auto">
            <table className="w-full text-sm">
              <thead className="text-slate-400">
                <tr>
                  <th className="p-3 text-left">Email</th>
                  <th className="p-3 text-left">Ad</th>
                  <th className="p-3 text-left">Rol</th>
                  <th className="p-3 text-left">Aktif</th>
                </tr>
              </thead>

              <tbody>
                {users.map((item) => (
                  <tr key={item.id} className="border-t border-white/10">
                    <td className="p-3">{item.email}</td>
                    <td className="p-3">{item.full_name || "-"}</td>
                    <td className="p-3">{item.role}</td>
                    <td className="p-3">{item.is_active ? "Evet" : "Hayır"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-xl font-bold">{value}</p>
    </div>
  );
}