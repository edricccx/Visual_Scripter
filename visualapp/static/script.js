function uploadVideo() {
    var form = document.getElementById('videoForm');
    var input = document.getElementById('videoFile');
    var video = document.getElementById('videoPlayer');

    var file = input.files[0];
    var objectURL = URL.createObjectURL(file);

    video.src = objectURL;

    // Hide the form after uploading

}