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


document.addEventListener("DOMContentLoaded", function () {
    var outputTextField = document.getElementById('outputTextField');
    var translateButton = document.getElementById('translateButton');

    translateButton.addEventListener("click", function () {
        var inputText = outputTextField.value;
        var targetLanguage = document.getElementById('target-language').value;
        console.log("translation process online");
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/translate/', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        xhr.onload = function () {
            if (xhr.status === 200) {
                var translatedText = xhr.responseText;
                var formattedTranslation = translatedText.replace(/(\d+s:)/g, '\n$1');
                document.getElementById('translatedTextField').value = formattedTranslation;

            } else {
                document.getElementById('translatedTextField').value = 'Translation failed';
            }
        };

        xhr.send('input-text=' + encodeURIComponent(inputText) + '&target-language=' + encodeURIComponent(targetLanguage));

    });
});
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

document.addEventListener("DOMContentLoaded", function () {
    var videoPlayer = document.getElementById('videoPlayer');
    var subtitleDisplay = document.getElementById('subtitleDisplay');
    var subtitlePreviewButton = document.getElementById('subtitlePreviewButton');
    var subtitles = []; // Array to store subtitles with timestamps

    // Event listener for subtitle preview button click
    subtitlePreviewButton.addEventListener("click", function () {
        // Reset video playback to start from the beginning
        videoPlayer.currentTime = 0;
        videoPlayer.play();

        // Get the translated text from the textarea
        var translatedText = document.getElementById('translatedTextField').value;

        // Split the translated text into lines
        var lines = translatedText.split('\n');

        // Format the lines into a single line with commas
        var formattedTranslatedText = lines.join(', ');

        // Split the formatted text into subtitles
        subtitles = formattedTranslatedText.split(', ');

        // Display subtitles
        displaySubtitles();
    });

    // Function to display subtitles
    function displaySubtitles() {
        subtitleDisplay.innerHTML = ''; // Clear previous subtitles

        subtitles.forEach(function (subtitle, index) {
            setTimeout(function () {
                subtitleDisplay.textContent = subtitle;
            }, index * 5000); // Display each subtitle for 5 seconds
        });
    }
});