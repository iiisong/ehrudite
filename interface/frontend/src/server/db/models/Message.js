const mongoose = require("mongoose")

const messageSchema = mongoose.Schema({
    question: {
        type: String,
        required: true
    },
    query: {
        type: String,
        required: true
    },
    response: {
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
      }
})

module.exports = mongoose.model("Message", messageSchema)