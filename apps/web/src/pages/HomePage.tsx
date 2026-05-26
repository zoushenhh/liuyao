import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import YaoSelector from '../components/forms/YaoSelector';
import { cast } from '../api/client';
import { saveLastCast } from '../utils/storage';
import { YAO_OPTIONS, YAO_NAMES, type CastResponse } from '../types';

export default function HomePage() {
  const navigate = useNavigate();
  const d = new Date();
  const today = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  const now = `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;

  const [date, setDate] = useState(today);
  const [time, setTime] = useState(now);
  const [yaoValues, setYaoValues] = useState<string[]>(YAO_NAMES.slice(0, 6).map(() => ''));
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [guideOpen, setGuideOpen] = useState(false);

  async function handleCast() {
    const yaoCode = yaoValues.map(name => YAO_OPTIONS[name]?.code || '').join('');
    if (yaoCode.length !== 6 || !/^[6789]{6}$/.test(yaoCode)) {
      setError('请为每一爻选择硬币结果');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const result: CastResponse = await cast({ date, time, yao_code: yaoCode, question: question.trim() });
      saveLastCast(result);
      navigate('/result');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '排盘请求失败');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-full md:max-w-2xl lg:max-w-4xl xl:max-w-5xl mx-auto min-h-screen flex flex-col">
      <Header
        extra={
          <button onClick={() => setGuideOpen(!guideOpen)}
                  className="w-11 h-11 flex items-center justify-center
                             text-cinnabar hover:text-cinnabar-hover transition-colors
                             active:scale-95 font-serif font-bold text-lg"
                  title="如何摇卦">
            ?
          </button>
        }
      >
        <input type="date" value={date} onChange={e => setDate(e.target.value)}
               className="field text-sm h-10 py-1 flex-1 min-w-0" />
        <input type="time" value={time} onChange={e => setTime(e.target.value)}
               className="field text-sm h-10 py-1 flex-shrink-0 w-32" />
      </Header>

      {/* Guide popup */}
      {guideOpen && (
        <div className="absolute top-14 right-2 z-50 w-72 p-4 card text-sm leading-relaxed space-y-2 shadow-lg">
          <p><strong>准备工具</strong>：3枚硬币</p>
          <p><strong>步骤</strong>：</p>
          <ol className="list-decimal pl-5 space-y-1">
            <li>静心凝神，手握3枚硬币</li>
            <li>抛掷硬币，统计正反面数量</li>
            <li>重复6次，从初爻到上爻记录</li>
          </ol>
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-gold"><th className="text-left py-1">结果</th><th className="text-left py-1">叫法</th><th className="text-left py-1">含义</th></tr>
            </thead>
            <tbody>
              <tr className="border-b border-gold/30"><td className="py-1">三枚正面</td><td>老阴</td><td>变爻</td></tr>
              <tr className="border-b border-gold/30"><td className="py-1">两正一反</td><td>少阳</td><td>静爻</td></tr>
              <tr className="border-b border-gold/30"><td className="py-1">两反一正</td><td>少阴</td><td>静爻</td></tr>
              <tr><td className="py-1">三枚反面</td><td>老阳</td><td>变爻</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {error && (
        <div className="mx-4 mt-3 p-3 bg-red-50 border-l-4 border-cinnabar text-sm text-cinnabar rounded">
          {error}
        </div>
      )}

      <main className="flex-1 p-3 md:p-4 lg:p-6 space-y-3 overflow-y-auto">
        <YaoSelector values={yaoValues} onChange={setYaoValues} />

        <hr className="border-gold/30" />

        <div className="flex gap-2 items-stretch">
          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="所问何事？如：近期事业发展如何？"
            className="field flex-1 resize-none min-h-[48px] text-sm"
            rows={2}
          />
          <button onClick={handleCast} disabled={loading}
                  className="btn-cinnabar flex-shrink-0 px-6 disabled:opacity-50">
            {loading ? '生成中...' : '生成排盘'}
          </button>
        </div>
      </main>
    </div>
  );
}
