html = '';

obj = ['Time_series_(line)', 'Time_series_(bar)', 'Keywords', 'Enterprises', 'Enterprises_30', 'Skills']

for(var i in obj) {
    html += '<option value=' + obj[i]  + '>' + obj[i] + '</option>'
}
document.getElementById('metric').innerHTML = html;