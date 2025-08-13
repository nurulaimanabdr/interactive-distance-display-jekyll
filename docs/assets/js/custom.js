<details>
  <summary>
document.addEventListener('DOMContentLoaded', function () {
  // copy buttons tied to data-target or nextElementSibling
  document.querySelectorAll('.copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var targetId = btn.getAttribute('data-target');
      var codeEl = targetId ? document.getElementById(targetId) : btn.nextElementSibling;
      if (!codeEl) return;
      var text = codeEl.textContent;
      navigator.clipboard.writeText(text).then(function() {
        var old = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function(){ btn.textContent = old; }, 1500);
      }, function() {
        alert('Copy failed — select and copy manually.');
      });
    });
  });

  // Optional: Add smooth scrolling to anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(e){
      var href = a.getAttribute('href');
      if (href.length > 1) {
        e.preventDefault();
        document.querySelector(href)?.scrollIntoView({behavior: 'smooth'});
      }
    });
  });
});
</summary>
