// Open and close basket
document.getElementById('basket-toggle').addEventListener('click', function() {
    document.getElementById('basket-sidebar').classList.toggle('open');
});

document.getElementById('basket-close').addEventListener('click', function() {
    document.getElementById('basket-sidebar').classList.remove('open');
});

function updateTotal() {
    let total = 0;
    document.querySelectorAll('#order tr.basket').forEach(row => {
        const quantityCell = row.querySelector('td[id^="quantity-')
        const priceCell = row.querySelector('.item-price');
        if (quantityCell && priceCell) {
            const quantity = parseInt(quantityCell.textContent, 10) || 0;
            const price = parseFloat(priceCell.textContent.replace('€', '')) || 0;
            total += quantity * price;
        }
    });
    document.querySelector('#order-total').textContent = `Total: €${total}`;
}

// Plus and minus logic
document.querySelector('#order table').addEventListener('click', async (e) => {
    const btn = e.target.closest('.plusminusButton');
    if (!btn) return;

    const itemId = btn.dataset.itemId;
    const action = btn.dataset.action;
    const url = action === 'increase'
    ? `/increase_quantity/${itemId}`
    : `/decrease_quantity/${itemId}`

    const response = await fetch(url, { method: 'POST' });
    const data = await response.json();

    const quantityCell = document.querySelector(`#quantity-${itemId}`);
    if (quantityCell) {
        quantityCell.textContent = data.quantity;
    }

    if(data.quantity === 0) {
        quantityCell.closest('tr').remove();
    }
    updateTotal();
});

document.querySelectorAll('.basket-button').forEach(btn => {
    btn.addEventListener('click', async () => {
        const itemId = btn.dataset.itemId;
        const response = await fetch(`/add_to_basket/${itemId}`, { method: 'POST' });
        const data = await response.json();

        let quantityCell = document.querySelector(`#quantity-${itemId}`);
        if (quantityCell) {
            quantityCell.textContent = data.quantity;
        } else {
            const table = document.querySelector('#order table');
            const newRow = document.createElement('tr');
            newRow.classList.add('basket');
                    newRow.innerHTML = `
                    <td id="quantity-${itemId}">${data.quantity}</td>
                    <td>
                        <button class="plusminusButton" data-item-id="${itemId}" data-action="increase">
                        <svg width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 3.5H3.5V3V1C3.5 0.723858 3.72386 0.5 4 0.5C4.27614 0.5 4.5 0.723858 4.5 1V3V3.5H5H7C7.27614 3.5 7.5 3.72386 7.5 4C7.5 4.27614 7.27614 4.5 7 4.5H5H4.5V5V7C4.5 7.27614 4.27614 7.5 4 7.5C3.72386 7.5 3.5 7.27614 3.5 7V5V4.5H3H1C0.723858 4.5 0.5 4.27614 0.5 4C0.5 3.72386 0.723858 3.5 1 3.5H3Z" stroke="#FFF"></path>
                        </svg>
                        </button>
                        <button class="plusminusButton" data-item-id="${itemId}" data-action="decrease">
                        <svg width="8" height="2" viewBox="0 0 8 2" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <mask id="path-1-inside-1" fill="white">
                                <path d="M7 0H1C0.447715 0 0 0.447715 0 1C0 1.55228 0.447715 2 1 2H7C7.55228 2 8 1.55228 8 1C8 0.447715 7.55228 0 7 0Z"></path>
                            </mask>
                            <path d="M1 2H7V-2H1V2ZM7 0H1V4H7V0ZM1 0C1.55228 0 2 0.447715 2 1H-2C-2 2.65685 -0.656854 4 1 4V0ZM6 1C6 0.447715 6.44772 0 7 0V4C8.65685 4 10 2.65685 10 1H6ZM7 2C6.44772 2 6 1.55228 6 1H10C10 -0.656854 8.65685 -2 7 -2V2ZM1 -2C-0.656854 -2 -2 -0.656854 -2 1H2C2 1.55228 1.55228 2 1 2V-2Z" fill="#FFF" mask="url(#path-1-inside-1)"></path>
                        </svg>
                        </button>
                    </td>
                    <td>${data.name || 'Item'}</td>
                    <td class="item-price">€${data.price || ''}</td>
                    `;
                    table.appendChild(newRow);
                    document.getElementById('basket-sidebar').classList.add('open');
        }
        updateTotal();
    });
});