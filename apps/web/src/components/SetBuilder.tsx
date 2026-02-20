import { useState } from 'react'

interface SetBuilderPayload {
  number_of_questions: number
  time_target_minutes: number
  mixed_topics: boolean
  unit?: number
  topic_ids: number[]
  difficulty?: number
  question_types: string[]
  exam_styles: string[]
  subject_code?: string
}

const QUESTION_TYPES = ['mcq', 'short', 'explain_justify', 'code', 'data', 'skill_drill']
const EXAM_STYLES = ['case_study', 'short', 'extended', 'interpretation', 'tracing']

export function SetBuilder({
  subjectCode,
  unit,
  onBuild,
}: {
  subjectCode: string
  unit: number
  onBuild: (payload: SetBuilderPayload) => void
}) {
  const [numberOfQuestions, setNumberOfQuestions] = useState(8)
  const [timeTargetMinutes, setTimeTargetMinutes] = useState(30)
  const [mixedTopics, setMixedTopics] = useState(true)
  const [difficulty, setDifficulty] = useState<number | undefined>(undefined)
  const [questionTypes, setQuestionTypes] = useState<string[]>([])
  const [examStyles, setExamStyles] = useState<string[]>([])

  function toggleValue<T extends string>(list: T[], value: T, setter: (items: T[]) => void) {
    if (list.includes(value)) {
      setter(list.filter((item) => item !== value))
    } else {
      setter([...list, value])
    }
  }

  return (
    <section className="rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-base font-semibold">Set Builder</h2>
      <div className="grid gap-3 md:grid-cols-3">
        <label className="text-sm">
          Number of questions
          <input
            type="number"
            min={1}
            max={50}
            value={numberOfQuestions}
            onChange={(e) => setNumberOfQuestions(Number(e.target.value))}
            className="mt-1 w-full rounded border px-2 py-1"
          />
        </label>
        <label className="text-sm">
          Time target (min)
          <input
            type="number"
            min={5}
            max={180}
            value={timeTargetMinutes}
            onChange={(e) => setTimeTargetMinutes(Number(e.target.value))}
            className="mt-1 w-full rounded border px-2 py-1"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={mixedTopics} onChange={(e) => setMixedTopics(e.target.checked)} />
          Mixed topics
        </label>
      </div>

      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <label className="text-sm">
          Difficulty (optional)
          <select
            value={difficulty ?? ''}
            onChange={(e) => setDifficulty(e.target.value ? Number(e.target.value) : undefined)}
            className="mt-1 w-full rounded border px-2 py-1"
          >
            <option value="">Any</option>
            {[1, 2, 3, 4, 5].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-3">
        <p className="text-sm font-medium">Question types</p>
        <div className="mt-1 flex flex-wrap gap-2">
          {QUESTION_TYPES.map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => toggleValue(questionTypes, type, setQuestionTypes)}
              className={`rounded px-2 py-1 text-xs ${
                questionTypes.includes(type) ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-700'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3">
        <p className="text-sm font-medium">Exam style tags</p>
        <div className="mt-1 flex flex-wrap gap-2">
          {EXAM_STYLES.map((style) => (
            <button
              key={style}
              type="button"
              onClick={() => toggleValue(examStyles, style, setExamStyles)}
              className={`rounded px-2 py-1 text-xs ${
                examStyles.includes(style) ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-700'
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      <button
        type="button"
        className="mt-4 rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
        onClick={() =>
          onBuild({
            number_of_questions: numberOfQuestions,
            time_target_minutes: timeTargetMinutes,
            mixed_topics: mixedTopics,
            unit,
            topic_ids: [],
            difficulty,
            question_types: questionTypes,
            exam_styles: examStyles,
            subject_code: subjectCode,
          })
        }
      >
        Generate set
      </button>
    </section>
  )
}
