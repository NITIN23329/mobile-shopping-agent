import { Sparkles } from "lucide-react";
import type { FC } from "react";

const ChatHeader: FC = () => {
  return (
    <header className="sticky top-0 z-10 bg-gradient-to-br from-white/95 via-white/90 to-brand-50/80 backdrop-blur border-b border-slate-200">
      <div className="mx-auto flex max-w-4xl items-center gap-3 px-4 py-4 sm:px-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-100 text-brand-700 shadow-card">
          <Sparkles className="h-6 w-6" />
        </div>
        <div className="flex flex-col">
          <h1 className="font-display text-xl font-semibold text-slate-900 sm:text-2xl">
            Mobile Shopping Agent
          </h1>
          <p className="text-sm text-slate-600 sm:text-base">
            Discover, compare, and understand the best phones for your lifestyle.
          </p>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
