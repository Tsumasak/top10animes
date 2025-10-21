// 🗓️  AUTO-GENERATED - Week Configuration
// Generated on: 2025-10-20 15:37:08
// Current Week: 4

export interface WeekData {
  id: string;
  title: string;
  period: string;
  label: string;
  dataFile: string;
  status: 'Aired' | 'Airing' | 'Upcoming';
  isCurrentWeek: boolean;
}

export const CURRENT_WEEK_NUMBER = 4;

export const WEEKS_DATA: WeekData[] = [
  {
    id: 'week1',
    title: 'Week 1 - Sep 29-Oct 05, 2025',
    period: 'Aired - Sep 29, 2025 to Oct 05, 2025',
    label: 'Week 1',
    dataFile: 'week1_episodes_data.json',
    status: 'Aired',
    isCurrentWeek: false
  },
  {
    id: 'week2',
    title: 'Week 2 - Oct 06-Oct 12, 2025',
    period: 'Aired - Oct 06, 2025 to Oct 12, 2025',
    label: 'Week 2',
    dataFile: 'week2_episodes_data.json',
    status: 'Aired',
    isCurrentWeek: false
  },
  {
    id: 'week3',
    title: 'Week 3 - Oct 13-Oct 19, 2025',
    period: 'Aired - Oct 13, 2025 to Oct 19, 2025',
    label: 'Week 3',
    dataFile: 'week3_episodes_data.json',
    status: 'Aired',
    isCurrentWeek: false
  },
  {
    id: 'week4',
    title: 'Week 4 - Oct 20-Oct 26, 2025',
    period: 'Airing - Oct 20, 2025 to Oct 26, 2025',
    label: 'Week 4',
    dataFile: 'week4_episodes_data.json',
    status: 'Airing',
    isCurrentWeek: true
  },
];

// Helper functions
export const getCurrentWeek = () => WEEKS_DATA.find(week => week.isCurrentWeek);
export const getWeekById = (id: string) => WEEKS_DATA.find(week => week.id === id);
export const getFormattedPeriod = (week: WeekData): string => week.period;
