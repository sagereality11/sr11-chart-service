const fs=require('fs'),{minify}=require('terser');
(async()=>{
 const src=['glyphs.js','triwheel.js','diagram.js'].map(f=>fs.readFileSync(f,'utf8')).join('\n')
  +'\n(function(){\n'+fs.readFileSync('trnpdf.js','utf8')+'\n})();\n'+fs.readFileSync('tmapp.js','utf8');
 const m=await minify(src,{compress:true,mangle:true,format:{comments:false,ascii_only:true}});
 const css=fs.readFileSync('tmsite/tm.css','utf8').replace(/\n/g,'');
 fs.writeFileSync('tmsite/bundle.min.js',m.code);
 const page='<!-- wp:html -->\n<style>'+css+'</style>\n<script data-jetpack-boost="ignore">'+m.code+'</script>\n<!-- /wp:html -->';
 fs.writeFileSync('tmsite/code-page.html',page);
 console.log('bundle',m.code.length,'page',page.length, 'amp', (m.code.match(/&&/g)||[]).length);
})();
