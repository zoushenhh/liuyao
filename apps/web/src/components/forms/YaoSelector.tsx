import { YAO_LABELS, YAO_NAMES, YAO_OPTIONS } from '../../types';

interface YaoSelectorProps {
  values: string[];
  onChange: (values: string[]) => void;
}

export default function YaoSelector({ values, onChange }: YaoSelectorProps) {
  function handleChange(index: number, name: string) {
    const next = [...values];
    next[index] = name;
    onChange(next);
  }

  return (
    <div>
      <h2 className="font-serif text-cinnabar text-lg mb-2">设定爻位</h2>
      <p className="text-xs text-gray-500 mb-3">
        从第一次（初爻）开始，依次向上填写到第六次（上爻）
      </p>
      <div className="grid grid-cols-3 gap-2">
        {YAO_LABELS.map((label, i) => (
          <div key={i} className="flex flex-col gap-1">
            <label className="text-xs font-serif text-cinnabar">{label}</label>
            <select
              value={values[i]}
              onChange={e => handleChange(i, e.target.value)}
              className="field text-sm"
            >
              <option value="">-- 请选择 --</option>
              {YAO_NAMES.map(name => (
                <option key={name} value={name}>
                  {YAO_OPTIONS[name].symbol} {name}
                </option>
              ))}
            </select>
            {values[i] && (
              <span className="text-xs text-gray-500">{YAO_OPTIONS[values[i]].desc}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
