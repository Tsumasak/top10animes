'use client';

import { CURRENT_WEEK_NUMBER } from '../config/weeks';

interface BlankStateProps {
  weekNumber: number;
  weekPeriod: string;
  isCurrentWeek: boolean;
}

export default function BlankState({ weekNumber, weekPeriod, isCurrentWeek }: BlankStateProps) {
  const getCurrentWeekMessage = () => {
    if (!isCurrentWeek) {
      return {
        emoji: "📂",
        title: "No episodes available",
        message: "This week doesn't have any loaded episodes.",
        submessage: "Data might not have been updated yet for this week."
      };
    }

    // Current week messages
    return {
      emoji: "⏰",
      title: "Current week in progress",
      message: "Episodes for this week are still being released.",
      submessage: "New episodes will appear here as they are released throughout the week."
    };
  };

  const { emoji, title, message, submessage } = getCurrentWeekMessage();

  return (
    <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
      <div className="text-6xl mb-6">{emoji}</div>
      <h3 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-200">
        {title}
      </h3>
      <p className="text-lg text-gray-600 dark:text-gray-400 mb-3 max-w-md">
        {message}
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-500 mb-6 max-w-lg">
        {submessage}
      </p>
    </div>
  );
}