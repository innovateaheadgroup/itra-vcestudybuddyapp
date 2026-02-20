export const SUBJECTS = [
  { code: 'SOFTDEV', name: 'Software Development' },
  { code: 'DATA', name: 'Data Analytics' },
] as const

export const TRACKS = {
  foundation: 'Foundation Track (Units 1-2)',
  scored: 'Scored Track (Units 3-4)',
} as const

export const COMMAND_TERMS = ['describe', 'explain', 'analyse', 'justify', 'evaluate'] as const

export const QUESTION_TYPES = ['mcq', 'short', 'explain_justify', 'code', 'data', 'skill_drill'] as const

export const EXAM_STYLES = ['case_study', 'short', 'extended', 'interpretation', 'tracing'] as const
