const connectDB = require("../connect.js");
const Message = require("../models/Message.js");
require('dotenv').config();

async function readMessage(req, res) {
  await connectDB();
  try {
    // Perform logic to retrieve messages from the database
    const messages = await Message.find().sort({ createdAt: -1 }).limit(10); // Example: Retrieve all messages

    // Return the retrieved messages
    return res.status(200).json(messages);
  } catch (e) {
    console.error('Error reading messages:', e);
    return res.status(500).send("Unable to read messages from the database");
  }
}

module.exports = readMessage;