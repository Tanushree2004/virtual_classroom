const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
let encryptedRoomId = urlParams.get('room');

encryptedRoomId = decodeURIComponent(encryptedRoomId);
let secretKey = CryptoJS.enc.Utf8.parse("your-secret-key");
let iv = CryptoJS.enc.Utf8.parse("1234567890123456");
let decrypted = CryptoJS.AES.decrypt(encryptedRoomId, secretKey, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
});
let roomId = decrypted.toString(CryptoJS.enc.Utf8)
// WebSocket connection for managing participants and messages
//let participantSocket = new WebSocket(`ws://${window.location.host}/ws/conference_meeting/${roomId}/`);
let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let participantSocket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/conference_meeting/${roomId}/`);

let participantDisplayName = sessionStorage.getItem('display_name');
if (!participantDisplayName) {
    window.location = 'lobby.html';
}

/*let uid = sessionStorage.getItem('uid');
if (!uid){
    uid = String(Math.floor(Math.random()*10000));
    sessionStorage.setItem('uid', uid);
}*/

let addParticipantToDom = (username) => {
    let membersWrapper = document.getElementById('members__list');
    if (document.getElementById(`member__${username}__wrapper`)) {
        return; 
    }
    let memberItem = `<div class="member__wrapper" id="member__${username}__wrapper">
                        <span class="green__icon"></span>
                        <p class="member_name">${username}</p>
                      </div>`;
    membersWrapper.insertAdjacentHTML('beforeend', memberItem);
    updateParticipantTotal();
};

let removeParticipantFromDom = (username) => {
    let memberWrapper = document.getElementById(`member__${username}__wrapper`);
    if (memberWrapper) {
        let name =  memberWrapper.getElementsByClassName('member_name')[0].textContent;
        addBotMessageToDom(`${name} has left.`)
        memberWrapper.remove();
    }
};

let updateParticipantTotal = () => {
    let total = document.getElementById('members__count');
    let members = document.querySelectorAll('.member__wrapper');
    total.innerText = members.length;
};

// WebSocket Event Handlers
participantSocket.onopen = () => {
    console.log("WebSocket for participants connected!");
    participantSocket.send(JSON.stringify({
        type: "join",
        username: participantDisplayName
    }));
    setTimeout(() => {
        participantSocket.send(JSON.stringify({ type: "get_participants" }));
    }, 1000);
};

participantSocket.onmessage = (event) => {
    console.log("Received Websocket message:", event.data);
    const data = JSON.parse(event.data);

    if (data.type === "participant_list") {
        console.log("Received participant list:", data.participants);
        let membersWrapper = document.getElementById('members__list');
        membersWrapper.innerHTML = ''; // Clear the existing list
        data.participants.forEach(username => addParticipantToDom(username));
        updateParticipantTotal();
    }
    if (data.type === "user_joined") {
        console.log("adding participant:", data.username);
        addParticipantToDom(data.username);
        addBotMessageToDom(`${data.username} has joined the meeting.`);
        updateParticipantTotal();
    } 
    else if (data.type === "user_left") {
        removeParticipantFromDom(data.username);
        addBotMessageToDom(`${data.username} has left the meeting.`);
        updateParticipantTotal();
    } 
    else if (data.type === "chat") {
        console.log("Chat message received from:", data.username, "Message:", data.message);
        addMessageToDom(data.username, data.message);
    }
     
};

participantSocket.onclose = () => {
    console.log("WebSocket for participants disconnected.");
};

// Sending Chat Messages
let sendMessage = (e) => {
    e.preventDefault();
    let messageInput = e.target.message;
    let message = messageInput.value.trim();
    if(!message) return;
    let chatMessage = JSON.stringify({
        type: "chat",
        username: participantDisplayName,
        message: message
    });
    console.log("Sending request for:", participantDisplayName);
    participantSocket.send(chatMessage);
    //addMessageToDom(participantDisplayName, message);
    e.target.reset();
    //messageInput.value = "";
};

// Function to add messages to the DOM
let addMessageToDom = (name, message) => {
    let messagesWrapper = document.getElementById('messages');
    let newMessage = `<div class="message__wrapper">
                        <div class="message__body">
                            <strong class="message__author">${name}</strong>
                            <p class="message__text">${message}</p>
                        </div>
                      </div>`;
    messagesWrapper.insertAdjacentHTML('beforeend', newMessage);
    let lastMessage = document.querySelector('#messages .message__wrapper:last-child');
    if (lastMessage) {
        lastMessage.scrollIntoView();
    }
};

// Function to handle bot messages
let addBotMessageToDom = (botMessage) => {
    let messagesWrapper = document.getElementById('messages');
    let newMessage = `<div class="message__wrapper">
                        <div class="message__body__bot">
                            <strong class="message__author__bot">🤖 Mumble Bot</strong>
                            <p class="message__text__bot">${botMessage}</p>
                        </div>
                      </div>`;
    messagesWrapper.insertAdjacentHTML('beforeend', newMessage);
    let lastMessage = document.querySelector('#messages .message__wrapper:last-child');
    if (lastMessage) {
        lastMessage.scrollIntoView();
    }
};

// Event listener for message form submission
let messageForm = document.getElementById('message__form');
messageForm.addEventListener('submit', sendMessage);

// Handling leave action
let leaveRoom = () => {
    participantSocket.send(JSON.stringify({
        type: "leave",
        username: participantDisplayName
    }));
    window.location = 'lobby.html';
};

window.addEventListener('beforeunload', leaveRoom);

// To load participants when the room is joined
let loadParticipants = () => {
    participantSocket.send(JSON.stringify({ type: "get_participants" }));
    updateParticipantTotal();
};
