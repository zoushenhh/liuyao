interface Tab {
  key: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (key: string) => void;
}

export default function Tabs({ tabs, active, onChange }: TabsProps) {
  return (
    <div className="flex border-b-2 border-gold">
      {tabs.map(tab => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`flex-1 py-3 px-1 font-serif font-bold text-center
                      text-sm transition-all min-h-[44px]
                      ${active === tab.key ? 'tab-selected' : 'tab-unselected'}`}
          role="tab"
          aria-selected={active === tab.key}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
