let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

const recordBtn = document.getElementById('record-btn');

recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        if (!window.localTracks || localTracks.length < 2) {
            alert("Local media tracks are not available yet.");
            return;
        }

        const audioTrack = localTracks[0]?.getMediaStreamTrack();
        const videoTrack = localTracks[1]?.getMediaStreamTrack();

        if (!audioTrack || !videoTrack) {
            alert("Audio/Video tracks not ready.");
            return;
        }

        const stream = new MediaStream([videoTrack, audioTrack]);

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'video/webm;codecs=vp9,opus'
        });

        recordedChunks = [];

        mediaRecorder.ondataavailable = function (event) {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = function () {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            const formData = new FormData();
            formData.append('recording', blob, 'recording.webm');
            formData.append('meeting_id', window.MEETING_ID);
            formData.append('recorded_by', window.USER_ID);

            fetch('/upload-recording/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            })
            .then(res => res.json())
            .then(data => {
                alert('Recording saved.');
                console.log(data);
            })
            .catch(err => {
                console.error(err);
                alert('Upload failed.');
            });
        };

        mediaRecorder.start();
        isRecording = true;
        updateRecordBtn(true);

    } else {
        mediaRecorder.stop();
        isRecording = false;
        updateRecordBtn(false);
    }
});

function updateRecordBtn(active) {
    const svg = recordBtn.querySelector('svg');
    svg.style.fill = active ? 'red' : '#ede0e0';
}

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let c = cookie.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return '';
}
