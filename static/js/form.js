window.addEventListener("load", function(){
    let checkbox  = document.getElementById('check');
    let x = document.getElementById('password');
    checkbox.addEventListener('change', function() {
        if(this.checked) {
            x.type = 'text'; 
        } else {
            x.type = 'password'; 
        }
    });
});