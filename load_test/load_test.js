const XMLHttpRequest = require("xhr2");
const fs = require("fs");

let rawdata = fs.readFileSync("../ips/ips.json");
let student = JSON.parse(rawdata);
let ip = student["kafka"];

let url = "http://" + ip + ":8002/labeling/test";

function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  var xmlHttp = new XMLHttpRequest();
  for (let i = 1; i <= 100000; i++) {
    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send(null);
    console.log(i);
    await timeout(100);
  }
}

main();
