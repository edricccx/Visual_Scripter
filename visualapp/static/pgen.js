// script.js

document.getElementById("generatePreviewButton").addEventListener("click", function () {
    fetch('/generate_preview')
        .then(response => {
            if (!response.ok) {
                throw new Error('Preview generation failed');
            }
            return response.blob();
        })
        .then(blob => {
            // Create object URL for the blob
            const blobUrl = URL.createObjectURL(blob);
            // Create a link element to trigger download
            const link = document.createElement('a');
            link.href = blobUrl;
            link.setAttribute('download', 'preview.mp4');
            document.body.appendChild(link);
            // Trigger the click event on the link
            link.click();
            // Clean up
            document.body.removeChild(link);
        })
        .catch(error => {
            console.error('Error:', error.message);
        });
});
