document.addEventListener("DOMContentLoaded", function () {
    const userUuid = document.getElementById("user-uuid").innerText;
    const gallery = document.getElementById("gallery");
    const downloadButton = document.getElementById("download-button");

    fetch(`/artifacts/${userUuid}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                gallery.innerHTML = `<p>${data.error}</p>`;
                downloadButton.style.display = "none";
                return;
            }

            data.forEach(artifact => {
                const artifactElement = document.createElement("div");
                artifactElement.classList.add("gallery-item");

                const fileUrl = artifact.file_url;
                const filename = artifact.filename.toLowerCase();

                // PNG or JPG Images
                if (filename.match(/\.(png|jpg|jpeg)$/)) {
                    const img = document.createElement("img");
                    img.src = fileUrl;
                    img.alt = filename;
                    img.classList.add("gallery-img");
                    artifactElement.appendChild(img);
                }

                // MP3 Audio
                else if (filename.endsWith(".mp3")) {
                    const audio = document.createElement("audio");
                    audio.controls = true;
                    const source = document.createElement("source");
                    source.src = fileUrl;
                    source.type = "audio/mpeg";
                    audio.appendChild(source);
                    artifactElement.appendChild(audio);
                }

                // MP4 Video
                else if (filename.endsWith(".mp4")) {
                    const video = document.createElement("video");
                    video.controls = true;
                    video.width = 200;
                    const source = document.createElement("source");
                    source.src = fileUrl;
                    source.type = "video/mp4";
                    video.appendChild(source);
                    artifactElement.appendChild(video);
                }

                // Skip all other file types
                else {
                    return;
                }

                gallery.appendChild(artifactElement);
            });
        })
        .catch(error => {
            console.error("Error fetching artifacts:", error);
        });

    downloadButton.addEventListener("click", function () {
        window.location.href = `/artifacts/download/${userUuid}`;
    });
});
