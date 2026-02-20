import { useState } from 'react'

import { CommandTermBadge } from '../components/CommandTermBadge'
import { FeedbackPanel } from '../components/FeedbackPanel'
import { SetBuilder, type SetBuilderPayload } from '../components/SetBuilder'
import { useAppContext } from '../context/AppContext'
import { api, type MarkResponse, type Question } from '../lib/api'

interface PracticeSetResponse {
  questions: Question[]
  estimated_minutes: number
}

export function PracticePage() {
  const { subjectCode, unit, track } = useAppContext()
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answerText, setAnswerText] = useState('')
  const [codeSnapshot, setCodeSnapshot] = useState('')
  const [feedback, setFeedback] = useState<MarkResponse | null>(null)
  const [isMarking, setIsMarking] = useState(false)

  const currentQuestion = questions[currentIndex]

  async function buildSet(payload: SetBuilderPayload) {
    const data = await api.post<PracticeSetResponse>('/api/practice/set-builder', payload)
    setQuestions(data.questions)
    setCurrentIndex(0)
    setAnswerText('')
    setCodeSnapshot(data.questions[0]?.starter_code ?? '')
    setFeedback(null)
  }

  async function submitAttempt() {
    if (!currentQuestion) return
    setIsMarking(true)
    try {
      const result = await api.post<MarkResponse>('/api/mark', {
        question_id: currentQuestion.id,
        answer_text: answerText,
        code_snapshot: codeSnapshot,
        integrity_mode: track,
        track,
        unit,
        is_sat_assessment: false,
      })
      setFeedback(result)
    } finally {
      setIsMarking(false)
    }
  }

  function nextQuestion() {
    if (currentIndex + 1 < questions.length) {
      const next = questions[currentIndex + 1]
      setCurrentIndex(currentIndex + 1)
      setAnswerText('')
      setCodeSnapshot(next?.starter_code ?? '')
      setFeedback(null)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Practice</h2>
      <SetBuilder onBuild={buildSet} unit={unit} subjectCode={subjectCode} />

      {currentQuestion && (
        <section className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Question {currentIndex + 1}/{questions.length}
            </p>
            <p className="text-sm font-semibold">
              {currentQuestion.marks} mark{currentQuestion.marks > 1 ? 's' : ''}
            </p>
          </div>

          <p className="text-sm text-slate-500">
            Type: {currentQuestion.type} • Exam style: {currentQuestion.exam_style}
          </p>
          <div className="flex flex-wrap gap-2">
            {currentQuestion.command_terms.map((term) => (
              <CommandTermBadge key={term} term={term} />
            ))}
          </div>

          <div className="rounded border bg-slate-50 p-3 text-sm">{currentQuestion.prompt_md}</div>
          {currentQuestion.case_material_md ? (
            <div className="rounded border border-amber-200 bg-amber-50 p-3 text-sm">{currentQuestion.case_material_md}</div>
          ) : null}

          {currentQuestion.type === 'mcq' && currentQuestion.options_json ? (
            <div className="space-y-2">
              {Object.entries(currentQuestion.options_json).map(([key, value]) => (
                <label key={key} className="flex items-center gap-2 rounded border bg-slate-50 px-3 py-2 text-sm">
                  <input
                    type="radio"
                    name="mcq"
                    value={key}
                    checked={answerText.toLowerCase() === key.toLowerCase()}
                    onChange={(e) => setAnswerText(e.target.value)}
                  />
                  <span>
                    {key}: {value}
                  </span>
                </label>
              ))}
            </div>
          ) : null}

          {['short', 'explain_justify', 'skill_drill'].includes(currentQuestion.type) ? (
            <textarea
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              className="h-40 w-full rounded border p-2 text-sm"
              placeholder="Write your answer..."
            />
          ) : null}

          {currentQuestion.type === 'code' ? (
            <div className="space-y-2">
              <textarea
                value={codeSnapshot}
                onChange={(e) => setCodeSnapshot(e.target.value)}
                className="h-56 w-full rounded border bg-slate-900 p-2 font-mono text-xs text-emerald-200"
              />
              <p className="text-xs text-slate-500">
                Public tests are used immediately; hidden tests run in practice mode only.
              </p>
            </div>
          ) : null}

          {currentQuestion.type === 'data' ? (
            <div className="space-y-2 rounded border border-blue-200 bg-blue-50 p-3">
              <p className="text-sm">Dataset preview + chart builder available in Data Lab.</p>
              <a href="/tools/data-lab" className="text-sm font-semibold text-blue-700 underline">
                Open Data Lab
              </a>
              <textarea
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                className="h-32 w-full rounded border p-2 text-sm"
                placeholder="Write your data interpretation..."
              />
            </div>
          ) : null}

          <div className="flex gap-2">
            <button
              onClick={submitAttempt}
              disabled={isMarking}
              className="rounded bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {isMarking ? 'Marking...' : 'Submit'}
            </button>
            <button onClick={nextQuestion} className="rounded bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">
              Next
            </button>
          </div>
        </section>
      )}

      {feedback && (
        <FeedbackPanel
          feedback={feedback.feedback}
          whereMarksWereLost={feedback.where_marks_were_lost}
          commonMistakes={feedback.common_mistakes}
          upgradeResponse={feedback.upgrade_response}
        />
      )}
    </div>
  )
}
