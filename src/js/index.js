const secrets = require('./secrets.js');

// Load the node-enocean-ble and get a `EnoceanBle` constructor object
const EnoceanBle = require('node-enocean-ble');
// Create an `EnoceanBle` object
const enocean = new EnoceanBle();
 
// Commissioning (Easyfit Double Rocker Wall Switch)
enocean.commission(secrets.comissioningData);
 
// Set a callback for incoming telegrams
enocean.ondata = (telegram) => {
  console.log(telegram);
};
 
// Start to monitor telegrams
enocean.start().then(() => {
  // Successfully started to monitor telegrams
}).catch((error) => {
  // Failed to start to monitor telegrams
  console.error(error);
});