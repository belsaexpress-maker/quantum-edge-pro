import { GoogleLogin } from "@react-oauth/google";
import { demoAdminLogin, loginWithGoogle } from "../services/authService";

export default function LoginPage({ onLogin }: { onLogin: () => void }) {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  async function handleSuccess(response: any) {
    try {
      if (!response.credential) return;
      await loginWithGoogle(response.credential);
      onLogin();
    } catch (error: any) {
      alert(error?.response?.data?.detail || "Google giriş başarısız");
    }
  }

  async function handleDemoAdmin() {
    try {
      await demoAdminLogin();
      onLogin();
    } catch (error: any) {
      alert(error?.response?.data?.detail || "Admin demo giriş başarısız");
    }
  }

  const googleReady =
    googleClientId &&
    googleClientId.includes(".apps.googleusercontent.com");

  return (
    <div className="flex min-h-[80vh] items-center justify-center text-white">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-[#070b1f] p-8 shadow-2xl">
        <h1 className="text-3xl font-bold">Quantum Edge</h1>
        <p className="mt-2 text-slate-400">
          Bot işlemleri ve emirler için giriş yap.
        </p>

        <div className="mt-8 flex justify-center">
          {googleReady ? (
            <GoogleLogin
              onSuccess={handleSuccess}
              onError={() => alert("Google giriş başarısız")}
            />
          ) : (
            <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4 text-sm text-yellow-200">
              Google Client ID henüz hazır değil. Şimdilik Admin Demo Giriş kullan.
            </div>
          )}
        </div>

        <button
          onClick={handleDemoAdmin}
          className="mt-6 w-full rounded-xl bg-cyan-500 px-4 py-3 font-bold text-black hover:bg-cyan-400"
        >
          Admin Demo Giriş
        </button>
      </div>
    </div>
  );
}