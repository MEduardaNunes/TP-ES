const tabs = document.querySelectorAll('.tab-btn');
const filterBtn = document.querySelector('.action-btn--ghost');

tabs.forEach(tab => tab.addEventListener('click', () => tabClicked(tab)));

const tabClicked = (tab) => {
    tabs.forEach(tab => tab.classList.remove('active'));
    tab.classList.add('active');
    
    const contents = document.querySelectorAll('.content');
    
    contents.forEach(content => content.classList.remove('show'));

    const contentId = tab.getAttribute('content-id');
    const content = document.getElementById(contentId);
    
    content.classList.add('show');

    if (contentId === 'agendas') {
    filterBtn.style.display = 'none';
  } else {
    filterBtn.style.display = 'flex';
  }
}

const currentActiveTab = document.querySelector('.tab-btn.active');
tabClicked(currentActiveTab);