const express = require('express');
const cors = require('cors');
const app = express();

require('dotenv').config();

app.use(cors());
app.use(express.json());

const connectDB = require('./db/connect');
const createMessage = require('./db/actions/createMessage');

app.post('/create-message', async (req, res) => {
  try {
    const result = await createMessage(req, res);
    return true;
  } catch {
    return false;
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