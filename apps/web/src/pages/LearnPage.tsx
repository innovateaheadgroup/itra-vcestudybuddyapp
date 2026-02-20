import { useState } from 'react'

import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'

import { TopicCard } from '../components/TopicCard'
import { useAppContext } from '../context/AppContext'
import { api, type TopicCard as TopicCardData } from '../lib/api'

interface Lesson {
  id: number
  title: string
  content_md: string
  estimated_minutes: number
}

export function LearnPage() {
  const { subjectCode, unit } = useAppContext()
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null)

  const topicsQuery = useQuery({
    queryKey: ['learn-topics', subjectCode, unit],
    queryFn: () => api.get<TopicCardData[]>(`/api/learn/topics?subject_code=${subjectCode}&unit=${unit}`),
  })

  const lessonsQuery = useQuery({
    queryKey: ['learn-lessons', selectedTopicId],
    queryFn: () => api.get<Lesson[]>(`/api/learn/topics/${selectedTopicId}/lessons`),
    enabled: Boolean(selectedTopicId),
  })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Learn</h2>
      <p className="text-sm text-slate-500">Curriculum map by subject, topic, lesson and mastery.</p>
      {topicsQuery.isLoading ? <p>Loading topics...</p> : null}
      <div className="grid gap-3 lg:grid-cols-2">
        {(topicsQuery.data ?? []).map((topic) => (
          <button
            key={topic.topic.id}
            className="text-left"
            onClick={() => {
              setSelectedTopicId(topic.topic.id)
            }}
          >
            <TopicCard data={topic} />
          </button>
        ))}
      </div>

      {selectedTopicId && (
        <section className="rounded-xl border bg-white p-4 shadow-sm">
          <h3 className="mb-3 text-base font-semibold">Lessons</h3>
          {lessonsQuery.isLoading ? <p>Loading lessons...</p> : null}
          <div className="space-y-4">
            {(lessonsQuery.data ?? []).map((lesson) => (
              <article key={lesson.id} className="rounded-lg border bg-slate-50 p-3">
                <h4 className="text-sm font-semibold">
                  {lesson.title} <span className="text-xs text-slate-500">~{lesson.estimated_minutes} min</span>
                </h4>
                <div className="prose prose-sm mt-2 max-w-none">
                  <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{lesson.content_md}</ReactMarkdown>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
