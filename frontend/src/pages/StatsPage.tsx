import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { getDashboardStats, getWeeklyStats, type DashboardStats, type DailyStat } from '@/lib/api';
import {
    Flame, Trophy, BookOpen, Clock, Calendar, TrendingUp,
    ArrowLeft, CheckCircle2, BarChart3
} from 'lucide-react';

interface StatsPageProps {
    onBack: () => void;
}

export function StatsPage({ onBack }: StatsPageProps) {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [weekly, setWeekly] = useState<DailyStat[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([getDashboardStats(), getWeeklyStats()]).then(([statsData, weeklyData]) => {
            setStats(statsData);
            setWeekly(weeklyData);
            setLoading(false);
        });
    }, []);

    const formatTime = (seconds: number): string => {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    };

    const getLocalDateString = (date: Date = new Date()): string => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Generate last 7 days for the activity chart
    const getLast7Days = (): string[] => {
        const days = [];
        for (let i = 6; i >= 0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            days.push(getLocalDateString(d));
        }
        return days;
    };

    const last7Days = getLast7Days();
    const weeklyMap = new Map(weekly.map(d => [d.date, d]));

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-muted-foreground">Loading statistics...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b bg-card sticky top-0 z-10">
                <div className="container mx-auto px-4 py-3 flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={onBack}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-xl font-bold flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-primary" />
                            Statistics
                        </h1>
                        <p className="text-sm text-muted-foreground">Track your learning progress</p>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-6 max-w-4xl">
                {/* Stats Cards Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {/* Streak Card */}
                    <Card className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/30">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-orange-500/20">
                                    <Flame className="h-6 w-6 text-orange-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">{stats?.current_streak || 0}</p>
                                    <p className="text-xs text-muted-foreground">Day Streak</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Lessons Completed */}
                    <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-green-500/20">
                                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">{stats?.total_lessons_completed || 0}</p>
                                    <p className="text-xs text-muted-foreground">Lessons Done</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Courses */}
                    <Card className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/30">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-500/20">
                                    <BookOpen className="h-6 w-6 text-blue-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">{stats?.total_courses || 0}</p>
                                    <p className="text-xs text-muted-foreground">Courses</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Active Days */}
                    <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/30">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-purple-500/20">
                                    <Calendar className="h-6 w-6 text-purple-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">{stats?.active_days || 0}</p>
                                    <p className="text-xs text-muted-foreground">Active Days</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Today's Progress */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-primary" />
                            Today's Progress
                        </CardTitle>
                        <CardDescription>What you've accomplished today</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Lessons Completed</span>
                                    <span className="font-medium">{stats?.today_lessons_completed || 0}</span>
                                </div>
                                <Progress value={Math.min((stats?.today_lessons_completed || 0) * 10, 100)} className="h-2" />
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Time Spent</span>
                                    <span className="font-medium">{formatTime(stats?.today_time_spent_seconds || 0)}</span>
                                </div>
                                <Progress value={Math.min((stats?.today_time_spent_seconds || 0) / 36, 100)} className="h-2" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Weekly Activity */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Trophy className="h-5 w-5 text-yellow-500" />
                            Weekly Activity
                        </CardTitle>
                        <CardDescription>Lessons completed each day</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end justify-between gap-2 h-48 pt-4">
                            {last7Days.map((date) => {
                                const dayStat = weeklyMap.get(date);
                                const count = dayStat?.lessons_completed || 0;
                                const maxCount = Math.max(...last7Days.map(d => weeklyMap.get(d)?.lessons_completed || 0), 1);
                                // Ensure a minimum visual height for non-zero values so they are visible
                                const percentage = count > 0 ? (count / maxCount) * 100 : 0;
                                // Visual height: if 0, show small 'track' or nothing? Code used 5% for empty.
                                // Let's make 0 count have a very small height or just be a track.
                                const height = count > 0 ? Math.max(percentage, 5) : 4;

                                // Parse as local date to ensure day name matches current locale day
                                const dayDate = new Date(date + 'T00:00:00');
                                const dayName = dayDate.toLocaleDateString('en', { weekday: 'short' });
                                const isToday = date === getLocalDateString();

                                return (
                                    <div key={date} className="flex-1 h-full flex flex-col items-center justify-end group">
                                        {/* Bar Track Area */}
                                        <div className="flex-1 w-full flex items-end justify-center pb-2 relative">
                                            {/* Tooltip / Value Bubble on hover could go here */}

                                            {/* The Bar */}
                                            <div
                                                className={`w-full max-w-[2.5rem] rounded-t-md transition-all duration-500 ease-out 
                                                    ${count > 0
                                                        ? isToday ? 'bg-primary' : 'bg-primary/80 hover:bg-primary'
                                                        : 'bg-muted/30'
                                                    }`}
                                                style={{
                                                    height: `${height}%`
                                                }}
                                            >
                                                {/* Floating number for non-zero bars */}
                                            </div>
                                        </div>

                                        {/* Label Area */}
                                        <div className="h-10 text-center flex flex-col justify-start">
                                            <p className={`text-xs uppercase font-medium mb-0.5 ${isToday ? 'text-primary font-bold' : 'text-muted-foreground'}`}>
                                                {dayName}
                                            </p>
                                            <p className={`text-xs font-semibold leading-none ${count > 0 ? 'text-foreground' : 'text-transparent'}`}>
                                                {count > 0 ? count : '-'}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                {/* Total Stats */}
                <Card className="mt-6">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Clock className="h-5 w-5 text-muted-foreground" />
                            All Time Stats
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <p className="text-3xl font-bold text-primary">{stats?.total_lessons_completed || 0}</p>
                                <p className="text-sm text-muted-foreground">Total Lessons</p>
                            </div>
                            <div>
                                <p className="text-3xl font-bold text-primary">{formatTime(stats?.total_time_spent_seconds || 0)}</p>
                                <p className="text-sm text-muted-foreground">Time Learned</p>
                            </div>
                            <div>
                                <p className="text-3xl font-bold text-primary">{stats?.active_days || 0}</p>
                                <p className="text-sm text-muted-foreground">Days Active</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </main>
        </div>
    );
}
