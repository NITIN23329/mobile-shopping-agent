import type { FC } from "react";
import clsx from "clsx";

interface LoadingDotsProps {
  className?: string;
}

const LoadingDots: FC<LoadingDotsProps> = ({ className }) => {
  return (
    <span className={clsx("flex items-center gap-1", className)} aria-label="Loading">
      {[0, 1, 2].map((index) => (
        <span
          // eslint-disable-next-line react/no-array-index-key
          key={index}
          className={clsx(
            "h-2 w-2 rounded-full bg-brand-500/80",
            "animate-bounce",
            index === 1 && "[animation-delay:120ms]",
            index === 2 && "[animation-delay:240ms]",
          )}
        />
      ))}
    </span>
  );
};

export default LoadingDots;
