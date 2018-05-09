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
var sendAnnounceChannelMessageA = function(key) {
//  announceChannel.remove(function() {
    announceChannel.push({
      sharedKey : sharedKeyA,
      id : id
    });
    console.log('Announced our sharedKey is ' + sharedKeyA);
    console.log('Announced our ID is ' + id);
    document.getElementById('idA').innerHTML = id;
    document.getElementById('keyA').innerHTML = sharedKeyA;
//  });
};
var sendAnnounceChannelMessageB = function(key) {
//  announceChannel.remove(function() {
    announceChannel.push({
      sharedKey : sharedKeyB,
      id : id
    });
    console.log('Announced our sharedKey is ' + sharedKeyB);
    console.log('Announced our ID is ' + id);
    document.getElementById('idB').innerHTML = id;
    document.getElementById('keyB').innerHTML = sharedKeyB;
//  });
};
var sendAnnounceChannelMessageC = function(key) {
//  announceChannel.remove(function() {
    announceChannel.push({
      sharedKey : sharedKeyC,
      id : id
    });
    console.log('Announced our sharedKey is ' + sharedKeyC);
    console.log('Announced our ID is ' + id);
    document.getElementById('idC').innerHTML = id;
    document.getElementById('keyC').innerHTML = sharedKeyC;
//  });
};

