document.addEventListener("DOMContentLoaded", () => {
/*document.getElementById('lobby__form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    let meetingId = document.getElementById('meeting_id').value;
    let name = document.getElementById('name').value;
    let roomPassword = document.getElementById('room_password').value;

    if (!meetingId || !name || !roomPassword) {
        alert("Please fill in all fields!");
        return;
    }

    let roomURL = `/conference_meeting/lobby/room/${meetingId}?meeting_id=${meetingId}&name=${encodeURIComponent(name)}&room_password=${encodeURIComponent(roomPassword)}`;

    window.location.href = roomURL; // Redirect correctly
});

let form = document.getElementById('lobby__form');

let displayName = sessionStorage.getItem('display_name');

if(displayName) {
    form.name.value = displayName;
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    sessionStorage.setItem('display_name', e.target.name.value);
    let inviteCode = e.target.room_password.value;
    if(!inviteCode) {
        inviteCode = String(Math.floor(Math.random()*10000));
    }
    //window.history.replaceState({},'','/conference_meeting/');
    window.location.href = `${window.location.origin}/conference_meeting/lobby/room/?room=${inviteCode}`;
    //window.location.replace("/conference_meeting/lobby/room/?room=" + inviteCode);

})*/


let form = document.getElementById('lobby__form');

let displayName = sessionStorage.getItem('display_name');

if(displayName) {
    form.name.value = displayName;
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    sessionStorage.setItem('display_name', e.target.name.value);
    let inviteCode = e.target.room_password.value;
    if(!inviteCode) {
        inviteCode = String(Math.floor(Math.random()*10000));
    }
    let secretKey = CryptoJS.enc.Utf8.parse("your-secret-key");
    let iv = CryptoJS.enc.Utf8.parse("1234567890123456");
    let encrypted = CryptoJS.AES.encrypt(inviteCode, secretKey, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    }).toString();
    let encoded = encrypted.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    window.location = `room/?room=${encodeURIComponent(encoded)}`;
});
});
