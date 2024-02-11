const connectDB = require("../connect.js");
const Message = require("../models/Message.js");
require('dotenv').config();

async function createMessage(messageData, res) {
  await connectDB();
  try {
    const { prompt, query, response_text } = messageData.body;
    const message = new Message({ question:prompt, query:query, response:response_text });
    await message.save();
    return res.status(200).send("Success");
  } catch (e) {
    return res.status(400).send("Unable to create a message. Invalid data");
  }
}

module.exports = createMessage;