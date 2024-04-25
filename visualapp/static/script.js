// /// function uploadVideo() {
// //     var form = document.getElementById('videoForm');
// //     var input = document.getElementById('videoFile');
// //     var video = document.getElementById('videoPlayer');

// //     var file = input.files[0];
// //     var objectURL = URL.createObjectURL(file);

// //     video.src = objectURL;

// //     // Hide the form after uploading

// // }

// // function uploadVideo() {
// //     var form = document.getElementById('videoForm');
// //     var input = document.getElementById('videoFile');
// //     var video = document.getElementById('videoPlayer');

// //     var file = input.files[0];

// //     // Check if a file is selected
// //     if (file) {
// //         // Create a FormData object and append the file to it
// //         var formData = new FormData();
// //         formData.append('videoFile', file);

// //         // Send an AJAX request to Django view to handle file upload
// //         var xhr = new XMLHttpRequest();
// //         xhr.open('POST', '/upload_video/', true);

// //         // Define the callback function when the upload is successful
// //         xhr.onload = function () {
// //             if (xhr.status === 200) {
// //                 // Parse the response if needed
// //                 var response = JSON.parse(xhr.responseText);
// //                 // Handle the response or perform additional actions
// //                 console.log(response);
// //             } else {
// //                 // Handle error cases
// //                 console.error('File upload failed!');
// //             }
// //         };

// //         // Send the FormData with the file
// //         xhr.send(formData);
// //     } else {
// //         console.error('No file selected!');
// //     }
// // }
// function uploadVideo() {
//     var form = document.getElementById('videoForm');
//     var input = document.getElementById('videoFile');
//     var video = document.getElementById('videoPlayer');

//     var file = input.files[0];

//     // Check if a file is selected
//     if (file) {
//         // Create a FormData object and append the file to it
//         var formData = new FormData();
//         formData.append('videoFile', file);

//         // Send an AJAX request to Django view to handle file upload
//         var xhr = new XMLHttpRequest();
//         xhr.open('POST', '/upload_video/', true);

//         // Define the callback function when the upload is successful
//         xhr.onload = function () {
//             if (xhr.status === 200) {
//                 // Parse the response
//                 var response = JSON.parse(xhr.responseText);

//                 // Update video source based on the server response
//                 video.src = response.file_path;

//                 // Handle the response or perform additional actions
//                 console.log(response);
//             } else {
//                 // Handle error cases
//                 console.error('File upload failed!');
//             }
//         };

//         // Send the FormData with the file
//         xhr.send(formData);
//     } else {
//         console.error('No file selected!');
//     }
// }
document.addEventListener("DOMContentLoaded", function () {
    var executeScriptButton = document.getElementById('executeScriptButton');
    var outputTextField = document.getElementById('outputTextField');

    executeScriptButton.addEventListener("click", function () {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'execute_script', true); // Specify the URL directly here
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken')); // Include CSRF token if required by Django
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var startIndex = xhr.responseText.indexOf("<!-- Display transcripts -->");
                    var endIndex = xhr.responseText.indexOf("</div>");

                    // Extract the desired content
                    var transcriptsContent = xhr.responseText.substring(startIndex, endIndex);

                    // Modify the extracted content
                    var modifiedTranscripts = transcriptsContent
                        .replace(/<[^>]+>/g, '')   // Remove HTML tags
                        .replace(/<p>\d+s: /g, '') // Remove "<p>s: " from each line
                        .replace(/<\/p>/g, '')     // Remove "</p>" from each line
                        .replace(/&#x27;/g, "")
                        .trim();                   // Trim whitespace from both ends

                    // Set the modified transcripts as the value of outputTextField
                    outputTextField.value = modifiedTranscripts;
                } else {
                    // Handle error
                    outputTextField.value = "Failed to execute script";
                }
            }
        };

        // Send the request
        xhr.send();
    });
});

// Function to get CSRF token from cookies
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
