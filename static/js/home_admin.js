document.addEventListener('DOMContentLoaded', function() {
    const addEmpBtn = document.getElementById('add-emp-btn');
    addEmpBtn.addEventListener('click', function() {
        window.location.href = '/admin/add_employee';
    });
});
