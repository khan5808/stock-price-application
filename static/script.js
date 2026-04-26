function goSearch(){
 const t=document.getElementById('searchBox').value;
 if(t) location.href='/stock/'+t.toUpperCase();
}

async function loadStockPage(ticker){
 const chartData = await fetch('/api/chart/'+ticker).then(r=>r.json());
 const chart = LightweightCharts.createChart(document.getElementById('chart'), {
   height:420,
   layout:{background:{color:'#111827'},textColor:'#DDD'},
   grid:{vertLines:{color:'#1f2937'},horzLines:{color:'#1f2937'}}
 });
 const series = chart.addCandlestickSeries();
 series.setData(chartData);

 const pred = await fetch('/api/predict/'+ticker).then(r=>r.json());
 document.getElementById('pred').innerHTML = `$${pred.prediction} (${pred.signal})`;

 const earn = await fetch('/api/earnings/'+ticker).then(r=>r.json());
 document.getElementById('earn').innerText = earn.next_earnings;

 const news = await fetch('/api/news/'+ticker).then(r=>r.json());
 document.getElementById('news').innerHTML = news.map(n=>`<li>${n.title}</li>`).join('');

 const insiders = await fetch('/api/insiders/'+ticker).then(r=>r.json());
 document.getElementById('insiders').innerHTML = insiders.map(i=>`<li>${i.name}: ${i.type} ${i.shares}</li>`).join('');
}
