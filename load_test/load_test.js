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

let url = "http://" + ip + ":18002/labeling/test";

function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
var xhr = [];
var nice_count = 0;
async function main() {
  var xhr = new XMLHttpRequest();
  for (let i = 1; i <= 2000; i++) {
    // GET test
    xhr.open("GET", url, true); // true for asynchronous
    xhr.send(null);
    console.log("GET " + i);

    // POST test
    xhr.open("POST", url, true); // true for asynchronous
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(
      JSON.stringify({
        image_id: "615feadea8601b26f6ef5d7a",
        selected_label: "A",
      })
    );
    console.log("POST " + i);

    await timeout(100);

    // * 400m의 70%인 280m의 배수에 도달할 때마다 SCALING 수행
    // 1000ms : (REPLICA = 1개), (CPU = 90m), (TARGET = 23%/70%)
    // 400ms : (REPLICA = 1개), (CPU = 180m), (TARGET = 44%/70%)
    // 200ms : (REPLICA = 2개), (CPU = 400m), (TARGET = 48%/70%)
    // 100ms : (REPLICA = 2개), (CPU = 550m), (TARGET = 65%/70%), (3500개 째에서 마스터 노드 죽는 경우가 있었음. ABORTED)
    // 90ms : (REPLICA = 3개), (CPU = 750m), (TARGET = 50%/70%), (지연 시간이 너무 긺)
    // 80ms : (REPLICA = 4개), (CPU = 900m), (TARGET = 20%/70%), (워커 노드 1개 죽음. ABORTED)
    // 50ms : (마스터 노드 죽음. ABORTED)
    // ---------------------------------------
    // 100ms 간격 미만으로 빠르게 요청하는 경우
    // 부하 loop 중에 CPU와 MEMORY 이용률이 점점 커지며
    // 부하 loop를 멈추고 나서도 그러한 현상은 한참 동안 이어짐 (90m의 경우, 10분 넘게 걸림)
    // 요청이 큐잉되기 때문에 그런 것 같음
    // 부하 loop를 멈추고 난 지, 수 분이 지나서야 점점 CPU와 MEMERY 이용률이 줄어들고,
    // 이용률이 0m에 가까워지기 전까지는 DB의 값이 계속해서 변함
    // CPU와 이용률과 MEMORY 사용량은 비례하므로
    // MEMORY에 저장된 요청 메시지를 CPU가 처리하느라 비례 관계에 있지 않을까 추측함
    // 요청 개수만큼 DB에 반영되지 않는 이유는
    // 첫번째로, MEMORY가 가득 차서 이 발생하여 메시지 유실이 발생한 것으로 추측하고
    // 두번째로, CPU 이용률만으로 자동으로 Pod가 Terminate 되기 때문에
    // 큐잉된 요청 메시지가 Pod와 함께 통째로 사라지는 문제가 발생할 것으로 추측
    // 100ms로 loop를 4000번 돌렸을 때, DB에는 3271번만 반영됨
    // SCALE IN을 Disable 시킨 상태에서
    // 동일하게 100ms로 loop를 4000번 돌렸을 때는, DB에 3271번 반영되며
    // 이는 두번째 추측에 대한 근거가 됨
    // scale out은 즉시 빠르게 혹은 미리 해야 좋고
    // scale in은 느리게 나중에 하는 것이 좋을 것 같다고 느낌
  }
}

async function main2() {
  var xhr = new XMLHttpRequest();
  for (let i = 1; i <= 2000; i++) {
    // 속도를 바꿔가면서 요청할 예정
  }
}

main();
