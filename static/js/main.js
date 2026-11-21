// SkillLens Interactive Client Script
document.addEventListener('DOMContentLoaded', () => {
  // 1. Live Skill Search Filter
  const skillSearchInput = document.getElementById('skillSearchInput');
  if (skillSearchInput) {
    skillSearchInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      const labels = document.querySelectorAll('.skill-tag-label');
      labels.forEach(label => {
        const text = label.textContent.toLowerCase();
        if (text.includes(term)) {
          label.style.display = 'flex';
        } else {
          label.style.display = 'none';
        }
      });
    });
  }

  // 2. Auto Dismiss Flash Alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // 3. Print Readiness Report Shortcut
  const printBtn = document.getElementById('printReportBtn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
});
