var colorChoice = document.getElementById("choose-color")
var colorRange = document.getElementById("id_color")
var randomRange = colorRange.value

colorRange.addEventListener('input', function(e) {
  var hue = this.value
  var hsl = "hsl("+ hue + ", 100%, 80%)"
  colorChoice.style.backgroundColor = hsl
});
colorRange.value = randomRange;
var inputEvent = new Event('input');
colorRange.dispatchEvent(inputEvent);