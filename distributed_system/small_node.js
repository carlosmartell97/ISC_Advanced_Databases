/* WebRTC Demo
 * Allows two clients to connect via WebRTC with Data Channels
 * Uses Firebase as a signalling server
 * http://fosterelli.co/getting-started-with-webrtc-data-channels
 */

/* == Announcement Channel Functions ==
 * The 'announcement channel' allows clients to find each other on Firebase
 * These functions are for communicating through the announcement channel
 * This is part of the signalling server mechanism
 *
 * After two clients find each other on the announcement channel, they
 * can directly send messages to each other to negotiate a WebRTC connection
 */

// Announce our arrival to the announcement channel
var sendAnnounceChannelMessage = function(key) {
//  announceChannel.remove(function() {
    announceChannel.push({
      sharedKey : sharedKey,
      id : id
    });
    console.log('Announced our sharedKey is ' + sharedKey);
    console.log('Announced our ID is ' + id);
    document.getElementById('id').innerHTML = id;
    document.getElementById('key').innerHTML = sharedKey;
//  });
};

// Handle an incoming message on the announcement channel
var handleAnnounceChannelMessage = function(snapshot) {
  var message = snapshot.val();
  if (message.id != id && message.sharedKey == sharedKey) {
    console.log('Discovered matching announcement from ' + message.id);
    remote = message.id;
    initiateWebRTCState();
    connect();
  }
};

/* == Signal Channel Functions ==
 * The signal channels are used to delegate the WebRTC connection between
 * two peers once they have found each other via the announcement channel.
 *
 * This is done on Firebase as well. Once the two peers communicate the
 * necessary information to 'find' each other via WebRTC, the signalling
 * channel is no longer used and the connection becomes peer-to-peer.
 */

// Send a message to the remote client via Firebase
var sendSignalChannelMessage = function(message) {
  message.sender = id;
  database.child('messages').child(remote).push(message);
};

