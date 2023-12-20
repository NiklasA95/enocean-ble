const secrets = require("./secrets.js");

// Load the node-enocean-ble and get a `EnoceanBle` constructor object
const EnoceanBle = require("./lib/enocean-ble.js");
// Create an `EnoceanBle` object
const enocean = new EnoceanBle();

// Commissioning
enocean.commission(secrets.commissioningData);

// Set a callback for incoming telegrams
enocean.ondata = (telegram) => {
  console.log(telegram);
};

// Start to monitor telegrams
enocean
  .start({ auth: false })
  .then(() => {
    // Successfully started to monitor telegrams
  })
  .catch((error) => {
    // Failed to start to monitor telegrams
    console.error(error);
  });
