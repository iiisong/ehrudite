const express = require('express');
const cors = require('cors');
const app = express();

require('dotenv').config();

app.use(cors());
app.use(express.json());

const connectDB = require('./db/connect');
const createMessage = require('./db/actions/createMessage');
const readMessage = require('./db/actions/readMessage');

app.post('/create-message', async (req, res) => {
  try {
    const result = await createMessage(req, res);
    return true;
  } catch {
    return false;
  }
});

app.get('/read-message', async (req, res) => {
  try {
    const result = await readMessage(req, res);
    return result;
  } catch (error) {
    console.error('Error reading message:', error);
    return error;
  }
});

const port = process.env.PORT || 4000;

const start = async () => {
  try {
    await connectDB();
    app.listen(port, () =>
      console.log(`Server is listening on port ${port}...`)
    );
  } catch (error) {
    console.log(error);
  }
};

start();