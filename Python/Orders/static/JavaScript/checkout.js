document.querySelectorAll('.saved-address').forEach(el => {
    el.addEventListener('click', () => {
        document.getElementById('selected_address_id').value = el.dataset.id;

        document.querySelectorAll('.saved-address').forEach(div => div.classList.remove('selected'));
        el.classList.add('selected');
    });
});