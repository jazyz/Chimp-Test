var rows = 6;
var cols = 10;
var tot = rows * cols;
var arr = new Array(tot);
var grid;
var lvl;
var cur;
var gameOn = false;
var titleText;

function startGame() {
  if (gameOn) {
    return;
  }
  gameOn = true;
  titleText = document.getElementById("startGame");
  titleText.innerHTML = "Chimp Test";
  grid = document.getElementById("grid");
  titleText.style.color = "#4287f5";
  for (let i = 0; i < tot; i++) {
    let square = document.createElement("div");
    square.className = "empty";
    square.id = i;
    grid.appendChild(square);
    arr[i] = 0;
  }
  lvl = 4;
  cur = 1;
  startLvl(lvl);
}

function resetArray() {
  for (let i = 0; i < tot; i++) {
    arr[i] = 0;
  }
}

function randint(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}

function startLvl(x) {
  for (let i = 1; i <= x; i++) {
    rand = randint(0, tot);
    while (arr[rand] != 0) {
      rand = randint(0, tot);
    }
    arr[rand] = i;
    let square = document.getElementById(rand);
    square.style.border = "3px solid cyan";
    square.innerHTML = i;
    square.addEventListener("click", function () {
      squareClicked(square, i, x);
    });
  }
}

function sendRanking() {
  console.log(is_logged_in);
  console.log(username);
  if (is_logged_in !== "True") {
    return;
  }
  const score = lvl;
  fetch("/rankings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user: username, score: score }),
  })
    .then(() => {
      console.log("Ranking submitted successfully");
    })
    .catch((error) => {
      console.error("Error submitting ranking:", error);
    });
}

function gameEnd() {
  grid.innerHTML = "";
  titleText.innerHTML = "Click Here to Restart Game";
  titleText.style.color = "red";
  if (is_logged_in !== "True") {
    alert("Your score: " + lvl);
  } else {
    alert("Your score: " + lvl + ". Ranking sent to leaderboard!");
  }
  sendRanking();
  gameOn = false;
}

function squareClicked(square, x, thislvl) {
  if (thislvl != lvl) {
    return;
  }
  if (x != cur) {
    gameEnd();
    return;
  }
  if (x == 1) {
    for (let i = 0; i < tot; i++) {
      let square = document.getElementById(i);
      square.innerHTML = "";
    }
  }
  square.style.border = "3px solid #4287f5";
  square.innerHTML = "";
  square.replaceWith(square.cloneNode(true));
  cur++;
  if (x == lvl) {
    cur = 1;
    resetArray();
    startLvl(++lvl);
  }
}
