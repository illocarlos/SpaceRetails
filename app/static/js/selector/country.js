html = '';

obj = ['Brazil',
         'England',
         'France',
         'Germany',
         'Mexico',
         'Netherland',
         'Portugal',
         'Spain',
         'USA']

for(var i in obj) {
    html += '<option value=' + obj[i]  + '>' + obj[i] + '</option>'
}
document.getElementById('country').innerHTML = html;