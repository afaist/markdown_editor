<script>
// MathJax 3 конфигурация — загружается ДО подключения библиотеки
window.MathJax = {
  tex: {
    inlineMath: [
      ['$', '$'],
      ['\\(', '\\)']
    ],
    displayMath: [
      ['$$', '$$'],
      ['\\[', '\\]']
    ],
    processEscapes: true,
    processEnvironments: true,
    packages: {
      '[+]': ['ams', 'bbox', 'textcomp']
    },
    tagSide: 'right',
    tagIndent: '0.8em'
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
    renderActions: {
      addMenu: []
    }
  },
  startup: {
    ready: function() {
      MathJax.startup.defaultReady();
      // Запускаем рендеринг после загрузки DOM
      function typeset() {
        MathJax.typesetPromise().catch(function(err) {
          console.warn('MathJax typeset error:', err.message);
        });
      }
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", typeset);
      } else {
        typeset();
      }
    }
  }
};
</script>