// Handle a WebRTC offer request from a remote client
var handleOfferSignal = function(message) {
  running = true;
  remote = message.sender;
  initiateWebRTCState();
  startSendingCandidates();
  peerConnection.setRemoteDescription(new RTCSessionDescription(message));
  peerConnection.createAnswer(function(sessionDescription) {
    console.log('Sending answer to ' + message.sender);
    peerConnection.setLocalDescription(sessionDescription);
    sendSignalChannelMessage(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};

// Handle a WebRTC answer response to our offer we gave the remote client
var handleAnswerSignal = function(message) {
  peerConnection.setRemoteDescription(new RTCSessionDescription(message));
};

// Handle an ICE candidate notification from the remote client
var handleCandidateSignal = function(message) {
  var candidate = new RTCIceCandidate(message);
  peerConnection.addIceCandidate(candidate);
};

// This is the general handler for a message from our remote client
// Determine what type of message it is, and call the appropriate handler
var handleSignalChannelMessage = function(snapshot) {
  var message = snapshot.val();
  var sender = message.sender;
  var type = message.type;
  console.log('Recieved a \'' + type + '\' signal from ' + sender);
    document.getElementById('incomingId').innerHTML = sender;
  if (type == 'offer') handleOfferSignal(message);
  else if (type == 'answer') handleAnswerSignal(message);
  else if (type == 'candidate' && running) handleCandidateSignal(message);
};

/* == ICE Candidate Functions ==
 * ICE candidates are what will connect the two peers
 * Both peers must find a list of suitable candidates and exchange their list
 * We exchange this list over the signalling channel (Firebase)
 */

// Add listener functions to ICE Candidate events
var startSendingCandidates = function() {
  peerConnection.oniceconnectionstatechange = handleICEConnectionStateChange;
  peerConnection.onicecandidate = handleICECandidate;
};

// This is how we determine when the WebRTC connection has ended
// This is most likely because the other peer left the page
var handleICEConnectionStateChange = function() {
  if (peerConnection.iceConnectionState == 'disconnected') {
    console.log('Client disconnected!');
    sendAnnounceChannelMessage(sharedKey);
  }
};

// Handle ICE Candidate events by sending them to our remote
// Send the ICE Candidates via the signal channel
var handleICECandidate = function(event) {
  var candidate = event.candidate;
  if (candidate) {
    candidate = candidate.toJSON();
    candidate.type = 'candidate';
    console.log('Sending candidate to ' + remote);
    sendSignalChannelMessage(candidate);
  } else {
    console.log('All candidates sent');
  }
};

/* == Data Channel Functions ==
 * The WebRTC connection is established by the time these functions run
 * The hard part is over, and these are the functions we really want to use
 *
 * The functions below relate to sending and receiving WebRTC messages over
 * the peer-to-peer data channels
 */

// This is our receiving data channel event
// We receive this channel when our peer opens a sending channel
// We will bind to trigger a handler when an incoming message happens
var handleDataChannel = function(event) {
  event.channel.onmessage = handleDataChannelMessage;
};

// This is called on an incoming message from our peer
// You probably want to overwrite this to do something more useful!
var handleDataChannelMessage = function(event) {
    var message = ""+event.data;
    var argument = message.slice(0,1);
    if(argument=='1' || argument=='2' || argument=='3'){
        console.log('Recieved Message: ' + message+' Argument:'+argument);
        window['part'+argument] = message.slice(1,message.length);
        document.getElementById('part'+message.slice(0,1)).innerHTML = message.slice(1,message.length);
    }
    else if(argument=='f'){
        dataChannel.send(message.slice(1,2)+window['part'+message.slice(1,2)]);
    }
};

// This is called when the WebRTC sending data channel is offically 'open'
var handleDataChannelOpen = function() {
  console.log('Data channel created!');
  dataChannel.send('Hello! I am ' + id);
};

// Called when the data channel has closed
var handleDataChannelClosed = function() {
  console.log('The data channel has been closed!');
};

// Function to offer to start a WebRTC connection with a peer
var connect = function() {
  running = true;
  startSendingCandidates();
  peerConnection.createOffer(function(sessionDescription) {
    console.log('Sending offer to ' + remote);
    peerConnection.setLocalDescription(sessionDescription);
    sendSignalChannelMessage(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};

// Function to initiate the WebRTC peerconnection and dataChannel
var initiateWebRTCState = function() {
  peerConnection = new webkitRTCPeerConnection(servers);
  peerConnection.ondatachannel = handleDataChannel;
  dataChannel = peerConnection.createDataChannel('myDataChannel');
  dataChannel.onmessage = handleDataChannelMessage;
  dataChannel.onopen = handleDataChannelOpen;
};

var id;              // Our unique ID
var sharedKey;       // Unique identifier for two clients to find each other
var remote;          // ID of the remote peer -- set once they send an offer
var peerConnection;  // This is our WebRTC connection
var dataChannel;     // This is our outgoing data channel within WebRTC
var running = false; // Keep track of our connection state
var part1, part2, part3;

// Use Google's public servers for STUN
// STUN is a component of the actual WebRTC connection
var servers = {
  iceServers: [ {
    url : 'stun:stun.l.google.com:19302'
  } ]
};

// Generate this browser a unique ID
// On Firebase peers use this unique ID to address messages to each other
// after they have found each other in the announcement channel
id = Math.random().toString().replace('.', '');

// Unique identifier for two clients to use
// They MUST share this to find each other
// Each peer waits in the announcement channel to find its matching identifier
// When it finds its matching identifier, it initiates a WebRTC offer with
// that client. This unique identifier can be pretty much anything in practice.
// Configure, connect, and set up Firebase
//sharedKey = prompt("Please enter a shared identifier");

// Fill this with the config in your Firebase dashboard
// You'll find it under "Add Firebase to your web app"
var config = {
//  apiKey: "AIzaSyDnL0UK9gexftWMirQscJW6OEfJlx2_JrA",
//  authDomain: "amber-fire-244.firebaseapp.com",
//  databaseURL: "https://amber-fire-244.firebaseio.com",
//  storageBucket: "",
//  messagingSenderId: "179120851804"
    apiKey: "AIzaSyDwqdXimd7NtDBzLac_tGc2J7v1L9lpI10",
    authDomain: "contrall-6af1a.firebaseapp.com",
    databaseURL: "https://contrall-6af1a.firebaseio.com",
    projectId: "contrall-6af1a",
    storageBucket: "contrall-6af1a.appspot.com",
    messagingSenderId: "101090883777"
};

// Setup database and channel events
var fb = firebase.initializeApp(config);
var database = fb.database().ref();
var announceChannel = database.child('announce');
var signalChannel = database.child('messages').child(id);
signalChannel.on('child_added', handleSignalChannelMessage);
announceChannel.on('child_added', handleAnnounceChannelMessage);

// Send a message to the announcement channel
// If our partner is already waiting, they will send us a WebRTC offer
// over our Firebase signalling channel and we can begin delegating WebRTC
//sendAnnounceChannelMessage();

//window.onload = function() {
////  document.getElementById('id').innerHTML = "mio";
//};

//function sendData(){
//    console.log('sendData() '+document.getElementById('sendText').value);
//    dataChannel.send(document.getElementById('sendText').value);
//}

function startCentralChannel(channelStart){
    sharedKey = document.getElementById('keyText').value;
    sendAnnounceChannelMessage(document.getElementById('keyText').value);
    console.log('startCentrallChannel() '+document.getElementById('keyText').value);
    dataChannel.send(channelStart);
    console.log('startMessage  '+channelStart);
}

function stopCentralChannel(channelStop){
    dataChannel.send(channelStop);
    console.log('stopCentrallChannel() '+channelStop);
}
