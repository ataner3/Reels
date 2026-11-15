// Renders the brand preview PNGs. Usage: node render.js   (needs Playwright + Chromium)
const {chromium}=require('playwright'),path=require('path');
const src=f=>'file://'+path.join(__dirname,f),out=f=>path.join(__dirname,'..',f);
(async()=>{const b=await chromium.launch();
 const shot=async(url,w,h,file,sel)=>{const p=await b.newPage({viewport:{width:w,height:h}});await p.goto(src(url));await p.evaluate(()=>document.fonts.ready);
  if(sel)await p.locator(sel).screenshot({path:out(file)});else await p.screenshot({path:out(file),fullPage:!h||h<10});await p.close()};
 await shot('logo.html',2400,1500,'01_logo_sheet.png','#sheet');
 await shot('logo.html',2400,1500,'01_logo_wordmark_dark.png','#solo-dark');
 await shot('logo.html',2400,1500,'01_logo_wordmark_light.png','#solo-light');
 await shot('profile.html',1080,1080,'02_profile_picture.png','#avatar');
 await shot('profile.html?img='+encodeURIComponent(src('../02_profile_picture.png')),1080,1700,'02_profile_picture_circle_check.png','#crop');
 for(const [f,n] of [['a','hook'],['b','fix'],['c','verdict']])await shot('frame.html?f='+f,1080,1920,`03_video_frame_${f}_${n}.png`);
 await shot('title.html',1080,1920,'04_title_card.png');
 const p=await b.newPage({viewport:{width:2400,height:1000}});await p.goto(src('board.html'));await p.screenshot({path:out('00_overview.png'),fullPage:true});
 await b.close()})();
