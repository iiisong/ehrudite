const mongoose = require("mongoose")

const messageSchema = mongoose.Schema({
    question: {
        type: String,
        required: true
    },
    response: {
        type: String,
        required: true
    }
})

module.exports = mongoose.model("Message", messageSchema)