document.getElementById("convertBtn").addEventListener("click", function () {
    var selectedFileType = document.getElementById("fileType").value;

    if (selectedFileType === 'select') {
        alert('Please select a file type.');
        return;
    }

    var currentUrl = window.location.pathname;
    var convertUrl = '/convert' + currentUrl;

    fetch(convertUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fileType: selectedFileType }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);

            var conversionResultElement = document.getElementById("conversionResult");
            conversionResultElement.innerHTML = 'Conversion Information:<br>';
            conversionResultElement.innerHTML += 'File Type: ' + data.result.fileType + '<br>';
            conversionResultElement.innerHTML += 'File Size: ' + data.result.fileSize + '<br>';

            if (data.result.conversionStatus !== undefined) {
                conversionResultElement.innerHTML += 'Conversion Status: ' + data.result.conversionStatus + '<br>';
            }

            var modalFooter = document.getElementById("modalFooter");
            if (modalFooter) {
                // Clear existing content
                modalFooter.innerHTML = '';

                // Add the cancel button back to the modal footer
                modalFooter.innerHTML += '<a href="#" class="btn" data-dismiss="modal" aria-hidden="true">Cancel</a>';

                // Check if the download button already exists
                var downloadBtn = document.getElementById("downloadBtn");
                if (!downloadBtn) {
                    modalFooter.innerHTML += '<button id="downloadBtn" class="btn btn-primary">Download</button>';
                }

                document.getElementById("downloadBtn").addEventListener("click", function () {
                    window.location.href = `/download${currentUrl}?fileType=${selectedFileType}`;
                });
            } else {
                console.error('Modal footer element not found.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
