const APP_ID = "fe63457742a44c6c8d4e851839c047cb"
//import AgoraRTM from '/js/agora-rtm-2.2.1.min.js';

let uid = sessionStorage.getItem('uid');
if (!uid) {
    uid = String(Math.floor(Math.random() * 10000));
    sessionStorage.setItem('uid', uid);
}

let token = null;
let client;

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
let roomId = urlParams.get('room');

if (!roomId) {
    roomId = 'main';
}
let displayName = sessionStorage.getItem('display_name');
if (!displayName) {
    window.location = 'lobby.html';
}
let localTracks = [];
let remoteUsers = {};
let localScreenTracks;
let sharingScreen = false;

let joinRoomInit = async () => {

    /*rtmClient = await AgoraRTM.createInstance(APP_ID);
    await rtmClient.login({uid, token});

    await rtmClient.addOrUpdateLocalUserAttributes({'name':displayName});

    channel = await rtmClient.createChannel(roomId);
    await channel.join();
    channel.on('MemberJoined', handleMemberJoined);
    channel.on('MemberLeft', handleMemberLeft);
    channel.on('ChannelMessage', handleChannelMessage);
    getMembers();
    addBotMessageToDom(`Welcome to the room ${displayName}`);*/

    client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
    if (!client) {
        console.error("Failed to create AgoraRTC client");
        return;
    }
    await client.join(APP_ID, roomId, token, uid);
    console.log("AgoraRTC client joined successfully");
    client.on('user-published', handleUserPublished);
    client.on('user-left', handleUserLeft);
    //joinStream();
}

let joinStream = async () => {
    document.getElementById('join-btn').style.display = 'none';
    document.getElementsByClassName('stream__actions')[0].style.display = 'flex';
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks({}, {
        encoderConfig: {
            width: { min: 640, ideal: 1920, max: 1920 },
            height: { min: 480, ideal: 1080, max: 1080 }
        }
    });
    let player = `<div class="video__container" id="user-container-${uid}">
                        <div class="video-player" id="user-${uid}"></div>
                  </div>`;
    document.getElementById('streams__container').insertAdjacentHTML('beforeend', player);
    document.getElementById(`user-container-${uid}`).addEventListener('click', expandVideoFrame);
    localTracks[1].play(`user-${uid}`);
    if (!client) {
        console.error("AgoraRTC client is not initialized.");
        return;
    }
    await client.publish([localTracks[0], localTracks[1]]);
}

let switchToCamera = async () => {
    let player = `<div class="video__container" id="user-container-${uid}">
                        <div class="video-player" id="user-${uid}"></div>
                  </div>`;
    displayFrame.insertAdjacentHTML('beforeend', player);
    await localTracks[0].setMuted(true);
    await localTracks[1].setMuted(true);
    document.getElementById('mic-btn').classList.remove('active');
    document.getElementById('screen-btn').classList.remove('active');

    localTracks[1].play(`user-${uid}`);
    await client.publish([localTracks[1]]);
}

let handleUserPublished = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await client.subscribe(user, mediaType);
    let player = document.getElementById(`user-container-${user.uid}`);
    if (player === null) {
        player = `<div class="video__container" id="user-container-${user.uid}">
                        <div class="video-player" id="user-${user.uid}"></div>
                  </div>`;
        document.getElementById('streams__container').insertAdjacentHTML('beforeend', player);
        document.getElementById(`user-container-${user.uid}`).addEventListener('click', expandVideoFrame);
    }

    if (displayFrame.style.display) {
        let videoFrame = document.getElementById(`user-container-${user.uid}`);
        videoFrame.style.height = '100px';
        videoFrame.style.width = '100px';
    }
    if (mediaType === 'video') {
        user.videoTrack.play(`user-${user.uid}`);
    }
    if (mediaType === 'audio') {
        user.audioTrack.play(`user-${user.uid}`);
    }
}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    let item = document.getElementById(`user-container-${user.uid}`);
    if (item) {
        item.remove();
    }
    if (userIdInDisplayFrame === `user-container-${user.uid}`) {
        displayFrame.style.display = null;
        let videoFrames = document.getElementsByClassName('video__container');
        for (let i = 0; videoFrames.length > i; i++) {
            videoFrames[i].style.height = '300px';
            videoFrames[i].style.width = '300px';
        }
    }
}

let toggleCamera = async (e) => {
    let button = e.currentTarget;
    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false);
        button.classList.add('active');
    }
    else {
        await localTracks[1].setMuted(true);
        button.classList.remove('active');
    }
}
document.getElementById('camera-btn').addEventListener('click', toggleCamera);

let toggleMic = async (e) => {
    let button = e.currentTarget;
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false);
        button.classList.add('active');
    }
    else {
        await localTracks[0].setMuted(true);
        button.classList.remove('active');
    }
}
document.getElementById('mic-btn').addEventListener('click', toggleMic);

