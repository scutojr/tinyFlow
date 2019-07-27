function leadingZero(num) {
  if (num > 10) {
    return num;
  } else {
    return `0${num}`;
  }
}


class Utils {
  dateString(date) {
    let h = leadingZero(date.getHours());
    let m = leadingZero(date.getMinutes());
    let s = leadingZero(date.getSeconds());
    return `${h}:${m}:${s}/${date.getMonth() + 1}.${date.getDate()}/${date.getFullYear()}`;
  }
}


export default new Utils();