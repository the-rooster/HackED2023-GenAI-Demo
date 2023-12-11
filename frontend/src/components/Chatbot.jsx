import React, { useState, useEffect } from 'react';

import loadingGif from '../assets/loading.gif';
import './Chatbot.css'; // Assume we have a CSS file to style our components

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [sessionId, setSessionId] = useState(''); // This is the session ID that you would get from the GenAI API


    // when component mounts, see if there is a session ID in local storage
    useEffect(() => {
        getSessionId();
    }, []);


    async function getSessionId() {
        const storedSessionId = localStorage.getItem('sessionId');
        if (storedSessionId) {
            setSessionId(storedSessionId);
        }


        // check if session ID is valid and if not, get a new one
        let req = await fetch("http://localhost:8080/session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: storedSessionId,
            }),
        });
        let res = await req.json();
        if (req.status !== 200) {
            console.log('Error getting session ID');
            return;
        }

        if (res.session_id == storedSessionId) {
            // get the chat history
            let req = await fetch("http://localhost:8080/get-messages", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    session_id: storedSessionId,
                }),
            });

            let res = await req.json();

            if (req.status !== 200) {
                console.log('Error getting chat history');
                return;
            }

            setMessages(res.messages);
        }
        
        setSessionId(res.session_id);

        localStorage.setItem('sessionId', res.session_id);
    
    }


    const sendMessage = async () => {
        if (inputText.trim()) {

            
            setMessages(msgs => [...msgs, { content: inputText, role: 'user' }]);
            setInputText('');


            if (!sessionId) {
                await getSessionId();
                console.log(sessionId,123123);
            }

            // Here you would also send the message to the GenAI agent
            let req = await fetch("http://localhost:8080/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: inputText,
                }),
            });

            let res = await req.json();

            if (req.status !== 200) {
                console.log('Error sending message');
                return;
            }

            setMessages(msgs => [...msgs, { content: res.content, role: 'assistant' }]);
        }
    };

    const clearMessages = () => {
        setMessages([]);

        if (localStorage.getItem('sessionId')) {
            localStorage.removeItem('sessionId');
        }
    };

    const handleInputChange = (e) => {
        setInputText(e.target.value);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    return (
        <>
            <div className="chatbot-container">
                <div className="messages-container">
                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.role}`}>
                            {message.content}
                        </div>
                    ))}
                </div>
                <div className="chatbot-options">
                    <input
                        type="text"
                        value={inputText}
                        onChange={handleInputChange}
                        onKeyUp={handleKeyPress}
                        placeholder="Type a message..."
                        className="message-input"
                    />
                    <button onClick={sendMessage} className="send-button">Send</button>
                </div>
            </div>
            <button onClick={clearMessages} className="clear-button">Clear</button>
        </>

    );
};

export default Chatbot;
