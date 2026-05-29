import { useEffect, useState, useCallback } from "react";
import AppLayoutMFE from "./components/AppLayoutMFE/AppLayoutMFE";
import { ChatSessionProvider } from "./components/Agent/ChatContext";
import { ThemeProvider } from "./components/ThemeContext";
import AppRefreshManager from "./AppRefreshManager";
import { SidebarProvider, SidebarInset } from "./components/ui/sidebar";
import { AppSidebar } from "./components/Sidebar";
import ErrorBoundary from "./components/ErrorBoundary";
import { Toaster } from "@/components/ui/sonner";

// MOCK USER FOR LOCAL DEVELOPMENT
const MOCK_USER = {
  userId: "dev-user-123",
  username: "khariri",
  attributes: {
    email: "khariri@tokaicom-mitra.co.id",
    given_name: "Khariri",
    family_name: "TMI",
    sub: "dev-user-123"
  }
};

const App = () => {
  // Force authenticated state for development
  const [authUser] = useState(MOCK_USER);

  const [colorMode, setColorMode] = useState(() => {
    const savedMode = localStorage.getItem("colorMode");
    return savedMode || "system";
  });

  const [effectiveTheme, setEffectiveTheme] = useState(() => {
    const getSystemTheme = () => {
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    };
    const getEffectiveTheme = (mode) => {
      if (mode === "system") {
        return getSystemTheme();
      }
      return mode;
    };
    return getEffectiveTheme(colorMode);
  });

  const getSystemTheme = () => {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const getEffectiveTheme = (mode) => {
    if (mode === "system") {
      return getSystemTheme();
    }
    return mode;
  };

  const setThemeMode = (mode) => {
    const validModes = ["SYSTEM", "LIGHT", "DARK"];
    const normalizedMode = mode.toUpperCase();

    if (validModes.includes(normalizedMode)) {
      setColorMode(normalizedMode.toLowerCase());
    } else {
      console.warn(`Invalid theme mode: ${mode}. Valid options are: SYSTEM, LIGHT, DARK`);
    }
  };

  useEffect(() => {
    const newEffectiveTheme = getEffectiveTheme(colorMode);
    setEffectiveTheme(newEffectiveTheme);
    localStorage.setItem("colorMode", colorMode);

    if (newEffectiveTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleSystemThemeChange = () => {
      if (colorMode === "system") {
        const updatedEffectiveTheme = getEffectiveTheme(colorMode);
        setEffectiveTheme(updatedEffectiveTheme);

        if (updatedEffectiveTheme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      }
    };

    if (colorMode === "system") {
      mediaQuery.addEventListener("change", handleSystemThemeChange);
    }

    return () => {
      mediaQuery.removeEventListener("change", handleSystemThemeChange);
    };
  }, [colorMode]);

  const handleNewChat = useCallback(() => {
    // Navigate to root will be handled by the sidebar
  }, []);

  const handleHistoryUpdate = useCallback((history) => {
    // Can be used for any app-level state updates if needed
  }, []);

  const checkAuthState = () => {
    // Mock function for development
    console.log("Auth check bypassed in development mode");
  };

  return (
    <div>
      <ErrorBoundary
        fallback={({ reset }) => (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100vh",
              gap: "16px",
            }}
          >
            <p style={{ fontSize: "16px", color: "#666" }}>Something went wrong.</p>
            <button
              onClick={() => {
                reset();
                window.location.reload();
              }}
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                background: "#f5f5f5",
                cursor: "pointer",
                fontSize: "14px",
              }}
            >
              Reload
            </button>
          </div>
        )}
      >
        <ThemeProvider
          colorMode={colorMode}
          effectiveTheme={effectiveTheme}
          setThemeMode={setThemeMode}
        >
          <AppRefreshManager>
            <ChatSessionProvider>
              <SidebarProvider defaultOpen={false}>
                <AppSidebar
                  user={authUser}
                  colorMode={colorMode}
                  effectiveTheme={effectiveTheme}
                  setThemeMode={setThemeMode}
                  setAuthUser={checkAuthState}
                  onNewChat={handleNewChat}
                  onHistoryUpdate={handleHistoryUpdate}
                />
                <SidebarInset>
                  <AppLayoutMFE
                    user={authUser}
                    colorMode={colorMode}
                    setThemeMode={setThemeMode}
                  />
                </SidebarInset>
              </SidebarProvider>
            </ChatSessionProvider>
          </AppRefreshManager>
          <Toaster />
        </ThemeProvider>
      </ErrorBoundary>
    </div>
  );
};

export default App;
