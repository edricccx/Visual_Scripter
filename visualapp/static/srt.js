document.getElementById('download-srt').addEventListener('click', function() {
  fetchSRTFile();
});

function fetchSRTFile() {
  fetch('/generate_srt/')
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'transcript.srt');
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch(error => {
      console.error('Error fetching SRT file:', error);
    });
}