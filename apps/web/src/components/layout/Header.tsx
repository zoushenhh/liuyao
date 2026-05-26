import { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface HeaderProps {
  children?: ReactNode;
  backTo?: string;
  showSettings?: boolean;
  extra?: ReactNode;
}

const GearIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24"
       stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066
             c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426
             1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826
             3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924
             1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826
             -2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756
             -2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826
             -3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

export default function Header({ children, backTo, showSettings = true, extra }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-3 py-2
                      border-b-2 border-gold bg-paper/90 backdrop-blur gap-2">
      <div className="flex items-center gap-1 min-w-0">
        {backTo && (
          <Link to={backTo} className="flex-shrink-0 w-11 h-11 flex items-center justify-center
                                       text-cinnabar font-serif text-lg hover:text-cinnabar-hover
                                       transition-colors" aria-label="返回">
            &lt;
          </Link>
        )}
        {children}
      </div>
      <div className="flex items-center gap-1 flex-shrink-0">
        {extra}
        {showSettings && (
          <Link to="/settings" className="w-11 h-11 flex items-center justify-center
                                         text-cinnabar hover:text-cinnabar-hover transition-colors
                                         active:scale-95" aria-label="AI配置">
            <GearIcon />
          </Link>
        )}
      </div>
    </header>
  );
}