let toggleScreen = async (e) => {
    let screenButton = e.currentTarget;
    let cameraButton = document.getElementById('camera-btn');
    if (!sharingScreen) {
        sharingScreen = true;
        screenButton.classList.add('active');
        cameraButton.classList.remove('active');
        cameraButton.style.display = 'none';

        localScreenTracks = await AgoraRTC.createScreenVideoTrack();
        document.getElementById(`user-container-${uid}`).remove();
        displayFrame.style.display = 'block';

        let player = `<div class="video__container" id="user-container-${uid}">
                        <div class="video-player" id="user-${uid}"></div>
                      </div>`;
        displayFrame.insertAdjacentHTML('beforeend', player);
        document.getElementById(`user-container-${uid}`).addEventListener('click', expandVideoFrame);
        userIdInDisplayFrame = `user-container-${uid}`;
        localScreenTracks.play(`user-${uid}`);

        await client.unpublish([localTracks[1]]);
        await client.publish([localScreenTracks]);

        let videoFrames = document.getElementsByClassName('video__container');
        for (let i = 0; videoFrames.length > i; i++) {
            if (videoFrames[i] != userIdInDisplayFrame) {
                videoFrames[i].style.height = '100px';
                videoFrames[i].style.width = '100px';
            }
        }
    }
    else {
        sharingScreen = false;
        cameraButton.style.display = 'block';
        document.getElementById(`user-container-${uid}`).remove();
        await client.unpublish([localScreenTracks]);
        switchToCamera();
    }
}

let leaveStream = async (e) => {
    e.preventDefault();
    document.getElementById('join-btn').style.display = 'block';
    document.getElementsByClassName('stream__actions')[0].style.display = 'none';

    for (let i = 0; localTracks.length > i; i++) {
        localTracks[i].stop();
        localTracks[i].close();
    }
    await client.unpublish([localTracks[0], localTracks[1]]);
    if (localScreenTracks) {
        await client.unpublish([localScreenTracks]);
    }
    document.getElementById(`user-container-${uid}`).remove();
    if (userIdInDisplayFrame === `user-container-${uid}`) {
        displayFrame.style.display = null;
        for (let i = 0; videoFrames.length > i; i++) {
            videoFrames[i].style.height = '300px';
            videoFrames[i].style.width = '300px';
        }
    }
    //channel.sendMessage({text:JSON.stringify({'type':'user_left','uid':uid})});
}

document.getElementById('screen-btn').addEventListener('click', toggleScreen);
document.getElementById('join-btn').addEventListener('click', joinStream);
document.getElementById('leave-btn').addEventListener('click', leaveStream);
joinRoomInit()


let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

const recordBtn = document.getElementById('record-btn');

recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        if (!localTracks || localTracks.length < 2) {
            alert("Local media tracks are not available yet. Click 'Join Stream' first.");
            return;
        }
        let mixedStream;
        try {
            console.log("🎬 Requesting screen recording...");
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: true,
                audio: true // Try to get system audio if available
            });

            // 2. Get mic stream separately
            const micStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: false
            });

            // 3. Combine video from screen + audio from mic
            // 3. Use Web Audio API to mix audio tracks properly
            const audioContext = new AudioContext();
            const destination = audioContext.createMediaStreamDestination();

            // Optional: Attach screen audio if available
            if (screenStream.getAudioTracks().length > 0) {
                const screenAudioSource = audioContext.createMediaStreamSource(screenStream);
                screenAudioSource.connect(destination);
            }

            // Attach mic audio
            if (micStream.getAudioTracks().length > 0) {
                const micAudioSource = audioContext.createMediaStreamSource(micStream);
                micAudioSource.connect(destination);
            }

            // Create final combined stream
            const combinedStream = new MediaStream();

            // Add screen video track(s)
            screenStream.getVideoTracks().forEach(track => combinedStream.addTrack(track));

            // Add mixed audio track (from the destination node)
            destination.stream.getAudioTracks().forEach(track => combinedStream.addTrack(track));

            mixedStream = combinedStream;


            console.log("✅ Screen recording started!", mixedStream);
        } catch (err) {
            alert("Screen recording permission denied.");
            return;
        }


        try {
            mediaRecorder = new MediaRecorder(mixedStream, {
                mimeType: 'video/webm;codecs=vp9,opus'
            });

            recordedChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) recordedChunks.push(event.data);
            };

            let hasUploaded = false;

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: 'video/webm' });
                const url = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `session_recording_${Date.now()}.webm`;
                document.body.appendChild(a);
                a.click();

                setTimeout(() => {
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 100);
            };


            mediaRecorder.start();
            isRecording = true;
            toggleRecordButton(true);
        } catch (err) {
            console.error("Recording error:", err);
            alert("Recording failed to start.");
        }

    } else {
        mediaRecorder.stop();
        isRecording = false;
        toggleRecordButton(false);
    }
});

function toggleRecordButton(active) {
    const icon = recordBtn.querySelector('svg');
    if (active) {
        icon.style.fill = 'red';
    } else {
        icon.style.fill = '#ede0e0';
    }
}

function getCSRFToken() {
    const name = 'csrftoken';
    const cookieArr = document.cookie.split(';');
    for (let cookie of cookieArr) {
        const c = cookie.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return null;
}