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
                const filename = artifact.filename;

                if (filename.match(/\.(jpg|jpeg|png|gif)$/i)) {
                    // Display images
                    const img = document.createElement("img");
                    img.src = fileUrl;
                    img.alt = filename;
                    img.classList.add("gallery-img");
                    artifactElement.appendChild(img);
                } else if (filename.match(/\.(mp3|wav|ogg)$/i)) {
                    // Display audio player
                    const audio = document.createElement("audio");
                    audio.controls = true;
                    const source = document.createElement("source");
                    source.src = fileUrl;
                    source.type = filename.endsWith(".mp3") ? "audio/mpeg" : "audio/ogg";
                    audio.appendChild(source);
                    artifactElement.appendChild(audio);
                } else {
                    // Display generic file download link
                    const fileLink = document.createElement("a");
                    fileLink.href = fileUrl;
                    fileLink.innerText = `Download ${filename}`;
                    fileLink.target = "_blank";
                    artifactElement.appendChild(fileLink);
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
