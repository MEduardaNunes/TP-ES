const DAY_START_MIN = 7 * 60;  
const DAY_END_MIN   = 22 * 60;  
const DAY_RANGE_MIN = DAY_END_MIN - DAY_START_MIN;
 
function parseTimeToMinutes(timeStr) {
    if (!timeStr) return 0;
    const [h, m] = timeStr.split(':');
    return parseInt(h) * 60 + parseInt(m);
}
 
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}
 
//Agrupa eventos que se sobrepõem temporalmente (transitivo).
//Cada evento é adicionado ao primeiro grupo cujo maxEnd > start do evento.

function groupOverlappingEvents(events) {
    if (events.length === 0) return [];
 
    const sorted = [...events].sort((a, b) =>
        parseTimeToMinutes(a.start_time) - parseTimeToMinutes(b.start_time)
    );

    const groups = [];
 
    sorted.forEach(event => {
        const start = parseTimeToMinutes(event.start_time);
        const end   = parseTimeToMinutes(event.end_time);
 
        let placed = false;
        for (const group of groups) {
            if (start < group.maxEnd) {
                group.events.push(event);
                group.maxEnd = Math.max(group.maxEnd, end);
                placed = true;
                break;
            }
        }
        if (!placed) {
            groups.push({ events: [event], maxEnd: end });
        }
    });
 
    return groups.map(g => g.events);
}
 
/**
 * Calcula colunas dentro de um grupo de eventos sobrepostos.
 * Retorna todos os eventos com { column, totalColumns }.
 */
function layoutGroup(group) {
    const columns = []; // columns[i] = end_time do último evento na coluna i
 
    const result = group.map(event => {
        const start = parseTimeToMinutes(event.start_time);
        const end   = parseTimeToMinutes(event.end_time);
 
        let col = 0;
        while (columns[col] !== undefined && columns[col] > start) {
            col++;
        }
        columns[col] = end;
 
        return { ...event, column: col };
    });
 
    const totalColumns = columns.length;
    return result.map(e => ({ ...e, totalColumns }));
}

