html = '';

obj = ['Last_Week', 'Last_Month', 'Last_Trimester']

for(var i in obj) {
    html += '<option value=' + obj[i]  + '>' + obj[i] + '</option>'
}
document.getElementById('date').innerHTML = html;