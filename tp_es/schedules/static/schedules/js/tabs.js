const tabs = document.querySelectorAll('.tab-btn');
const filterBtn = document.querySelector('.action-btn--ghost');
const TAB_STORAGE_KEY = 'planify.activeCalendarTab';

tabs.forEach(tab => tab.addEventListener('click', () => tabClicked(tab)));

const tabClicked = (tab) => {
  if (!tab) return;

    tabs.forEach(tab => tab.classList.remove('active'));
    tab.classList.add('active');
    
    const contents = document.querySelectorAll('.content');
    
    contents.forEach(content => content.classList.remove('show'));

    const contentId = tab.getAttribute('content-id');
    const content = document.getElementById(contentId);
    if (!content) return;

    content.classList.add('show');

    // Keep the current tab between page reloads/navigation.
    localStorage.setItem(TAB_STORAGE_KEY, contentId);

    if (contentId === 'agendas') {
      if (filterBtn) filterBtn.style.display = 'none';
    } else {
      if (filterBtn) filterBtn.style.display = 'flex';
    }
}

const getActiveTabId = () => {
  const activeTab = document.querySelector('.tab-btn.active');
  return activeTab ? activeTab.getAttribute('content-id') : null;
};

const ensureTabField = (form, tabId) => {
  if (!(form instanceof HTMLFormElement) || !tabId) return;

  let tabInput = form.querySelector('input[name="tab"]');
  if (!tabInput) {
    tabInput = document.createElement('input');
    tabInput.type = 'hidden';
    tabInput.name = 'tab';
    form.appendChild(tabInput);
  }

  tabInput.value = tabId;
};

document.addEventListener('submit', (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;

  const activeTabId = getActiveTabId();
  ensureTabField(form, activeTabId);
});

// Some flows use form.submit() directly (e.g., checkbox onchange), which skips submit events.
if (!window.__planifyPatchedFormSubmit) {
  const nativeSubmit = HTMLFormElement.prototype.submit;
  HTMLFormElement.prototype.submit = function patchedSubmit() {
    ensureTabField(this, getActiveTabId());
    return nativeSubmit.call(this);
  };
  window.__planifyPatchedFormSubmit = true;
}

  const getInitialTab = () => {
    const params = new URLSearchParams(window.location.search);
    const tabFromQuery = params.get('tab');
    if (tabFromQuery && document.querySelector(`.tab-btn[content-id="${tabFromQuery}"]`)) {
      return tabFromQuery;
    }

    const tabFromStorage = localStorage.getItem(TAB_STORAGE_KEY);
    if (tabFromStorage && document.querySelector(`.tab-btn[content-id="${tabFromStorage}"]`)) {
      return tabFromStorage;
    }

    const fallbackTab = document.querySelector('.tab-btn.active');
    return fallbackTab ? fallbackTab.getAttribute('content-id') : 'calendario';
  };

  const initialTabId = getInitialTab();
  const initialTab = document.querySelector(`.tab-btn[content-id="${initialTabId}"]`) || document.querySelector('.tab-btn.active') || tabs[0];
  tabClicked(initialTab);