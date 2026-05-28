import { useState } from "react";
import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="main-shell">
        <Topbar onMenu={() => setSidebarOpen((open) => !open)} />
        <main className="page">
          <Outlet />
        </main>
      </div>
      {sidebarOpen ? <button className="scrim" onClick={() => setSidebarOpen(false)} aria-label="Close menu" /> : null}
    </div>
  );
}
