//saved responses
var responses = [
    "Hey",
    "Sure"
];
//tracks number of messages sent by user to know which response to send
var messageCount = 0;

//function to add message to message box based on type of user
function addMessage(message, type) {
    var chatBox = document.getElementById("chatBox");
    var messageDiv = document.createElement("div");
    messageDiv.textContent = message;
    //adds the messages to list
    messageDiv.classList.add("message");
    if (type === "user") {
        messageDiv.classList.add("userMessage");
    } else {
        messageDiv.classList.add("responseMessage");
    }
    //appends message to end
    chatBox.appendChild(messageDiv);
    //automatically scrolls to bottom of messages if needed
    chatBox.scrollTop = chatBox.scrollHeight;
}

//function to get the message sent by user or bot response
function sendMessage() {
    var userInput = document.getElementById("messageInput").value;
    addMessage(userInput, "user");
    document.getElementById("messageInput").value = "";
    //sets timer for response. 
    setTimeout(function () {
        var botResponse = responses[messageCount];
        addMessage(botResponse, "bot");
        messageCount = (messageCount + 1) % responses.length;
    }, 3000);
}
//adds listeners to button and if user hits enter
// document.getElementById("sendButton").addEventListener("click", function () {
//     sendMessage();
// });
document.getElementById("messageInput").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});