function hexToRgba(hex, alpha) {
  hex = hex.replace('#', '');

  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

 
function renderEvent(event) {
    const timeHtml = event.start_time && 
                    event.start_time !== "None" && 
                    event.start_time !== "null"
    ? `<div class="event-time">${event.start_time}</div>`
    : '';
    const isChecked = event.is_checked;
    const eventColor = isChecked ? hexToRgba(event.color, 0.9) : event.color;
    const iconHtml = event.icon_image_url
        ? `<img src="${escapeHtml(event.icon_image_url)}" class="activity-icon-image" alt="" onerror="this.style.display='none'">`
        : (event.icon_emoji || event.default_icon_emoji)
            ? `<span class="activity-icon-emoji">${escapeHtml(event.icon_emoji || event.default_icon_emoji)}</span>`
            : '';

    return `
           <div class="event-card ${isChecked ? 'event-card--completed' : ''}"
               data-event-id="${escapeHtml(String(event.id || ''))}"
               data-schedule-id="${escapeHtml(String(event.schedule_id || ''))}"
               data-schedule-name="${escapeHtml(event.schedule_name || '')}"
               data-color="${escapeHtml(event.color || '#6366f1')}"
               data-can-manage="${escapeHtml(event.can_manage ? 'true' : 'false')}"
               data-title="${escapeHtml(event.title || '')}"
               data-kind="${escapeHtml(event.kind || '')}"
               data-activity-type="${escapeHtml(event.activity_type || '')}"
               data-priority="${escapeHtml(event.priority || 'important')}"
               data-date="${escapeHtml(event.date || '')}"
               data-start-time="${escapeHtml(event.start_time || '')}"
               data-end-time="${escapeHtml(event.end_time || '')}"
               data-notes="${escapeHtml(event.notes || '')}"
               data-icon-emoji="${escapeHtml(event.icon_emoji || '')}"
               data-icon-image-url="${escapeHtml(event.icon_image_url || '')}"
               style="background-color: ${escapeHtml(eventColor)};">
            ${timeHtml}
            <div class="event-title">${iconHtml}${escapeHtml(event.title)}</div>
        </div>
    `;
}
 
/**
 * Render de uma tarefa (sem posicionamento temporal).
 */
function renderTask(task) {
    const isChecked = task.is_checked;
    const color = isChecked ? hexToRgba(task.color, 0.9) : (task.color || '#59e7ec');
    const iconHtml = task.icon_image_url
        ? `<img src="${escapeHtml(task.icon_image_url)}" class="activity-icon-image" alt="" onerror="this.style.display='none'">`
        : (task.icon_emoji || task.default_icon_emoji)
            ? `<span class="activity-icon-emoji">${escapeHtml(task.icon_emoji || task.default_icon_emoji)}</span>`
            : '';

    return `
           <div class="task-item ${isChecked ? 'task-item--completed' : ''}" 
               data-task-id="${escapeHtml(String(task.id || ''))}"
               data-schedule-id="${escapeHtml(String(task.schedule_id || ''))}"
               data-schedule-name="${escapeHtml(task.schedule_name || '')}"
               data-color="${escapeHtml(task.color || '#6366f1')}"
               data-can-manage="${escapeHtml(task.can_manage ? 'true' : 'false')}"
               data-title="${escapeHtml(task.title || '')}"
               data-kind="${escapeHtml(task.kind || '')}"
               data-activity-type="${escapeHtml(task.activity_type || '')}"
               data-priority="${escapeHtml(task.priority || 'important')}"
               data-date="${escapeHtml(task.date || '')}"
               data-start-time="${escapeHtml(task.start_time || '')}"
               data-end-time="${escapeHtml(task.end_time || '')}"
               data-icon-emoji="${escapeHtml(task.icon_emoji || '')}"
               data-icon-image-url="${escapeHtml(task.icon_image_url || '')}"
              data-notes="${escapeHtml(task.notes || '')}">
            <div class="task-dot" style="background-color:${color};"></div>
            <span class="task-title">${iconHtml}${escapeHtml(task.title)}</span>
        </div>
    `;
}
 
function renderDayCell(dayData, isToday) {
    const events = dayData.activities
        .filter(a => a.kind === 'event')
        .sort((a, b) => parseTimeToMinutes(a.start_time) - parseTimeToMinutes(b.start_time));
    const tasks  = dayData.activities.filter(a => a.kind === 'task');
 
    const todayClass = isToday ? 'today' : '';
 
    const tasksHtml = tasks.length > 0
        ? `<div class="day-tasks">${tasks.map(renderTask).join('')}</div>`
        : '';
 
    return `
        <div class="calendar-day ${todayClass}" data-day="${dayData.day}">
            <div class="day-number">${dayData.day}</div>
            ${tasksHtml}
            <div class="day-events">
                ${events.map(renderEvent).join('')}
            </div>
        </div>
    `;
}
 
/**
 * Render do grid completo do calendário.
 */
function renderCalendar() {
    const grid = document.getElementById('calendar-grid');

    if (!window.calendarData) {
        console.error("calendarData não carregado");
        return;
    }

    const { year, month, days } = window.calendarData;
    
    const today = new Date();
 
    const html = days.map(dayData => {
        if (!dayData.day) {
            return `<div class="calendar-day other-month"></div>`;
        }
 
        const isToday =
            dayData.day === today.getDate() &&
            month === (today.getMonth() + 1) &&
            year === today.getFullYear();
 
        return renderDayCell(dayData, isToday);
    }).join('');
 
    grid.innerHTML = html;
}
 
// modal de criação de eventos/tarefas
function openCreateModal(day) {
    const modal     = document.getElementById('modal');
    const dateInput = document.getElementById('date-input');
 
    const { year, month } = window.calendarData;
 
    const formattedMonth = String(month).padStart(2, '0');
    const formattedDay   = String(day).padStart(2, '0');
 
    dateInput.value = `${year}-${formattedMonth}-${formattedDay}`;
 
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}
 
document.addEventListener('DOMContentLoaded', () => {
    renderCalendar();
    setupDayClick();
 
    const form         = document.getElementById('activity-form');
    const kindSelect   = document.getElementById('kind-select');
    const scheduleSelect = document.getElementById('schedule-select');
 
    if (form) {
        form.addEventListener('submit', function () {
            if (scheduleSelect) {
                const scheduleId = scheduleSelect.value;
                this.action = `/schedules/${scheduleId}/create_activity/`;
            }
        });
    }
 
    if (kindSelect) {
        kindSelect.addEventListener('change', function () {
            const timeFields = document.getElementById('time-fields');
            if (timeFields) {
                timeFields.style.display = this.value === 'task' ? 'none' : 'block';
            }
        });
    }
});
 
function setupDayClick() {
    const grid = document.getElementById('calendar-grid');
    if (!grid) return;
 
    grid.addEventListener('click', (e) => {
        const eventCard = e.target.closest('.event-card');
        if (eventCard) {
            const activityData = {
                id: eventCard.dataset.eventId,
                schedule_id: eventCard.dataset.scheduleId,
                schedule_name: eventCard.dataset.scheduleName,
                color: eventCard.dataset.color,
                title: eventCard.dataset.title,
                kind: eventCard.dataset.kind,
                activity_type: eventCard.dataset.activityType,
                priority: eventCard.dataset.priority,
                date: eventCard.dataset.date,
                start_time: eventCard.dataset.startTime,
                end_time: eventCard.dataset.endTime,
                notes: eventCard.dataset.notes,
                icon_emoji: eventCard.dataset.iconEmoji,
                icon_image_url: eventCard.dataset.iconImageUrl
            };
            openActivityDetailsModal(e, activityData);
            return;
        }

        const taskItem = e.target.closest('.task-item');
        if (taskItem) {
            const activityData = {
                id: taskItem.dataset.taskId,
                schedule_id: taskItem.dataset.scheduleId,
                schedule_name: taskItem.dataset.scheduleName,
                color: taskItem.dataset.color,
                title: taskItem.dataset.title,
                kind: taskItem.dataset.kind,
                activity_type: taskItem.dataset.activityType,
                priority: taskItem.dataset.priority,
                date: taskItem.dataset.date,
                start_time: taskItem.dataset.startTime,
                end_time: taskItem.dataset.endTime,
                notes: taskItem.dataset.notes,
                icon_emoji: taskItem.dataset.iconEmoji,
                icon_image_url: taskItem.dataset.iconImageUrl
            };
            openActivityDetailsModal(e, activityData);
            return;
        }
        
        const dayCell = e.target.closest('.calendar-day');
        if (dayCell && dayCell.dataset.day) {
            if (!window.hasAdminSchedules) {
                showAlert("Você não é administrador de nenhuma agenda.");
                return;
            }
            openCreateModal(dayCell.dataset.day);
        }

        if (!dayCell) return;

        const day = dayCell.dataset.day;
        if (!day) return;
    });
}

function createToast(message, type = 'warning') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.textContent = message;

    container.appendChild(toast);
    window.requestAnimationFrame(() => toast.classList.add('show'));

    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        }, { once: true });
    }, 3200);
}

function showAlert(message, type = 'warning') {
    createToast(message, type);
}



