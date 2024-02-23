// function uploadVideo() {
//     var form = document.getElementById('videoForm');
//     var input = document.getElementById('videoFile');
//     var video = document.getElementById('videoPlayer');

//     var file = input.files[0];
//     var objectURL = URL.createObjectURL(file);

//     video.src = objectURL;

//     // Hide the form after uploading

// }
function uploadVideo() {
    var form = document.getElementById('videoForm');
    var input = document.getElementById('videoFile');
    var video = document.getElementById('videoPlayer');

    var file = input.files[0];

    // Check if a file is selected
    if (file) {
        // Create a FormData object and append the file to it
        var formData = new FormData();
        formData.append('videoFile', file);

        // Send an AJAX request to Django view to handle file upload
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload_video/', true);

        // Define the callback function when the upload is successful
        xhr.onload = function () {
            if (xhr.status === 200) {
                // Parse the response if needed
                var response = JSON.parse(xhr.responseText);
                // Handle the response or perform additional actions
                console.log(response);
            } else {
                // Handle error cases
                console.error('File upload failed!');
            }
        };

        // Send the FormData with the file
        xhr.send(formData);
    } else {
        console.error('No file selected!');
    }
}
