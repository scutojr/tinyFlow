const proxy = require('http-proxy-middleware');
const process = require('child_process');


var cmd = "docker-machine.exe ls | awk '$4 ~ /Running/ {print $5}'"
var regExp = /([\d\.]+):/g
var msg = new String(process.execSync(cmd))
var match = regExp.exec(msg)
var dockerMachine = "localhost"


if (match != undefined) {
  dockerMachine = match[1]
}


module.exports = function (app) {
  app.use(proxy('/tobot', { target: "http://" + dockerMachine + ":54321"}));
};
