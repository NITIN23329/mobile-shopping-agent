import { Github, Linkedin, Sparkles } from "lucide-react";
import type { FC } from "react";

const ChatHeader: FC = () => {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-gradient-to-br from-white/95 via-white/90 to-brand-50/80 backdrop-blur">
      <div className="mx-auto flex max-w-4xl items-center justify-between gap-3 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
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
        <div className="hidden items-center gap-2 sm:flex">
          <a
            href="https://github.com/NITIN23329/mobile-shopping-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="group inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:text-slate-900"
          >
            <Github className="h-4 w-4 transition group-hover:scale-110" />
            <span>GitHub</span>
          </a>
          <a
            href="https://www.linkedin.com/in/nitindas230202/"
            target="_blank"
            rel="noopener noreferrer"
            className="group inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:text-slate-900"
          >
            <Linkedin className="h-4 w-4 transition group-hover:scale-110" />
            <span>LinkedIn</span>
          </a>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
