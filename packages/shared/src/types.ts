export type IntegrityMode = 'foundation' | 'scored'

export interface FeedbackCriterion {
  name: string
  score: number
  max: number
  notes: string[]
}

export interface FeedbackObject {
  score: number
  max_score: number
  criteria: FeedbackCriterion[]
  missing: string[]
  next_steps: string[]
  drills: Array<{ topic_id: number; count: number }>
  mistake_tags: string[]
  integrity_mode: IntegrityMode
}
