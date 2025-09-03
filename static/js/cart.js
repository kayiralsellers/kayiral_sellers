let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Add item to cart
function addToCart(name, price, quantity = 1) {
    let found = cart.find(item => item.name === name);
    if (found) {
        found.quantity += quantity;
    } else {
        cart.push({ name: name, price: price, quantity: quantity });
    }
    saveCart();
    alert(`${name} x${quantity} added to cart!`);
}

// Remove one quantity of item from cart
function removeFromCart(name) {
    let index = cart.findIndex(item => item.name === name);
    if (index !== -1) {
        if (cart[index].quantity > 1) {
            cart[index].quantity -= 1;
        } else {
            cart.splice(index, 1); // remove item completely if quantity is 1
        }
        saveCart();
    }
}

// Delete item completely
function deleteFromCart(name) {
    cart = cart.filter(item => item.name !== name);
    saveCart();
}

// Save cart to localStorage and optionally refresh cart UI
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart(); // call this if you have a function to refresh the cart display
}

// Example render function (optional)
function renderCart() {
    const cartTable = document.getElementById('cart-table');
    if (!cartTable) return;

    cartTable.innerHTML = '';
    cart.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.name}</td>
            <td>
                <button onclick="removeFromCart('${item.name}')">-</button>
                ${item.quantity}
                <button onclick="addToCart('${item.name}', ${item.price}, 1)">+</button>
            </td>
            <td>PKR ${item.price}</td>
            <td>PKR ${item.price * item.quantity}</td>
            <td><button onclick="deleteFromCart('${item.name}')">Remove</button></td>
        `;
        cartTable.appendChild(row);
    });
}

// Initialize cart UI
renderCart();
