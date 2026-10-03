import { Link, useNavigate } from "react-router-dom";
import { clearSession, currentName, currentRole } from "../lib/api";

export default function Layout({ title, children, tabs = [] }) {
  const navigate = useNavigate();
  const name = currentName();
  const role = currentRole();

  const logout = () => {
    clearSession();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-full flex flex-col">
      <header className="bg-navy-700 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to={`/${role}/dashboard`} className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gold-500 flex items-center justify-center
                            text-navy-900 font-bold">SV</div>
            <div>
              <div className="font-semibold leading-tight">MDM Allotment</div>
              <div className="text-xs text-navy-100">St. Vincent Pallotti College</div>
            </div>
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <span className="hidden sm:inline text-navy-100">{name}</span>
            <button onClick={logout} className="btn-ghost !border-white !text-white hover:!bg-navy-500">
              Logout
            </button>
          </div>
        </div>
      </header>

      {tabs.length > 0 && (
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 flex gap-1 overflow-x-auto">
            {tabs.map((t) => (
              <Link
                key={t.to}
                to={t.to}
                className="px-4 py-3 text-sm font-medium text-gray-600 hover:text-navy-700
                           border-b-2 border-transparent hover:border-gold-500 whitespace-nowrap"
              >
                {t.label}
              </Link>
            ))}
          </div>
        </nav>
      )}

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {title && <h1 className="text-2xl font-semibold text-navy-700 mb-5">{title}</h1>}
        {children}
      </main>

      <footer className="text-center text-xs text-gray-500 py-4">
        © {new Date().getFullYear()} St. Vincent Pallotti College of Engineering & Technology
      </footer>
    </div>
  );
}