// Handle an incoming message on the announcement channel
var handleAnnounceChannelMessage = function(snapshot) {
  var message = snapshot.val();
  if (message.id != id && message.sharedKey == sharedKeyA) {
    console.log('FIRST m.id='+message.id+' id:'+id+' m.sk:'+message.shareKey+' skA:'+sharedKeyA+' skB:'+sharedKeyB+' skC:'+sharedKeyC);
    console.log('Discovered matching announcement from ' + message.id);
    remoteA = message.id;
    initiateWebRTCState('myDataChannelA');
    connectA();
  }
  else if (message.id != id && message.sharedKey == sharedKeyB) {
      console.log('SECOND m.id='+message.id+' id:'+id+' m.sk:'+message.shareKey+' skA:'+sharedKeyA+' skB:'+sharedKeyB+' skC:'+sharedKeyC);
    console.log('Discovered matching announcement from ' + message.id);
    remoteB = message.id;
    initiateWebRTCState('myDataChannelB');
    connectB();
  }
  else if (message.id != id && message.sharedKey == sharedKeyC) {
      console.log('THIRD m.id='+message.id+' id:'+id+' m.sk:'+message.shareKey+' skA:'+sharedKeyA+' skB:'+sharedKeyB+' skC:'+sharedKeyC);
    console.log('Discovered matching announcement from ' + message.id);
    remoteC = message.id;
    initiateWebRTCState('myDataChannelC');
    connectC();
  }
  else {
      console.log('NOPE m.id='+message.id+' id:'+id+' m.sk:'+message.shareKey+' skA:'+sharedKeyA+' skB:'+sharedKeyB+' skC:'+sharedKeyC);
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
var sendSignalChannelMessageA = function(message) {
  message.sender = id;
  database.child('messages').child(remoteA).push(message);
};
var sendSignalChannelMessageB = function(message) {
  message.sender = id;
  database.child('messages').child(remoteB).push(message);
};
var sendSignalChannelMessageC = function(message) {
  message.sender = id;
  database.child('messages').child(remoteC).push(message);
};

// Handle a WebRTC offer request from a remote client
var handleOfferSignalA = function(message) {
  running = true;
  remote = message.sender;
  initiateWebRTCState('myDataChannelA');
    console.log('sender:'+message.sender);
  startSendingCandidatesA();
  peerConnectionA.setRemoteDescription(new RTCSessionDescription(message));
  peerConnectionA.createAnswer(function(sessionDescription) {
    console.log('Sending answer to ' + message.sender);
    peerConnectionA.setLocalDescription(sessionDescription);
    sendSignalChannelMessageA(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};
var handleOfferSignalB = function(message) {
  running = true;
  remote = message.sender;
  initiateWebRTCState('myDataChannelB');
  startSendingCandidatesB();
  peerConnectionB.setRemoteDescription(new RTCSessionDescription(message));
  peerConnectionB.createAnswer(function(sessionDescription) {
    console.log('Sending answer to ' + message.sender);
    peerConnectionB.setLocalDescription(sessionDescription);
    sendSignalChannelMessageB(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};
var handleOfferSignalC = function(message) {
  running = true;
  remote = message.sender;
  initiateWebRTCState('myDataChannelC');
  startSendingCandidatesC();
  peerConnectionC.setRemoteDescription(new RTCSessionDescription(message));
  peerConnectionC.createAnswer(function(sessionDescription) {
    console.log('Sending answer to ' + message.sender);
    peerConnectionC.setLocalDescription(sessionDescription);
    sendSignalChannelMessageC(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};

// Handle a WebRTC answer response to our offer we gave the remote client
var handleAnswerSignalA = function(message) {
  peerConnectionA.setRemoteDescription(new RTCSessionDescription(message));
};
var handleAnswerSignalB = function(message) {
  peerConnectionB.setRemoteDescription(new RTCSessionDescription(message));
};
var handleAnswerSignalC = function(message) {
  peerConnectionC.setRemoteDescription(new RTCSessionDescription(message));
};

// Handle an ICE candidate notification from the remote client
var handleCandidateSignalA = function(message) {
  var candidateA = new RTCIceCandidate(message);
  peerConnectionA.addIceCandidate(candidateA);
};
var handleCandidateSignalB = function(message) {
  var candidateB = new RTCIceCandidate(message);
  peerConnectionB.addIceCandidate(candidateB);
};
var handleCandidateSignalC = function(message) {
  var candidateC = new RTCIceCandidate(message);
  peerConnectionC.addIceCandidate(candidateC);
};

// This is the general handler for a message from our remote client
// Determine what type of message it is, and call the appropriate handler
var handleSignalChannelMessageA = function(snapshot) {
  var message = snapshot.val();
  var sender = message.sender;
  var type = message.type;
  console.log('Recieved a \'' + type + '\' signal from ' + sender);
    document.getElementById('incomingIdA').innerHTML = sender;
  if (type == 'offer') handleOfferSignalA(message);
  else if (type == 'answer') handleAnswerSignalA(message);
  else if (type == 'candidate' && running) handleCandidateSignalA(message);
};
var handleSignalChannelMessageB = function(snapshot) {
  var message = snapshot.val();
  var sender = message.sender;
  var type = message.type;
  console.log('Recieved a \'' + type + '\' signal from ' + sender);
    document.getElementById('incomingIdB').innerHTML = sender;
  if (type == 'offer') handleOfferSignalB(message);
  else if (type == 'answer') handleAnswerSignalB(message);
  else if (type == 'candidate' && running) handleCandidateSignalB(message);
};
var handleSignalChannelMessageC = function(snapshot) {
  var message = snapshot.val();
  var sender = message.sender;
  var type = message.type;
  console.log('Recieved a \'' + type + '\' signal from ' + sender);
    document.getElementById('incomingIdC').innerHTML = sender;
  if (type == 'offer') handleOfferSignalC(message);
  else if (type == 'answer') handleAnswerSignalC(message);
  else if (type == 'candidate' && running) handleCandidateSignalC(message);
};

/* == ICE Candidate Functions ==
 * ICE candidates are what will connect the two peers
 * Both peers must find a list of suitable candidates and exchange their list
 * We exchange this list over the signalling channel (Firebase)
 */

// Add listener functions to ICE Candidate events
var startSendingCandidatesA = function() {
  peerConnectionA.oniceconnectionstatechange = handleICEConnectionStateChange;
  peerConnectionA.onicecandidate = handleICECandidateA;
};
var startSendingCandidatesB = function() {
  peerConnectionB.oniceconnectionstatechange = handleICEConnectionStateChange;
  peerConnectionB.onicecandidate = handleICECandidateB;
};
var startSendingCandidatesC = function() {
  peerConnectionC.oniceconnectionstatechange = handleICEConnectionStateChange;
  peerConnectionC.onicecandidate = handleICECandidateC;
};

// This is how we determine when the WebRTC connection has ended
// This is most likely because the other peer left the page
var handleICEConnectionStateChange = function() {
  if (peerConnectionA.iceConnectionState == 'disconnected') {
    console.log('Node A disconnected!');
    document.getElementById('aStatus').innerHTML = 'DORMANT';
    statusChannelA = false;
  }
  if (peerConnectionB.iceConnectionState == 'disconnected') {
    console.log('Node B disconnected!');
    document.getElementById('bStatus').innerHTML = 'DORMANT';
    statusChannelB = false;
  }
  if (peerConnectionC.iceConnectionState == 'disconnected') {
    console.log('Node C disconnected!');
    document.getElementById('cStatus').innerHTML = 'DORMANT';
    statusChannelC = false;
  }
};

// Handle ICE Candidate events by sending them to our remote
// Send the ICE Candidates via the signal channel
var handleICECandidateA = function(event) {
  var candidate = event.candidate;
  if (candidate) {
    candidate = candidate.toJSON();
    candidate.type = 'candidate';
    console.log('Sending candidate to ' + remoteA);
    sendSignalChannelMessageA(candidate);
  } else {
    console.log('All candidates sent');
  }
};
var handleICECandidateB = function(event) {
  var candidate = event.candidate;
  if (candidate) {
    candidate = candidate.toJSON();
    candidate.type = 'candidate';
    console.log('Sending candidate to ' + remoteB);
    sendSignalChannelMessageB(candidate);
  } else {
    console.log('All candidates sent');
  }
};
var handleICECandidateC = function(event) {
  var candidate = event.candidate;
  if (candidate) {
    candidate = candidate.toJSON();
    candidate.type = 'candidate';
    console.log('Sending candidate to ' + remoteC);
    sendSignalChannelMessageC(candidate);
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
var handleDataChannelA = function(event) {
  event.channel.onmessage = handleDataChannelMessageA;
};
var handleDataChannelB = function(event) {
  event.channel.onmessage = handleDataChannelMessageB;
};
var handleDataChannelC = function(event) {
  event.channel.onmessage = handleDataChannelMessageC;
};

// This is called on an incoming message from our peer
// You probably want to overwrite this to do something more useful!
var handleDataChannelMessageA = function(event) {
    var message = event.data;
    console.log('Recieved Message from A: ' + message);
    if(message=="StopA"){
        document.getElementById('aStatus').innerHTML = 'DORMANT';
        statusChannelA = false;
    }
    else if (message=="StartA") {
      document.getElementById('aStatus').innerHTML = 'ACTIVE';
      statusChannelA = true;
    }
    else {
        var argument = message.slice(0,1);
        window['part'+argument] = message.slice(1,message.length);
        document.getElementById('part'+argument).innerHTML = window['part'+argument];
        document.getElementById('fetchText').value = part1+part2+part3;
//       document.getElementById('incomingTextA').value = event.data;
    }
//  document.write(event.data + '<br />');
};
var handleDataChannelMessageB = function(event) {
    var message = event.data;
    console.log('Recieved Message from B: ' + message);
    if(message=="StopB"){
       document.getElementById('bStatus').innerHTML = 'DORMANT';
        statusChannelB = false;
    }
    else if (message=="StartB") {
      document.getElementById('bStatus').innerHTML = 'ACTIVE';
      statusChannelB = true;
    }
    else {
        var argument = message.slice(0,1);
        window['part'+argument] = message.slice(1,message.length);
        document.getElementById('part'+argument).innerHTML = window['part'+argument];
        document.getElementById('fetchText').value = part1+part2+part3;
//       document.getElementById('incomingTextB').value = event.data;
    }
//  document.write(event.data + '<br />');
};
var handleDataChannelMessageC = function(event) {
    var message = event.data;
    console.log('Recieved Message from C: ' + message);
    if(message=="StopC"){
        document.getElementById('cStatus').innerHTML = 'DORMANT';
        statusChannelC = false;
    }
    else if (message=="StartC") {
      document.getElementById('cStatus').innerHTML = 'ACTIVE';
      statusChannelC = true;
    }
    else {
        var argument = message.slice(0,1);
        window['part'+argument] = message.slice(1,message.length);
        document.getElementById('part'+argument).innerHTML = window['part'+argument];
        document.getElementById('fetchText').value = part1+part2+part3;
//       document.getElementById('incomingTextC').value = event.data;
    }
//  document.write(event.data + '<br />');
};

// This is called when the WebRTC sending data channel is offically 'open'
var handleDataChannelOpenA = function() {
  console.log('Data channel A created!');
  dataChannelA.send('Hello! I am ' + id);
};
var handleDataChannelOpenB = function() {
  console.log('Data channel B created!');
  dataChannelB.send('Hello! I am ' + id);
};
var handleDataChannelOpenC = function() {
  console.log('Data channel C created!');
  dataChannelC.send('Hello! I am ' + id);
};

// Called when the data channel has closed
var handleDataChannelClosed = function() {
  console.log('The data channel has been closed!');
};

// Function to offer to start a WebRTC connection with a peer
var connectA = function() {
  running = true;
  startSendingCandidatesA();
  peerConnectionA.createOffer(function(sessionDescription) {
    console.log('Sending offer to ' + remoteA);
    peerConnectionA.setLocalDescription(sessionDescription);
    sendSignalChannelMessageA(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};
var connectB = function() {
  running = true;
  startSendingCandidatesB();
  peerConnectionB.createOffer(function(sessionDescription) {
    console.log('Sending offer to ' + remoteB);
    peerConnectionB.setLocalDescription(sessionDescription);
    sendSignalChannelMessageB(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};
var connectC = function() {
  running = true;
  startSendingCandidatesC();
  peerConnectionC.createOffer(function(sessionDescription) {
    console.log('Sending offer to ' + remoteB);
    peerConnectionC.setLocalDescription(sessionDescription);
    sendSignalChannelMessageC(sessionDescription.toJSON());
  }, function(err) {
    console.error('Could not create offer', err);
  });
};

// Function to initiate the WebRTC peerconnection and dataChannel
var initiateWebRTCState = function(channel) {
  if(channel=='myDataChannelA'){
     peerConnectionA = new webkitRTCPeerConnection(servers);
     peerConnectionA.ondatachannel = handleDataChannelA;
     dataChannelA = peerConnectionA.createDataChannel(channel);
     dataChannelA.onmessage = handleDataChannelMessageA;
     dataChannelA.onopen = handleDataChannelOpenA;
  }
else if(channel=='myDataChannelB'){
     peerConnectionB = new webkitRTCPeerConnection(servers);
     peerConnectionB.ondatachannel = handleDataChannelB;
     dataChannelB = peerConnectionB.createDataChannel(channel);
     dataChannelB.onmessage = handleDataChannelMessageB;
     dataChannelB.onopen = handleDataChannelOpenB;
  }
else if(channel=='myDataChannelC'){
     peerConnectionC = new webkitRTCPeerConnection(servers);
     peerConnectionC.ondatachannel = handleDataChannelC;
     dataChannelC = peerConnectionC.createDataChannel(channel);
     dataChannelC.onmessage = handleDataChannelMessageC;
     dataChannelC.onopen = handleDataChannelOpenC;
  } else {
      console.log("NONE:"+channel);
  }
};

var id;              // Our unique ID
var sharedKeyA;       // Unique identifier for two clients to find each other
var sharedKeyB;       // Unique identifier for two clients to find each other
var sharedKeyC;       // Unique identifier for two clients to find each other
var remoteA;          // ID of the remote peer -- set once they send an offer
var remoteB;          // ID of the remote peer -- set once they send an offer
var remoteC;          // ID of the remote peer -- set once they send an offer
var peerConnectionA;  // This is our WebRTC connection
var peerConnectionB;  // This is our WebRTC connection
var peerConnectionC;  // This is our WebRTC connection
var dataChannelA;     // This is our outgoing data channel within WebRTC
var dataChannelB;     // This is our outgoing data channel within WebRTC
var dataChannelC;     // This is our outgoing data channel within WebRTC
var statusChannelA = false;
var statusChannelB = false;
var statusChannelC = false;
var running = false; // Keep track of our connection state
var part1="", part2="", part3="";

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
signalChannel.on('child_added', handleSignalChannelMessageA);
signalChannel.on('child_added', handleSignalChannelMessageB);
signalChannel.on('child_added', handleSignalChannelMessageC);
announceChannel.on('child_added', handleAnnounceChannelMessage);

// Send a message to the announcement channel
// If our partner is already waiting, they will send us a WebRTC offer
// over our Firebase signalling channel and we can begin delegating WebRTC
//sendAnnounceChannelMessage();

//window.onload = function() {
////  document.getElementById('id').innerHTML = "mio";
//};

function sendDataA(message){
    console.log('sendData()A '+message);
    if(statusChannelA){
       dataChannelA.send(message);
    }
}
function sendDataB(message){
    console.log('sendData()B '+message);
    if(statusChannelB){
        dataChannelB.send(message);
    }
}
function sendDataC(message){
    console.log('sendData()C '+message);
    if(statusChannelC){
        dataChannelC.send(message);
    }
}

function startChannelA(message){
    sharedKeyA = document.getElementById('keyTextA').value;
    sendAnnounceChannelMessageA(document.getElementById('keyTextA').value);
    //document.getElementById('aStatus').innerHTML = 'ACTIVE';
    //statusChannelA = true;
    console.log('startChannelA() '+document.getElementById('keyTextA').value);
}
function startChannelB(message){
    sharedKeyB = document.getElementById('keyTextB').value;
    sendAnnounceChannelMessageB(document.getElementById('keyTextB').value);
    //document.getElementById('bStatus').innerHTML = 'ACTIVE';
    //statusChannelB = true;
    console.log('startChannelB() '+document.getElementById('keyTextB').value);
}
function startChannelC(message){
    sharedKeyC = document.getElementById('keyTextC').value;
    sendAnnounceChannelMessageC(document.getElementById('keyTextC').value);
    //document.getElementById('cStatus').innerHTML = 'ACTIVE';
    //statusChannelC = true;
    console.log('startChannelC() '+document.getElementById('keyTextC').value);
}

function sendData(){
  var text = document.getElementById("sendText").value;
  var size = text.length;
  var segment1size = 0;
  var segmentsize = 0;

  //Para definir los tamaños de division, si es o no divisible entre 3
  if (size%3 == 0){
  	segmentsize = size/3;
    segment1size = segmentsize;
  } else {
    segmentsize = size/3;
    segment1size = segmentsize + size%3;
  }

  //dividir el texto segun los tamaños de segmento
  var text1 = text.slice(0,segment1size);
  var text2 = text.slice(segment1size, segment1size + segmentsize);
  var text3 = text.slice(segment1size+segmentsize, size);

  sendDataA('1'+text1);
  sendDataA('2'+text2);

  sendDataB('2'+text2);
  sendDataB('3'+text3);

  sendDataC('3'+text3);
  sendDataC('1'+text1);
}

function fetchData(){
  console.log("statusChannelA:"+statusChannelA);
  console.log("statusChannelB:"+statusChannelB);
  console.log("statusChannelC:"+statusChannelC);
  if(statusChannelA&&statusChannelB&&statusChannelC){
   //todos los nodos sirven
   sendDataA('f1');
   sendDataB('f2');
   sendDataC('f3');
  } else if (statusChannelA&&statusChannelB|| statusChannelA&&statusChannelC){
   if(statusChannelB){
     //el nodo A y B sirven
     sendDataA('f1');
     sendDataA('f2');
     sendDataB('f3');
    } else {
     //el nodo A y C sirven
     sendDataC('f1');
     sendDataA('f2');
     sendDataC('f3');
   }
  } else if (statusChannelB&&statusChannelC){
   //el nodo B y C sirven
   sendDataC('f1');
   sendDataB('f2');
   sendDataB('f3');
  } else if (statusChannelA || statusChannelB || statusChannelC ){
   if(statusChannelA){
     //solo el nodo A sirve
     sendDataA('f1');
     sendDataA('f2');
     sendDataA('f3');
   } else if(statusChannelB) {
     //solo el nodo B sirve
     sendDataB('f1');
     sendDataB('f2');
     sendDataB('f3');
   } else {
     //solo el nodo C sirve
     sendDataC('f1');
     sendDataC('f2');
     sendDataC('f3');
   }
  } else {
   //ningun nodo sirve
   document.getElementById('fetchText').value = "ningun nodo esta conectado";
  }
}
