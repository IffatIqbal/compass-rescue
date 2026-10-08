// Lightweight offline logic check; not a browser/layout test.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/Compass-Rescue.html','utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const elements=new Map();const el=id=>{if(!elements.has(id))elements.set(id,{innerHTML:'',textContent:'',value:0,max:0,add(){},click(){}});return elements.get(id)};
const ctx={document:{getElementById:el,createElement:()=>({click(){}})},Option:function(t,v){this.text=t;this.value=v},requestAnimationFrame(){},setTimeout(){},Blob,URL,console};
vm.createContext(ctx);vm.runInContext(script,ctx);
assert(el('ring-intact').innerHTML.includes('<circle'));
assert(el('chart').innerHTML.includes('<polyline'));
el('trial').onchange({target:{value:5}});el('time').oninput({target:{value:90}});
assert.equal(el('clock').textContent,'8.1 s');assert.equal(el('window').textContent,'Stimulation-free hold');
assert(!el('err-rescue').textContent.includes('NaN'));
el('filter').value='PENa';el('filter').oninput();assert.equal(el('neuron-count').textContent,'20 / 106 neurons');
el('play').onclick();assert.equal(el('play').textContent,'Pause');
console.log('Viewer logic: eight-trial selection, playback toggle, scrub, SVG generation passed. Layout not browser-verified.');
