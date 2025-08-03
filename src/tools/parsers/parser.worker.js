// Worker.js
// import MavlinkParser from 'mavlinkParser'
const mavparser = require('./mavlinkParser')
const DataflashParser = require('./JsDataflashParser/parser').default
const DjiParser = require('./djiParser').default

let parser

// Python backend configuration
const PYTHON_BACKEND_URL = 'http://localhost:8000/api/process-flight-data';
let collectedMessages = {};

// Function to serialize and send data to Python
async function sendToPython(messagesData) {
    try {
        // Convert Float64Array to regular arrays for JSON
        const serialized = {};
        for (const [messageType, messageContent] of Object.entries(messagesData)) {
            serialized[messageType] = {};
            if (typeof messageContent === 'object' && messageContent !== null) {
                for (const [fieldName, fieldData] of Object.entries(messageContent)) {
                    if (fieldData instanceof Float64Array || fieldData instanceof Array) {
                        serialized[messageType][fieldName] = Array.from(fieldData);
                    } else {
                        serialized[messageType][fieldName] = fieldData;
                    }
                }
            } else {
                serialized[messageType] = messageContent;
            }
        }

        await fetch(PYTHON_BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: serialized })
        });
    } catch (error) {
        console.error('Failed to send data to Python:', error);
    }
}

// Override postMessage to capture data
const originalPostMessage = self.postMessage
self.postMessage = function(data) {
    // Collect individual messages
    if (data.messageType && data.messageList) {
        console.log('Received individual message batch:', {
            type: data.messageType,
            data: data.messageList
        });
        collectedMessages[data.messageType] = data.messageList;
    }
    
    // Send to Python when we have complete data
    if (data.messages && Object.keys(data.messages).length > 0) {
        console.log('Received complete messages batch:', data.messages);
        sendToPython(data.messages);
    } else if (data.messagesDoneLoading && Object.keys(collectedMessages).length > 0) {
        console.log('All messages loaded, final batch:', collectedMessages);
        sendToPython(collectedMessages);
    }
    
    // Call original
    originalPostMessage.call(this, data)
}

self.addEventListener('message', async function (event) {
    if (event.data === null) {
        console.log('got bad file message!')
    } else if (event.data.action === 'parse') {
        const data = event.data.file
        collectedMessages = {}; // Reset for new file
        
        if (event.data.isTlog) {
            parser = new mavparser.MavlinkParser()
            parser.processData(data)
        } else if (event.data.isDji) {
            parser = new DjiParser()
            await parser.processData(data)
        } else {
            parser = new DataflashParser(true)
            parser.processData(data, ['CMD', 'MSG', 'FILE', 'MODE', 'AHR2', 'ATT', 'GPS', 'POS',
                'XKQ1', 'XKQ', 'NKQ1', 'NKQ2', 'XKQ2', 'PARM', 'MSG', 'STAT', 'EV', 'XKF4', 'FNCE'])
        }
    } else if (event.data.action === 'loadType') {
        if (!parser) {
            console.log('parser not ready')
        }
        parser.loadType(event.data.type.split('[')[0])
    } else if (event.data.action === 'trimFile') {
        parser.trimFile(event.data.time)
    }
})