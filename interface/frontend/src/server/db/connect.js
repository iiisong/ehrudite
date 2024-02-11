const mongoose = require("mongoose")
require('dotenv').config();

async function connectDB() {
    if (mongoose.connections[0].readyState) return;
    await mongoose.connect(process.env.MONGO_DB, {
            dbName: process.env.COL_NAME,
        })
        .catch((e) => {
            console.error("Error connecting to database.");
            throw e;
        });
};

module.exports = connectDB;