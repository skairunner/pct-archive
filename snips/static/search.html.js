document.addEventListener('DOMContentLoaded', init);

var FOLDOPEN = false;

function init() {
  let el = document.querySelector('#formcontent');
  let newdiv = null;
  // Insert the thing to click to fold/unfold
  let folddiv = document.createElement('div');
  folddiv.classList.add('fold');
  folddiv.textContent = '▶ Tags';
  folddiv.onclick = function() {
    FOLDOPEN = !FOLDOPEN;
    if (FOLDOPEN) {
      this.textContent = '▼ Tags';
      newdiv.setAttribute("style", "display: initial;");
    } else {
      this.textContent = '▶ Tags';
      newdiv.setAttribute("style", "display: none;");
    }
  };
  el.appendChild(folddiv);

  newdiv = document.createElement('div');
  newdiv.setAttribute("style", "display: none;");
  newdiv.classList.add('tagfold');
  el.appendChild(newdiv);
  // Put all tags in here
  let tags = document.querySelectorAll('.tag');
  for (let tag of tags) {
    newdiv.appendChild(tag);
  }
}
