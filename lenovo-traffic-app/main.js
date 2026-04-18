import './style.css';
import { XMLParser } from 'fast-xml-parser';

async function fetchEvents() {
  const statusEl = document.getElementById('status');
  const calendarContainer = document.getElementById('calendar-container');
  const calendarGrid = document.getElementById('calendar-grid');
  
  try {
    const res = await fetch('/api/events');
    if (!res.ok) throw new Error("Failed to fetch RSS data. Did you start the dev server?");
    
    const xmlData = await res.text();
    const parser = new XMLParser({
      ignoreAttributes: true,
      parseTagValue: true,
    });
    
    const jsonObj = parser.parse(xmlData);
    let items = jsonObj?.rss?.channel?.item;
    
    if (!Array.isArray(items)) {
        if (items) items = [items];
        else items = [];
    }
    
    const now = new Date();
    // We only care about events in the CURRENT month/year
    const currentMonth = now.getMonth(); 
    const currentYear = now.getFullYear();
    const headersDate = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(now);
    document.getElementById('current-month-display').textContent = headersDate;
    
    // Parse all events
    let events = items.map(item => {
      const dateString = item['ev:startdate'] || item['dc:date'] || item.pubDate;
      const eventDate = new Date(dateString);
      
      return {
        title: item.title,
        link: item.link,
        date: eventDate,
        type: item['ev:type'] || 'Event',
      };
    });
    
    // Filter to JUST the current month according to the user's request.
    events = events.filter(e => e.date.getMonth() === currentMonth && e.date.getFullYear() === currentYear);
    
    // Group events by day of month
    const eventsByDay = {};
    events.forEach(e => {
        const day = e.date.getDate();
        if (!eventsByDay[day]) eventsByDay[day] = [];
        eventsByDay[day].push(e);
    });
    
    // --- BUILD THE CALENDAR UI ---
    
    // Get the first day of the month (0 = Sun, 1 = Mon...)
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    // Get total days in month
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    // Determine how many rows are needed
    const totalCells = firstDay + daysInMonth;
    const requiredRows = Math.ceil(totalCells / 7);
    const totalSlotsToRender = requiredRows * 7;
    
    const todayNum = now.getDate();
    const isCurrentMonthActual = true; // since currentMonth is initialized from now()

    for (let i = 0; i < totalSlotsToRender; i++) {
        const cell = document.createElement('div');
        
        if (i < firstDay || i >= firstDay + daysInMonth) {
            // Empty cell outside the current month boundaries
            cell.className = 'calendar-day empty';
        } else {
            // Valid day cell
            const dayNumber = i - firstDay + 1;
            cell.className = 'calendar-day';
            
            // Highlight today
            if (isCurrentMonthActual && dayNumber === todayNum) {
                cell.classList.add('today');
            }
            
            const dayNumDiv = document.createElement('div');
            dayNumDiv.className = 'day-number';
            dayNumDiv.textContent = dayNumber;
            cell.appendChild(dayNumDiv);
            
            // Add events for this day
            if (eventsByDay[dayNumber] && eventsByDay[dayNumber].length > 0) {
                cell.classList.add('has-events');
                
                // Sort by time
                eventsByDay[dayNumber].sort((a,b) => a.date - b.date);
                
                eventsByDay[dayNumber].forEach(evt => {
                    const badge = document.createElement('a');
                    badge.href = evt.link;
                    badge.target = '_blank';
                    badge.className = 'event-badge';
                    
                    const timeStr = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' }).format(evt.date);
                    
                    badge.innerHTML = `<span class="event-time">${timeStr}</span> ${evt.title}`;
                    cell.appendChild(badge);
                });
            }
        }
        calendarGrid.appendChild(cell);
    }
    
    // Show calendar, hide status
    statusEl.classList.add('hidden');
    calendarContainer.classList.remove('hidden');

  } catch (error) {
    statusEl.textContent = `Error loading events: ${error.message}`;
    statusEl.style.color = '#c0392b';
  }
}

fetchEvents();
