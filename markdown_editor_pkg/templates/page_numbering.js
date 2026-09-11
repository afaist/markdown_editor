<script>
    document.addEventListener("DOMContentLoaded", function() {{
        var footers = document.querySelectorAll('.page-footer');
        if (footers.length === 0) return;

        var originalFooter = footers[0];
        var footerTemplate = originalFooter.outerHTML;

        var content = document.body.innerHTML;
        var cleanContent = content
            .replace(/<div class="page-header"[^>]*>.*?<\\/div>/gi, '')
            .replace(/<div class="page-footer"[^>]*>.*?<\\/div>/gi, '');

        var newBody = document.createElement('div');
        newBody.style.cssText = 'width:100%;';

        var pageDiv = document.createElement('div');
        pageDiv.className = 'print-page';
        pageDiv.innerHTML = cleanContent;

        var resolved = footerTemplate.replace('{{PAGE_NUM}}', '1/1');
        var temp = document.createElement('div');
        temp.innerHTML = resolved;
        var footerEl = temp.firstChild;
        pageDiv.appendChild(footerEl);

        newBody.appendChild(pageDiv);
        document.body.innerHTML = '';
        document.body.appendChild(newBody);
    }});
</script>
