import { createContext, useContext, useEffect, useState } from "react"

type Theme = "dark" | "light" | "system"

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
  enableSystem?: boolean
  disableTransitionOnChange?: boolean
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme?: "dark" | "light"
  systemTheme?: "dark" | "light"
}

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "simz-ui-theme",
  enableSystem = true,
  disableTransitionOnChange = false,
  ...props
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  )
  const [systemTheme, setSystemTheme] = useState<"dark" | "light">(
    () => (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
  )

  // Function to get the resolved theme (actual theme applied)
  const getResolvedTheme = (): "dark" | "light" => {
    return theme === "system" ? systemTheme : (theme as "dark" | "light")
  }

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")

    const handleChange = () => {
      const newSystemTheme = mediaQuery.matches ? "dark" : "light"
      setSystemTheme(newSystemTheme)

      // If current theme is system, update the DOM
      if (theme === "system") {
        updateDOM(newSystemTheme)
      }
    }

    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  // Function to update the DOM with the current theme
  const updateDOM = (resolvedTheme: "dark" | "light") => {
    const root = window.document.documentElement

    if (disableTransitionOnChange) {
      root.classList.add("[&_*]:!transition-none")

      // Force a reflow
      window.getComputedStyle(root).getPropertyValue("opacity")
    }

    root.classList.remove("light", "dark")
    root.classList.add(resolvedTheme)

    if (disableTransitionOnChange) {
      // Remove the transition-none class after a short delay
      setTimeout(() => {
        root.classList.remove("[&_*]:!transition-none")
      }, 0)
    }
  }

  // Update the DOM when theme changes
  useEffect(() => {
    const resolvedTheme = getResolvedTheme()
    updateDOM(resolvedTheme)
  }, [theme, systemTheme])

  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme)
    setThemeState(newTheme)
  }

  const value = {
    theme,
    setTheme,
    resolvedTheme: getResolvedTheme(),
    systemTheme,
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider")

  return context
}
