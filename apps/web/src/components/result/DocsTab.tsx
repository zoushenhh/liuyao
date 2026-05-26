import { useState, useEffect } from 'react';
import { fetchTexts, fetchText } from '../../api/client';
import type { TextItem, TextContent } from '../../types';

export default function DocsTab() {
  const [texts, setTexts] = useState<TextItem[]>([]);
  const [active, setActive] = useState('');
  const [content, setContent] = useState<TextContent | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTexts().then(items => {
      setTexts(items);
      if (items.length > 0) setActive(items[0].name);
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchText(active)
      .then(setContent)
      .catch(() => setContent(null))
      .finally(() => setLoading(false));
  }, [active]);

  return (
    <div className="space-y-3">
      <div className="flex overflow-x-auto scrollbar-hide space-x-1
                      -webkit-overflow-scrolling-touch border-b border-gold/50">
        {texts.map(t => (
          <button
            key={t.name}
            onClick={() => setActive(t.name)}
            className={`flex-shrink-0 px-4 py-2 text-sm font-serif font-bold rounded-t
                        min-h-[44px] transition-colors
                        ${active === t.name
                          ? 'border-b-2 border-cinnabar text-cinnabar'
                          : 'text-gray-500 hover:text-dark'}`}
          >
            {t.title}
          </button>
        ))}
      </div>

      <div className="card p-4 min-h-[50vh]">
        {loading ? (
          <div className="text-center py-8 text-gray-400">加载中...</div>
        ) : content ? (
          <div className="prose prose-sm max-w-none text-sm leading-relaxed whitespace-pre-wrap">
            {content.content}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">暂无内容</div>
        )}
      </div>
    </div>
  );
}
