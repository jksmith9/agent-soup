import './style.css';
import { XMLParser } from 'fast-xml-parser';

async function fetchEvents() {
  const statusEl = document.getElementById('status');
  const urgentGrid = document.getElementById('urgent-events-grid');
  const upcomingGrid = document.getElementById('upcoming-events-grid');
  
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
    
    if (!items.length) {
      statusEl.textContent = 'No events currently scheduled.';
      return;
    }
    
    const now = new Date();
    // One week window for "High Traffic"
    const oneWeekMs = 7 * 24 * 60 * 60 * 1000; 
    
    let events = items.map(item => {
      // Carbonhouse RSS provides dc:date
      const dateString = item['ev:startdate'] || item['dc:date'] || item.pubDate;
      const eventDate = new Date(dateString);
      
      return {
        title: item.title,
        link: item.link,
        date: eventDate,
        type: item['ev:type'] || 'Event',
      };
    });
    
    // Filter out past events
    events = events.filter(e => e.date > now);
    
    // Sort chronologically
    events.sort((a, b) => a.date - b.date);
    
    const urgentEvents = events.filter(e => (e.date.getTime() - now.getTime()) <= oneWeekMs);
    const upcomingEvents = events.filter(e => (e.date.getTime() - now.getTime()) > oneWeekMs);
    
    statusEl.classList.add('hidden');
    
    if (urgentEvents.length > 0) {
      renderEvents(urgentGrid, urgentEvents, true);
    } else {
      document.getElementById('high-impact').classList.add('hidden');
    }
    
    if (upcomingEvents.length > 0) {
      renderEvents(upcomingGrid, upcomingEvents, false);
    } else {
      document.getElementById('future-impact').classList.add('hidden');
    }
    
  } catch (error) {
    statusEl.textContent = `Error loading events: ${error.message}`;
    statusEl.style.color = '#ef4444';
  }
}

function renderEvents(gridElement, events, isUrgent) {
  const dateFormatter = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });

  events.forEach((event, index) => {
    const card = document.createElement('a');
    card.href = event.link;
    card.target = '_blank';
    card.className = `event-card ${isUrgent ? 'high-risk' : ''}`;
    // Limit animation delays
    if (index > 5) card.style.animationDelay = '0.6s';
    
    const title = document.createElement('h3');
    title.textContent = event.title;
    
    const dateLine = document.createElement('div');
    dateLine.className = 'event-date';
    dateLine.textContent = dateFormatter.format(event.date);
    
    const typeLabel = document.createElement('div');
    typeLabel.className = 'event-type';
    typeLabel.textContent = event.type;
    
    card.appendChild(typeLabel);
    card.appendChild(title);
    card.appendChild(dateLine);
    
    gridElement.appendChild(card);
  });
}

fetchEvents();
