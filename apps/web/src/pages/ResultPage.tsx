import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import Tabs from '../components/ui/Tabs';
import DivinationCard from '../components/result/DivinationCard';
import AITab from '../components/result/AITab';
import DocsTab from '../components/result/DocsTab';
import { loadLastCast } from '../utils/storage';
import type { CastResponse } from '../types';

const RESULT_TABS = [
  { key: 'pan', label: '卦象' },
  { key: 'ai', label: 'AI 解读' },
  { key: 'docs', label: '文档' },
];

export default function ResultPage() {
  const navigate = useNavigate();
  const [cast, setCast] = useState<CastResponse | null>(null);
  const [activeTab, setActiveTab] = useState('pan');

  useEffect(() => {
    const loaded = loadLastCast();
    if (!loaded) {
      navigate('/');
      return;
    }
    setCast(loaded);
  }, [navigate]);

  if (!cast) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-paper">
        <div className="text-center text-gray-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="max-w-full md:max-w-2xl lg:max-w-4xl xl:max-w-5xl mx-auto min-h-screen flex flex-col">
      <Header backTo="/"
        extra={
          <button onClick={() => navigate('/')}
                  className="btn-cinnabar h-9 px-3 text-sm">
            重新摇卦
          </button>
        }
      >
        <div className="text-xs text-gray-500 truncate">
          {cast.date} {cast.time} | 卦码:{cast.yao_code}
          {cast.question && <span className="ml-2">{cast.question}</span>}
        </div>
      </Header>

      <Tabs tabs={RESULT_TABS} active={activeTab} onChange={setActiveTab} />

      <div className="flex-1 overflow-hidden">
        {activeTab === 'pan' && <DivinationCard panResult={cast.pan_result} />}
        {activeTab === 'ai' && <AITab cast={cast} />}
        {activeTab === 'docs' && <DocsTab />}
      </div>
    </div>
  );
}
