// injects brushed-metal + grain texture overlays into every .art element
document.querySelectorAll('.art').forEach((el,i)=>{
  el.insertAdjacentHTML('afterbegin',`
  <svg class="tex brush"><filter id="b${i}"><feTurbulence type="fractalNoise" baseFrequency="0.0035 0.75" numOctaves="3" seed="${7+i}"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#b${i})"/></svg>
  <svg class="tex grain"><filter id="n${i}"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="${3+i}"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#n${i})"/></svg>`);
});
