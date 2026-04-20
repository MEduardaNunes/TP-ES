const toggleButton = document.getElementById('toggle-btn')
const sidebar = document.getElementById('sidebar')


function toggleSidebar(){
    sidebar.classList.toggle('close')
    toggleButton.classList.toggle('rotate')

    closeAllSubMenus()
}

function toggleSubMenu(button){
    if(!button.nextElementSibling.classList.contains('show')) {
        closeAllSubMenus()
    }

    button.nextElementSibling.classList.toggle('show')
    button.classList.toggle('rotate')

    if(sidebar.classList.contains('close')) {
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')
    }
}

function closeAllSubMenus(){
    Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
        ul.classList.remove('show')
        ul.previousElementSibling.classList.remove('rotate')
    })
}

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
 
 
function renderEvent(event) {
    const rawStart = parseTimeToMinutes(event.start_time);
    const rawEnd   = parseTimeToMinutes(event.end_time);
 
    const start = Math.max(rawStart, DAY_START_MIN);
    const end   = Math.min(rawEnd, DAY_END_MIN);
 
    const top    = ((start - DAY_START_MIN) / DAY_RANGE_MIN) * 100;
    const height = Math.max(((end - start) / DAY_RANGE_MIN) * 100, 2.5); // mínimo visível
 
    const widthPct = 100 / event.totalColumns;
    const leftPct  = event.column * widthPct;
 
    return `
        <div class="event-card"
             data-event-id="${event.id}"
             style="
                top:    ${top}%;
                height: ${height}%;
                left:   ${leftPct}%;
                width:  calc(${widthPct}% - 3px);
                background-color: ${event.color};
             ">
            <div class="event-time">${event.start_time}</div>
            <div class="event-title">${event.title}</div>
        </div>
    `;
}
 
/**
 * Render de uma tarefa (sem posicionamento temporal).
 */
function renderTask(task) {
    const color = task.color || '#6366f1';
    return `
        <div class="task-item" data-task-id="${task.id}">
            <div class="task-dot" style="background-color:${color};"></div>
            <span class="task-title">${task.title}</span>
        </div>
    `;
}
 
function renderDayCell(dayData, isToday) {
    const events = dayData.activities.filter(a => a.kind === 'event');
    const tasks  = dayData.activities.filter(a => a.kind === 'task');
 
    const groups = groupOverlappingEvents(events);
    const positionedEvents = groups.flatMap(group => layoutGroup(group));
 
    const todayClass = isToday ? 'today' : '';
 
    const tasksHtml = tasks.length > 0
        ? `<div class="day-tasks">${tasks.map(renderTask).join('')}</div>`
        : '';
 
    return `
        <div class="calendar-day ${todayClass}" data-day="${dayData.day}">
            <div class="day-number">${dayData.day}</div>
            <div class="day-events">
                ${positionedEvents.map(renderEvent).join('')}
            </div>
            ${tasksHtml}
        </div>
    `;
}
 
/**
 * Render do grid completo do calendário.
 */
function renderCalendar() {
    const grid = document.getElementById('calendar-grid');
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
 
        return `
            <div class="calendar-day ${isToday ? 'today' : ''}" data-day="${dayData.day}">
                <div class="day-number">${dayData.day}</div>
            </div>
        `;
    }).join('');
 
    grid.innerHTML = html;
}
 
 
// modal de criação de eventos/tarefas
function openCreateModal(day) {
    const modal     = document.getElementById('modal');
    const dateInput = document.getElementById('modal-date');
 
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
 
    grid.addEventListener('click', (e) => {
        const dayCell = e.target.closest('.calendar-day');
        if (!dayCell) return;
 
        const day = dayCell.dataset.day;
        if (!day) return;
 
        openCreateModal(day);
    });
}

