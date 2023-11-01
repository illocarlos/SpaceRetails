html = '';

obj = ['All', 'Internship', 'Entry_Level', 'Mid_Level', 'Senior_Level']

for(var i in obj) {
    html += '<option value=' + obj[i]  + '>' + obj[i] + '</option>'
}
document.getElementById('experience').innerHTML = html;