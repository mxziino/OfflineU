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

    // Generate last 7 days for the activity chart
    const getLast7Days = (): string[] => {
        const days = [];
        for (let i = 6; i >= 0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            days.push(d.toISOString().split('T')[0]);
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
                        <div className="flex items-end justify-between gap-2 h-32">
                            {last7Days.map((date) => {
                                const dayStat = weeklyMap.get(date);
                                const count = dayStat?.lessons_completed || 0;
                                const maxCount = Math.max(...last7Days.map(d => weeklyMap.get(d)?.lessons_completed || 0), 1);
                                const height = count > 0 ? Math.max((count / maxCount) * 100, 10) : 5;
                                const dayName = new Date(date).toLocaleDateString('en', { weekday: 'short' });
                                const isToday = date === new Date().toISOString().split('T')[0];

                                return (
                                    <div key={date} className="flex-1 flex flex-col items-center gap-2">
                                        <div
                                            className="w-full rounded-t-md transition-all duration-300"
                                            style={{
                                                height: `${height}%`,
                                                backgroundColor: count > 0
                                                    ? isToday ? 'hsl(var(--primary))' : 'hsl(var(--primary) / 0.6)'
                                                    : 'hsl(var(--muted))'
                                            }}
                                        />
                                        <div className="text-center">
                                            <p className={`text-xs ${isToday ? 'font-bold text-primary' : 'text-muted-foreground'}`}>
                                                {dayName}
                                            </p>
                                            {count > 0 && (
                                                <p className="text-xs font-medium">{count}</p>
                                            )}
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
