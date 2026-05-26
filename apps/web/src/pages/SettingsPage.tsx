import { useState, useEffect } from 'react';
import Header from '../components/layout/Header';
import { loadSettings, saveSettings } from '../utils/storage';
import { validateApiKey } from '../api/client';
import type { AISettings } from '../types';
import { DEFAULT_SETTINGS } from '../types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<AISettings>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState(false);
  const [validating, setValidating] = useState(false);
  const [keyStatus, setKeyStatus] = useState<{ valid: boolean; message: string } | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    setSettings(loadSettings());
  }, []);

  function update<K extends keyof AISettings>(key: K, value: AISettings[K]) {
    setSettings(prev => ({ ...prev, [key]: value }));
  }

  function handleSave() {
    saveSettings(settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function handleReset() {
    saveSettings(DEFAULT_SETTINGS);
    setSettings({ ...DEFAULT_SETTINGS });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  async function handleValidate() {
    if (!settings.api_key.trim()) {
      setKeyStatus({ valid: false, message: '请先输入 API Key' });
      return;
    }
    setValidating(true);
    setKeyStatus(null);
    try {
      const res = await validateApiKey({
        base_url: settings.base_url,
        api_key: settings.api_key,
        model: settings.model,
      });
      setKeyStatus(res);
    } catch (e: unknown) {
      setKeyStatus({ valid: false, message: e instanceof Error ? e.message : '验证失败' });
    } finally {
      setValidating(false);
    }
  }

  return (
    <div className="max-w-full md:max-w-2xl lg:max-w-4xl xl:max-w-5xl mx-auto min-h-screen flex flex-col">
      <Header backTo="/" showSettings={false}>
        <h1 className="font-serif text-lg text-cinnabar font-bold">AI 配置</h1>
      </Header>

      <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">

        {/* Basic settings */}
        <section className="space-y-3">
          <h2 className="font-serif text-base text-cinnabar">基础设置</h2>

          <div>
            <label className="block font-serif text-xs text-cinnabar mb-1">Base URL</label>
            <input type="text" value={settings.base_url}
              onChange={e => update('base_url', e.target.value)}
              placeholder="自定义 API 地址（可选，留空使用 OpenAI 默认）"
              className="field text-sm" />
          </div>

          {/* Model + Temperature same row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-serif text-xs text-cinnabar mb-1">模型名称</label>
              <input type="text" value={settings.model}
                onChange={e => update('model', e.target.value)}
                className="field text-sm" />
            </div>
            <div>
              <label className="block font-serif text-xs text-cinnabar mb-1">
                温度: {settings.temperature.toFixed(1)}
              </label>
              <input type="range" min="0" max="1" step="0.1"
                value={settings.temperature}
                onChange={e => update('temperature', parseFloat(e.target.value))}
                className="w-full accent-cinnabar h-11" />
            </div>
          </div>

          <div>
            <label className="block font-serif text-xs text-cinnabar mb-1">API Key</label>
            <div className="flex gap-2">
              <input type="password" value={settings.api_key}
                onChange={e => update('api_key', e.target.value)}
                placeholder="请输入 API 密钥"
                className="field text-sm flex-1" />
              <button onClick={handleValidate} disabled={validating}
                      className="btn-gold px-3 text-sm flex-shrink-0 disabled:opacity-50">
                {validating ? '验证中...' : '验证'}
              </button>
            </div>
            {keyStatus && (
              <p className={`text-xs mt-1 ${keyStatus.valid ? 'text-green-600' : 'text-red-500'}`}>
                {keyStatus.message}
              </p>
            )}
          </div>
        </section>

        <hr className="border-gold/30" />

        {/* Prompts */}
        <section className="space-y-3">
          <h2 className="font-serif text-base text-cinnabar">提示词设置</h2>

          <div>
            <label className="block font-serif text-xs text-cinnabar mb-1">系统提示词</label>
            <textarea value={settings.system_prompt}
              onChange={e => update('system_prompt', e.target.value)}
              className="field h-32 resize-none font-mono text-xs" />
          </div>

          <div>
            <label className="block font-serif text-xs text-cinnabar mb-1">
              用户提示词模板
              <span className="text-gray-400 ml-1">{'({question} {pan_result})'}</span>
            </label>
            <textarea value={settings.user_prompt_template}
              onChange={e => update('user_prompt_template', e.target.value)}
              className="field h-40 resize-none font-mono text-xs" />
          </div>
        </section>

        <hr className="border-gold/30" />

        {/* Advanced - collapsible */}
        <section>
          <button onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center gap-2 w-full text-left font-serif text-base text-cinnabar
                             min-h-[44px] hover:text-cinnabar-hover transition-colors">
            <span className={`transition-transform text-xs ${showAdvanced ? 'rotate-90' : ''}`}>&gt;</span>
            高级选项
          </button>
          {showAdvanced && (
            <div className="mt-2 grid grid-cols-3 gap-3">
              <div>
                <label className="block font-serif text-xs text-cinnabar mb-1">
                  Token 数<span className="text-gray-400"> (0=不限)</span>
                </label>
                <input type="number" min="0"
                  value={settings.max_tokens ?? 0}
                  onChange={e => update('max_tokens', parseInt(e.target.value) || null)}
                  className="field text-sm" />
              </div>
              <div>
                <label className="block font-serif text-xs text-cinnabar mb-1">超时(秒)</label>
                <input type="number" min="1" max="300"
                  value={settings.timeout}
                  onChange={e => update('timeout', parseFloat(e.target.value) || 60)}
                  className="field text-sm" />
              </div>
              <div>
                <label className="block font-serif text-xs text-cinnabar mb-1">重试次数</label>
                <input type="number" min="0" max="10"
                  value={settings.max_retries}
                  onChange={e => update('max_retries', parseInt(e.target.value) || 0)}
                  className="field text-sm" />
              </div>
            </div>
          )}
        </section>

        <hr className="border-gold/30" />

        {/* Status */}
        {settings.api_key ? (
          <div className="p-2 bg-green-50 border-l-4 border-green-500 text-xs text-green-700 rounded">
            API Key 已配置
          </div>
        ) : (
          <div className="p-2 bg-yellow-50 border-l-4 border-gold text-xs text-dark rounded">
            请配置 API Key 以使用 AI 解读功能
          </div>
        )}

        {/* Actions */}
        <div className="grid grid-cols-2 gap-3">
          <button onClick={handleReset} className="btn-gold">重置默认</button>
          <button onClick={handleSave} className="btn-cinnabar">
            {saved ? '已保存' : '保存配置'}
          </button>
        </div>
      </main>
    </div>
  );
}
