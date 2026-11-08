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
    }
  }
};
</script>
<script src="file:__MATHJAX_JS_PATH__"></script>
