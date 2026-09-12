<script src="file://{katex_js}"></script>
<script src="file://{auto_render_js}"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement === 'undefined') {{
            console.error("KaTeX auto-render not loaded");
            return;
        }}
        try {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ],
                throwOnError: false,
                strict: 'ignore'
            }});
        }} catch (e) {{
            console.error("KaTeX render error:", e);
        }}
    }});
</script>
