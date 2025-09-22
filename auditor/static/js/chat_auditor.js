document.addEventListener('DOMContentLoaded', function() {
    var lastMessageId = null;

    function displayMessages(){
        $.ajax({
            type: 'GET',
            url: "getMessages",
            data: { room_id: room_id,
            last_message_id: lastMessageId }, // Pass the last message ID to the server
        
            success: function(response) {
                console.log(response);
                for (var key in response.messages) {
                    // Add new messages only
                    if (response.messages[key].id > lastMessageId) {
                        var temp = '<li class="';
        
                        if (response.messages[key].sender_id === response.auditor_id) {
                            var messageClass = "message-sender";
                            var timestampClass = "timestamp-sender"
                        } else {
                            var messageClass = "message-receiver";
                            var timestampClass = "timestamp-receiver"
                        }
        
                        var temp2 = temp + messageClass + '">'+
                            '<div class="message-content">'+response.messages[key].content+'</div>'+
                            '</li>'+
                            '<div class="message-timestamp '+timestampClass+'">'+response.messages[key].timestamp+'</div>'
                            ;
        
                        $("#message-list").append(temp2);
        
                        // Update the last message ID
                        lastMessageId = response.messages[key].id;
                    }
                }
            },
            error: function(response) {
                console.log("error fetching messages");
                console.log(response);
            }
        });
    }
    displayMessages();
    setInterval(function() {
        displayMessages();
    }, 500);


    // pressing enter sends the message
    // it wont send if the message is empty
    var textarea = document.getElementById('message');
    textarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); 
            if (textarea.value.trim() !== '') {
                $.ajax({
        
                    //AJAX 
                        
                    type:'POST',
                    url:'auditor/send',
                    data:{
                        room_id:$('#room_id').val(),
                        message:$('#message').val(),
                        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                    },
        
                });
            
                textarea.value = ''
            }
                
        }
    });
    
    // deny empty strings from bieng entered when pressing send
    var form = document.getElementById('post-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        if (textarea.value.trim() !== '') {

            $.ajax({

                //AJAX 
                  
                type:'POST',
                url:'auditor/send',
                data:{
                    room_id:$('#room_id').val(),
                    message:$('#message').val(),
                  csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                },
        
            });

            textarea.value = ''
        }
    });

    
    // automaticly scoll to the end of the chat when the page is loaded
    var chatContainer = document.getElementById('chat-messages');
    chatContainer.scrollTop = chatContainer.scrollHeight;


    // automaticly scroll to the end of the chat when a new message gets added
    var messageList = document.getElementById('message-list');
    var observer = new MutationObserver(function() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    });
    observer.observe(messageList, { childList: true });

});