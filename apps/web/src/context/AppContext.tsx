import { createContext, useContext, useMemo, useState } from 'react'

type SubjectCode = 'SOFTDEV' | 'DATA'
type Track = 'foundation' | 'scored'

interface AppContextValue {
  subjectCode: SubjectCode
  setSubjectCode: (code: SubjectCode) => void
  unit: 1 | 2 | 3 | 4
  setUnit: (unit: 1 | 2 | 3 | 4) => void
  track: Track
}

const AppContext = createContext<AppContextValue | null>(null)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [subjectCode, setSubjectCode] = useState<SubjectCode>('SOFTDEV')
  const [unit, setUnit] = useState<1 | 2 | 3 | 4>(1)
  const track: Track = unit <= 2 ? 'foundation' : 'scored'

  const value = useMemo(
    () => ({
      subjectCode,
      setSubjectCode,
      unit,
      setUnit,
      track,
    }),
    [subjectCode, unit, track],
  )

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider')
  }
  return context
}
