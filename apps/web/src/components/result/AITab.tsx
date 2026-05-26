import { useState, useCallback } from 'react';
import type { CastResponse } from '../../types';
import { loadSettings } from '../../utils/storage';
import { interpret } from '../../api/client';

interface AITabProps {
  cast: CastResponse;
}

export default function AITab({ cast }: AITabProps) {
  const [question, setQuestion] = useState(cast.question);
  const [aiResult, setAiResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = useCallback(async () => {
    const settings = loadSettings();
    if (!settings.api_key.trim()) {
      setError('请先配置 API Key（点击右上角齿轮图标）');
      return;
    }
    if (!question.trim()) {
      setError('请输入所问之事');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const res = await interpret({
        question: question.trim(),
        pan_result: cast.pan_result,
        settings,
      });
      setAiResult(res.content);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'AI 解读失败');
    } finally {
      setLoading(false);
    }
  }, [question, cast.pan_result]);

  // After result, show card-style view only
  if (aiResult) {
    return (
      <div className="flex flex-col h-full">
        <div className="card flex-1 flex flex-col m-1">
          <div className="flex-1 overflow-y-auto p-4 text-sm leading-relaxed whitespace-pre-wrap">
            {aiResult}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 p-2">
          <button onClick={() => navigator.clipboard.writeText(aiResult)} className="btn-gold text-sm">
            复制结果
          </button>
          <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(aiResult)}`}
             download={`周易解读_${new Date().toISOString().slice(0, 10)}.txt`}
             className="btn-gold text-sm flex items-center justify-center">
            下载解读
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-2">
      <textarea
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="调整问题描述，以获得更精准的解读"
        className="field resize-none text-sm"
        rows={2}
      />
      <button onClick={handleGenerate} disabled={loading}
              className="btn-cinnabar w-full disabled:opacity-50">
        {loading ? 'AI 正在解读中...' : '生成 AI 解读'}
      </button>
      {error && (
        <div className="p-3 bg-red-50 border-l-4 border-cinnabar text-sm text-cinnabar rounded">
          {error}
        </div>
      )}
      {!aiResult && !loading && !error && (
        <div className="text-center py-8 text-gray-400 text-sm">
          输入问题后点击上方按钮生成 AI 解读
        </div>
      )}
    </div>
  );
}
