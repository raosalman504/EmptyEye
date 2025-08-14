const socket = io();
const notifList = document.getElementById('notification-list');
const notifSound = document.getElementById('notif-sound');

socket.on('notification', (data) => {
    console.log('Received notification:', data);
    const li = document.createElement('li');
    li.textContent = data.message;
    notifList.prepend(li);
    notifSound.play();
    // Browser push notification
    if (Notification.permission === 'granted') {
        new Notification('Empty Eye Alert', { body: data.message });
    }
});

window.onload = function() {
    // Request notification permission
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
    // Load notification history
    fetch('/notifications').then(res => res.json()).then(data => {
        notifList.innerHTML = '';
        data.forEach(n => {
            const li = document.createElement('li');
            li.textContent = n.message + ' (' + n.timestamp + ')';
            notifList.appendChild(li);
        });
    });
};

// Placeholder for video feed integration
// You will need to add code to display the live detection feed here.
