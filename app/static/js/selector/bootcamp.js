html = '';

obj = ['Cyber', 'Data', 'Marketing', 'Product', 'Ux/Ui', 'Web', 'Web3']

for(var i in obj) {
    html += '<option value=' + obj[i]  + '>' + obj[i] + '</option>'
}
document.getElementById('bootcamp').innerHTML = html;


