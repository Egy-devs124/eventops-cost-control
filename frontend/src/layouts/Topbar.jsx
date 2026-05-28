import { Bell, Languages, LogOut, Menu, Moon, Sun, UserRound } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { useTheme } from "../context/ThemeContext";

export function Topbar({ onMenu }) {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="topbar">
      <button className="icon-button menu-button" type="button" onClick={onMenu} aria-label={t("action.menu")}>
        <Menu size={20} />
      </button>
      <div className="topbar-spacer" />
      <button
        className="toolbar-button"
        type="button"
        onClick={() => setLanguage(language === "ar" ? "en" : "ar")}
      >
        <Languages size={16} />
        {language === "ar" ? t("english") : t("arabic")}
      </button>
      <button className="toolbar-button" type="button" onClick={toggleTheme}>
        {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        {theme === "dark" ? t("light") : t("dark")}
      </button>
      <Link className="icon-button" to="/notifications" aria-label={t("notifications")}>
        <Bell size={18} />
      </Link>
      <Link className="profile-pill" to="/profile">
        <UserRound size={18} />
        <span>{user?.username}</span>
      </Link>
      <button className="icon-button" type="button" onClick={logout} aria-label={t("logout")}>
        <LogOut size={18} />
      </button>
    </header>
  );
}
