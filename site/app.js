'use strict';
const shareButton = document.getElementById('copy-link');
const shareStatus = document.getElementById('copy-status');
shareButton.addEventListener('click', async () => {
  const url = 'https://xnos666.github.io/ReSkate-PS5/';
  try {
    await navigator.clipboard.writeText(url);
    shareStatus.textContent = 'Project link copied. Please include the experimental status when sharing.';
  } catch {
    shareStatus.textContent = 'Copy this link: ' + url;
  }
});
