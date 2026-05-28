import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { navItems } from "./navigation";

export function Sidebar({ open, onClose }) {
  const { hasRole } = useAuth();
  const { t } = useLanguage();

  return (
    <aside className={`sidebar ${open ? "open" : ""}`}>
      <div className="brand">
        <span className="brand-mark">EO</span>
        <div>
          <strong>{t("appName")}</strong>
          <small>ERP</small>
        </div>
      </div>
      <nav>
        {navItems
          .filter((item) => hasRole(item.roles))
          .map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} onClick={onClose}>
                <Icon size={18} />
                <span>{t(item.labelKey)}</span>
              </NavLink>
            );
          })}
      </nav>
    </aside>
  );
}
