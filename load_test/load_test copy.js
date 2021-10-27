// const XMLHttpRequest = require("xhr2");
// const fs = require("fs");

// let rawdata = fs.readFileSync("../ips/ips.json");
// let student = JSON.parse(rawdata);
// let ip = student["kafka"];

// let url = "http://localhost:8002/labeling/test";

// function timeout(ms) {
//   return new Promise((resolve) => setTimeout(resolve, ms));
// }

// async function main() {
//   count = 0;
//   for (let i = 1; i <= 100; i++) {
//     var xmlHttp = new XMLHttpRequest();
//     xmlHttp.onreadystatechange = function () {
//       // 요청에 대한 콜백
//       if (xmlHttp.readyState === xmlHttp.DONE) {
//         // 요청이 완료되면
//         if (xmlHttp.status === 200 || xmlHttp.status === 201) {
//           count = count + 1;
//           console.log(xmlHttp.status);
//           console.log(i + ":" + count);
//         } else {
//           console.log(xmlHttp.status);
//           console.error("error" + i);
//         }
//       }
//     };
//     xmlHttp.open("GET", url, true); // true for asynchronous
//     xmlHttp.send(null);
//     await timeout(1);
//   }
// }

// main();

// let num = 0;

// function httpGetAsync(theUrl, callback) {
//   var xmlHttp = new XMLHttpRequest();
//   //   xmlHttp.onreadystatechange = function () {
//   //     if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
//   //       callback(xmlHttp.responseText);
//   //   };
//   xmlHttp.open("GET", theUrl, true); // true for asynchronous
//   xmlHttp.send(null);
//   num++;
// }

const XMLHttpRequest = require("xhr2");
const fs = require("fs");

let rawdata = fs.readFileSync("../ips/ips.json");
let student = JSON.parse(rawdata);
let ip = student["kafka"];

let url = "http://localhost:8002/labeling/test";

function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
var xhr = [];
var nice_count = 0;
async function main() {
  for (let i = 1; i <= 100; i++) {
    xhr[i] = new XMLHttpRequest();
    xhr[i].onreadystatechange = function (e) {
      if (xhr[i].readyState === 4) {
        if (xhr[i].status === 200) {
          nice_count += 1;
          //   console.log(xhr[i].responseText);
          console.log("[" + i + "] : NICE" + nice_count);
        } else {
          console.log(
            `xhr[${i}].readyState = 4 && xhr[${i}].status != 200 ` +
              xhr[i].status
          );
          console.error(xhr[i].onerror);
        }
      } else {
        if (xhr[i].status === 200) {
          //   console.log(xhr[i].responseText);
          console.log(
            "[" +
              i +
              "] xhr[i].readyState != 4" +
              "(" +
              xhr[i].readyState +
              ")" +
              " && xhr[i].status = 200(" +
              xhr[i].status +
              ")"
          );
        } else {
          console.log(
            "[" +
              i +
              "] xhr[i].readyState != 4" +
              "(" +
              xhr[i].readyState +
              ")" +
              " && xhr[i].status != 200(" +
              xhr[i].status +
              ")" +
              xhr[i].statusText
          );
        }
      }
    };

    // GET test
    xhr[i].open("GET", url, true); // true for asynchronous
    xhr[i].send(null);
    // console.log("GET " + i);

    // POST test
    // xmlHttp.open("POST", url, true); // true for asynchronous
    // xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // xmlHttp.send(
    //   JSON.stringify({
    //     image_id: "615feadea8601b26f6ef5d7a",
    //     selected_label: "A",
    //   })
    // );
    // console.log("POST " + i);

    await timeout(1);
  }
}

main();
