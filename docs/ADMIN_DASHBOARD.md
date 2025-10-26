# IT Quizbee - Admin Dashboard

## Overview

The Admin Dashboard provides comprehensive analytics and insights into quiz performance, user attempts, and trends over time. It uses real-time data from the MySQL database to visualize quiz statistics through interactive charts and tables.

## Access

**URL:** `http://localhost:5000/admin`

The dashboard is accessible from any page via the **Dashboard** button in the header navigation.

## Features

### 📊 Summary Cards

Four key metrics displayed at the top:

1. **Total Attempts** - Total number of quiz attempts across all modes
2. **Average Score** - Overall average score percentage
3. **Popular Mode** - Most frequently used quiz mode
4. **Completed Sessions** - Total completed quiz sessions

### 📈 Interactive Charts

#### 1. Performance by Quiz Mode
- **Type:** Dual-axis bar chart
- **Shows:** Average score and number of attempts for each quiz mode
- **Modes:** Elimination, Finals, Review

#### 2. Performance by Difficulty (Finals Mode)
- **Type:** Doughnut chart
- **Shows:** Average scores for Easy, Average, and Difficult questions
- **Color-coded:** Green (Easy), Yellow (Average), Red (Difficult)

#### 3. Performance Trend (Last 30 Days)
- **Type:** Line chart with dual axes
- **Shows:** Average scores and attempt counts over time
- **Intervals:** Daily, Weekly, or Monthly (selectable)
- **Interactive:** Change interval using dropdown

#### 4. Performance by Topic
- **Type:** Pie chart
- **Shows:** Average scores for each topic
- **Only displays:** Topics with at least one attempt in review mode

### 📋 Recent Attempts Table

Shows the 20 most recent quiz attempts with:
- Date and time
- Quiz mode (with badge)
- Difficulty level (if applicable)
- Score percentage (color-coded)
- Questions answered (correct/total)
- View details link

**Filters:**
- **Mode Filter:** All Modes, Elimination Full, Finals Full, or Review
- **Date Filter:** Last 7, 14, 30, or 90 days

### 📊 Statistics Panels

#### Mode Statistics
Detailed breakdown by quiz mode:
- Average score
- Total attempts
- Visual bar indicator

#### Difficulty Statistics
Detailed breakdown by difficulty level:
- Average score per difficulty
- Total attempts
- Color-coded indicators

### ⚡ Quick Actions

- **Refresh Data** - Reload all analytics data
- **Export Analytics** - Export data (coming soon)
- **View API** - Direct access to raw API endpoint

## API Endpoints Used

The dashboard consumes the following analytics API endpoints:

### 1. Summary Statistics
```
GET /api/analytics/summary
```
Returns overall statistics including total attempts, average score, popular mode, and completed sessions.

### 2. Stats by Mode
```
GET /api/analytics/by-mode
```
Returns detailed statistics grouped by quiz mode.

### 3. Stats by Difficulty
```
GET /api/analytics/by-difficulty
```
Returns statistics for finals mode grouped by difficulty level.

### 4. Stats by Topic
```
GET /api/analytics/by-topic
```
Returns statistics grouped by topic (for review mode).

### 5. Recent Attempts
```
GET /api/analytics/recent-attempts?limit=20&days=7&mode=
```
Returns recent quiz attempts with filtering options.

### 6. Performance Trend
```
GET /api/analytics/performance-trend?days=30&interval=day
```
Returns performance trends over time with configurable intervals.

### 7. Attempt Details
```
GET /api/analytics/attempt/{attempt_id}
```
Returns detailed information about a specific quiz attempt.

## Data Visualization

### Charts Library
- **Chart.js v4.4.0** - Modern, responsive charts
- **Types Used:** Bar, Doughnut, Pie, Line

### Color Scheme
- **Primary:** Indigo (#4F46E5)
- **Success:** Green (#22C55E)
- **Warning:** Yellow (#EAB308)
- **Danger:** Red (#EF4444)
- **Purple:** #A855F7
- **Orange:** #F97316

### Score Color Coding
- **Green:** 80% and above (Excellent)
- **Yellow:** 60-79% (Good)
- **Red:** Below 60% (Needs improvement)

## Responsive Design

The dashboard is fully responsive and works on:
- ✅ Desktop (1920px+)
- ✅ Laptop (1280px-1920px)
- ✅ Tablet (768px-1280px)
- ✅ Mobile (320px-768px)

## Real-time Updates

### Auto-refresh
Charts and data automatically refresh when:
- Filter selections change
- Trend interval is modified
- Refresh button is clicked

### Manual Refresh
Click the **Refresh Data** button to reload all analytics data.

## Database Tables

The dashboard visualizes data from:

### quiz_sessions
- Session information
- Created and expiry times
- Completion status

### quiz_attempts
- Individual quiz results
- Scores and answers
- Timestamps
- Topic/subtopic metadata

## Use Cases

### For Educators
- Track student performance
- Identify difficult topics
- Monitor progress over time
- Analyze quiz mode effectiveness

### For Content Creators
- See which topics need more questions
- Identify difficulty level gaps
- Understand user engagement patterns

### For Administrators
- Monitor system usage
- Analyze peak usage times
- Track completion rates
- Export data for reporting

## Technical Details

### Frontend Technologies
- **Tailwind CSS** - Utility-first CSS framework
- **Bootstrap Icons** - Icon library
- **Chart.js** - Data visualization
- **Vanilla JavaScript** - No framework dependencies

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database queries
- **MySQL** - Database storage

### Performance
- Lazy loading of charts
- Efficient database queries with aggregation
- Client-side filtering where possible
- Optimized chart rendering

## Future Enhancements

Planned features:
- [ ] Export to CSV/Excel
- [ ] Date range picker
- [ ] User authentication
- [ ] Real-time notifications
- [ ] Advanced filtering options
- [ ] Custom report generation
- [ ] Email reports
- [ ] Comparison views

## Troubleshooting

### No Data Showing
- Ensure MySQL database is running
- Check database connection in `.env`
- Verify quiz attempts exist in database
- Check browser console for errors

### Charts Not Loading
- Clear browser cache
- Check Chart.js CDN availability
- Verify JavaScript console for errors

### Slow Loading
- Reduce date range in filters
- Check database connection speed
- Optimize database indexes
- Consider caching frequently accessed data

## Security Considerations

**Note:** This dashboard currently has no authentication. For production use:

1. Add authentication middleware
2. Implement role-based access control
3. Use HTTPS in production
4. Add CSRF protection
5. Sanitize all inputs
6. Rate limit API endpoints

## Support

For issues or questions:
1. Check this documentation
2. Review API endpoint responses
3. Check Flask application logs
4. Verify database connectivity

## License

MIT License - Same as main application
