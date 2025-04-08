/**
 * GlassRain Cart System
 * 
 * Handles the shopping cart functionality for the GlassRain platform.
 * This includes adding and removing items, updating quantities,
 * calculating totals, managing the cart UI, and handling saved items.
 */

const Cart = (function() {
    // Private cart state
    let cartItems = [];
    let savedItems = [];
    let cartOpen = false;
    let savedItemsOpen = false;
    
    // Load cart and saved items from localStorage if available
    function loadCart() {
        const savedCart = localStorage.getItem('glassrainCart');
        if (savedCart) {
            try {
                cartItems = JSON.parse(savedCart);
                updateCartUI();
            } catch (e) {
                console.error('Failed to load cart from localStorage:', e);
                cartItems = [];
            }
        }
        
        // Load saved items
        const savedItemsList = localStorage.getItem('glassrainSavedItems');
        if (savedItemsList) {
            try {
                savedItems = JSON.parse(savedItemsList);
                updateSavedItemsUI();
            } catch (e) {
                console.error('Failed to load saved items from localStorage:', e);
                savedItems = [];
            }
        }
    }
    
    // Save cart to localStorage
    function saveCart() {
        try {
            localStorage.setItem('glassrainCart', JSON.stringify(cartItems));
        } catch (e) {
            console.error('Failed to save cart to localStorage:', e);
        }
    }
    
    // Save saved items to localStorage
    function saveSavedItems() {
        try {
            localStorage.setItem('glassrainSavedItems', JSON.stringify(savedItems));
        } catch (e) {
            console.error('Failed to save items to localStorage:', e);
        }
    }
    
    // Update cart count and contents
    function updateCartUI() {
        // Update cart count
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
            cartCount.textContent = totalItems;
        }
        
        // Update saved items count if element exists
        const savedItemsCount = document.getElementById('saved-items-count');
        if (savedItemsCount) {
            savedItemsCount.textContent = savedItems.length;
            // Show or hide the count based on items
            savedItemsCount.style.display = savedItems.length > 0 ? 'inline-block' : 'none';
        }
        
        // Update cart contents
        const cartContent = document.getElementById('cart-content');
        const emptyCartMessage = document.getElementById('empty-cart-message');
        const checkoutBtn = document.getElementById('checkout-btn');
        
        if (!cartContent) return;
        
        if (cartItems.length === 0) {
            // Cart is empty
            if (emptyCartMessage) emptyCartMessage.style.display = 'block';
            cartContent.innerHTML = '';
            if (checkoutBtn) checkoutBtn.disabled = true;
            return;
        }
        
        // Cart has items
        if (emptyCartMessage) emptyCartMessage.style.display = 'none';
        if (checkoutBtn) checkoutBtn.disabled = false;
        
        // Group items by store
        const itemsByStore = {};
        cartItems.forEach(item => {
            if (!itemsByStore[item.store_id]) {
                itemsByStore[item.store_id] = {
                    id: item.store_id,
                    name: item.store_name,
                    logo_url: item.store_logo || 'https://cdn-icons-png.flaticon.com/512/825/825573.png',
                    items: []
                };
            }
            itemsByStore[item.store_id].items.push(item);
        });
        
        // Build cart HTML
        let cartHTML = '';
        
        Object.values(itemsByStore).forEach(store => {
            let storeTotal = 0;
            
            // Start store section
            cartHTML += `
                <div class="cart-store" data-store-id="${store.id}">
                    <div class="cart-store-header">
                        <img src="${store.logo_url}" alt="${store.name}" class="cart-store-logo">
                        <span class="cart-store-name">${store.name}</span>
                    </div>
                    <div class="cart-items">
            `;
            
            // Add store items
            store.items.forEach(item => {
                const itemPrice = item.is_on_sale ? item.sale_price : item.price;
                const itemTotal = itemPrice * item.quantity;
                storeTotal += itemTotal;
                
                cartHTML += `
                    <div class="cart-item" data-item-id="${item.id}">
                        <img src="${item.image_url}" alt="${item.name}" class="cart-item-image">
                        <div class="cart-item-details">
                            <div class="cart-item-name">${item.name}</div>
                            <div class="cart-item-price">$${itemPrice.toFixed(2)}</div>
                            <div class="cart-item-quantity">
                                <button class="quantity-btn" onclick="Cart.decreaseQuantity(${item.id})">-</button>
                                <span>${item.quantity}</span>
                                <button class="quantity-btn" onclick="Cart.increaseQuantity(${item.id})">+</button>
                            </div>
                            <div class="cart-item-actions">
                                <button class="save-for-later-btn" onclick="Cart.saveForLater(${item.id})">Save for Later</button>
                            </div>
                        </div>
                        <button class="cart-item-remove" onclick="Cart.removeItem(${item.id})">×</button>
                    </div>
                `;
            });
            
            // Add store total
            cartHTML += `
                    </div>
                    <div class="cart-store-total">
                        <span>Store Total:</span>
                        <span>$${storeTotal.toFixed(2)}</span>
                    </div>
                </div>
            `;
        });
        
        // Update cart content
        cartContent.innerHTML = cartHTML;
        
        // Update total price
        updateTotalPrice();
    }
    
    // Update total price in cart footer
    function updateTotalPrice() {
        const cartTotalElement = document.getElementById('cart-total');
        if (!cartTotalElement) return;
        
        const total = cartItems.reduce((sum, item) => {
            const price = item.is_on_sale ? item.sale_price : item.price;
            return sum + (price * item.quantity);
        }, 0);
        
        cartTotalElement.textContent = `$${total.toFixed(2)}`;
    }
    
    // Add an item to the cart
    function addItem(product) {
        // Check if item already exists in cart
        const existingItemIndex = cartItems.findIndex(item => item.id === product.id);
        
        if (existingItemIndex >= 0) {
            // Increase quantity if item exists
            cartItems[existingItemIndex].quantity += 1;
        } else {
            // Add new item to cart
            cartItems.push({
                ...product,
                quantity: 1
            });
        }
        
        // Save and update UI
        saveCart();
        updateCartUI();
        
        // Show cart if not already open
        if (!cartOpen) {
            toggleCart();
        }
        
        // Track the add-to-cart event
        trackAddToCart(product);
    }
    
    // Remove an item from the cart
    function removeItem(itemId) {
        cartItems = cartItems.filter(item => item.id !== itemId);
        saveCart();
        updateCartUI();
    }
    
    // Increase item quantity
    function increaseQuantity(itemId) {
        const itemIndex = cartItems.findIndex(item => item.id === itemId);
        if (itemIndex >= 0) {
            cartItems[itemIndex].quantity += 1;
            saveCart();
            updateCartUI();
        }
    }
    
    // Decrease item quantity
    function decreaseQuantity(itemId) {
        const itemIndex = cartItems.findIndex(item => item.id === itemId);
        if (itemIndex >= 0) {
            if (cartItems[itemIndex].quantity > 1) {
                cartItems[itemIndex].quantity -= 1;
            } else {
                // Remove item if quantity reaches 0
                removeItem(itemId);
                return;
            }
            saveCart();
            updateCartUI();
        }
    }
    
    // Clear the entire cart
    function clearCart() {
        cartItems = [];
        saveCart();
        updateCartUI();
    }
    
    // Get all items in the cart
    function getItems() {
        return [...cartItems];
    }
    
    // Get unique stores in the cart
    function getUniqueStores() {
        const stores = {};
        cartItems.forEach(item => {
            if (!stores[item.store_id]) {
                stores[item.store_id] = {
                    id: item.store_id,
                    name: item.store_name,
                    logo_url: item.store_logo || 'https://cdn-icons-png.flaticon.com/512/825/825573.png'
                };
            }
        });
        return Object.values(stores);
    }
    
    // Get items for a specific store
    function getStoreItems(storeId) {
        return cartItems.filter(item => item.store_id === storeId);
    }
    
    // Calculate total for a specific store
    function getStoreTotal(storeId) {
        return cartItems
            .filter(item => item.store_id === storeId)
            .reduce((total, item) => {
                const price = item.is_on_sale ? item.sale_price : item.price;
                return total + (price * item.quantity);
            }, 0);
    }
    
    // Track add to cart event
    function trackAddToCart(product) {
        // In a real implementation, this would send tracking data to an analytics service
        console.log('Add to cart event:', product);
        
        // If API endpoint is available, track the event
        try {
            fetch('/api/track_checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: 'add_to_cart',
                    product_id: product.id,
                    product_name: product.name,
                    price: product.is_on_sale ? product.sale_price : product.price,
                    store_id: product.store_id,
                    store_name: product.store_name
                })
            }).catch(error => {
                console.log('Error tracking add to cart event (this is normal if tracking endpoint is not implemented)');
            });
        } catch (e) {
            console.log('Error tracking add to cart event:', e);
        }
    }
    
    // Toggle the cart panel
    function toggleCart() {
        const cartPanel = document.getElementById('cart-panel');
        const overlay = document.querySelector('.overlay');
        const savedItemsPanel = document.getElementById('saved-items-panel');
        
        if (cartPanel && overlay) {
            // If saved items panel is open, close it first
            if (savedItemsOpen && savedItemsPanel) {
                savedItemsPanel.style.right = '-400px';
                savedItemsOpen = false;
            }
            
            // Toggle cart panel
            cartPanel.classList.toggle('open');
            overlay.classList.toggle('active');
            cartOpen = cartPanel.classList.contains('open');
            
            // Update cart UI when opening
            if (cartOpen) {
                updateCartUI();
            }
        }
    }
    
    // Initialize the cart
    function init() {
        loadCart();
        updateCartUI();
        updateSavedItemsUI();
        
        // Add event listeners for cart toggle
        const cartIcon = document.querySelector('.cart-icon');
        if (cartIcon) {
            cartIcon.addEventListener('click', toggleCart);
        }
        
        // Add event listeners for saved items toggle
        const savedItemsIcon = document.querySelector('.saved-items-icon');
        if (savedItemsIcon) {
            savedItemsIcon.addEventListener('click', toggleSavedItems);
        }
        
        // Ensure saved items panel starts hidden but ready for animation
        const savedItemsPanel = document.getElementById('saved-items-panel');
        if (savedItemsPanel) {
            savedItemsPanel.style.right = '-400px';
            savedItemsPanel.style.display = 'flex';
        }
        
        // Add CSS class for active panels
        // This is added dynamically to ensure it doesn't conflict with other styles
        const style = document.createElement('style');
        style.textContent = `
            .cart-panel.open {
                right: 0;
            }
            .saved-items-panel.open {
                right: 0;
            }
            .overlay.active {
                display: block;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Save for Later feature
    function updateSavedItemsUI() {
        // Check if saved items UI exists
        const savedItemsContent = document.getElementById('saved-items-content');
        const emptySavedItemsMessage = document.getElementById('empty-saved-items-message');
        
        if (!savedItemsContent) return;
        
        // Update saved items count
        const savedItemsCount = document.getElementById('saved-items-count');
        if (savedItemsCount) {
            savedItemsCount.textContent = savedItems.length;
            savedItemsCount.style.display = savedItems.length > 0 ? 'inline-block' : 'none';
        }
        
        if (savedItems.length === 0) {
            // No saved items
            if (emptySavedItemsMessage) emptySavedItemsMessage.style.display = 'block';
            savedItemsContent.innerHTML = '';
            return;
        }
        
        // Show saved items
        if (emptySavedItemsMessage) emptySavedItemsMessage.style.display = 'none';
        
        // Group items by store
        const itemsByStore = {};
        savedItems.forEach(item => {
            if (!itemsByStore[item.store_id]) {
                itemsByStore[item.store_id] = {
                    id: item.store_id,
                    name: item.store_name,
                    logo_url: item.store_logo || 'https://cdn-icons-png.flaticon.com/512/825/825573.png',
                    items: []
                };
            }
            itemsByStore[item.store_id].items.push(item);
        });
        
        // Build saved items HTML
        let savedHTML = '';
        
        Object.values(itemsByStore).forEach(store => {
            // Start store section
            savedHTML += `
                <div class="saved-store" data-store-id="${store.id}">
                    <div class="saved-store-header">
                        <img src="${store.logo_url}" alt="${store.name}" class="saved-store-logo">
                        <span class="saved-store-name">${store.name}</span>
                    </div>
                    <div class="saved-items">
            `;
            
            // Add store items
            store.items.forEach(item => {
                const itemPrice = item.is_on_sale ? item.sale_price : item.price;
                
                savedHTML += `
                    <div class="saved-item" data-item-id="${item.id}">
                        <img src="${item.image_url}" alt="${item.name}" class="saved-item-image">
                        <div class="saved-item-details">
                            <div class="saved-item-name">${item.name}</div>
                            <div class="saved-item-price">$${itemPrice.toFixed(2)}</div>
                            <div class="saved-item-store">${store.name}</div>
                            <div class="saved-item-actions">
                                <button class="move-to-cart-btn" onclick="Cart.moveToCart(${item.id})">Move to Cart</button>
                                <button class="remove-saved-btn" onclick="Cart.removeSavedItem(${item.id})">Remove</button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            // Close store section
            savedHTML += `
                    </div>
                </div>
            `;
        });
        
        // Update saved items container
        savedItemsContent.innerHTML = savedHTML;
    }
    
    // Save an item for later
    function saveForLater(itemId) {
        // Find item in cart
        const itemIndex = cartItems.findIndex(item => item.id === itemId);
        if (itemIndex < 0) return;
        
        // Remove from cart and add to saved items
        const item = cartItems[itemIndex];
        savedItems.push({...item, quantity: 1}); // We store quantity=1 for saved items
        
        // Remove from cart
        cartItems.splice(itemIndex, 1);
        
        // Save and update UI
        saveCart();
        saveSavedItems();
        updateCartUI();
        updateSavedItemsUI();
    }
    
    // Move item from saved items to cart
    function moveToCart(itemId) {
        // Find item in saved items
        const itemIndex = savedItems.findIndex(item => item.id === itemId);
        if (itemIndex < 0) return;
        
        // Get item and remove from saved items
        const item = savedItems[itemIndex];
        savedItems.splice(itemIndex, 1);
        
        // Check if item already exists in cart
        const cartItemIndex = cartItems.findIndex(cartItem => cartItem.id === itemId);
        if (cartItemIndex >= 0) {
            // Increase quantity in cart
            cartItems[cartItemIndex].quantity += 1;
        } else {
            // Add to cart with quantity 1
            cartItems.push({
                ...item,
                quantity: 1
            });
        }
        
        // Save and update UI
        saveCart();
        saveSavedItems();
        updateCartUI();
        updateSavedItemsUI();
    }
    
    // Remove an item from saved items
    function removeSavedItem(itemId) {
        savedItems = savedItems.filter(item => item.id !== itemId);
        saveSavedItems();
        updateSavedItemsUI();
    }
    
    // Toggle saved items panel
    function toggleSavedItems() {
        const savedItemsPanel = document.getElementById('saved-items-panel');
        const overlay = document.querySelector('.overlay');
        const cartPanel = document.getElementById('cart-panel');
        
        if (savedItemsPanel && overlay) {
            // If cart is open, close it first
            if (cartOpen && cartPanel) {
                cartPanel.classList.remove('open');
                cartOpen = false;
            }
            
            // Toggle saved items panel
            if (savedItemsOpen) {
                // Closing panel
                savedItemsPanel.style.right = '-400px';
                overlay.classList.remove('active');
                savedItemsOpen = false;
            } else {
                // Opening panel
                savedItemsPanel.style.display = 'flex';
                setTimeout(() => {
                    savedItemsPanel.style.right = '0';
                }, 10);
                overlay.classList.add('active');
                savedItemsOpen = true;
            }
            
            // Update saved items UI if opening
            if (savedItemsOpen) {
                updateSavedItemsUI();
            }
        }
    }
    
    // Public API
    return {
        init,
        addItem,
        removeItem,
        increaseQuantity,
        decreaseQuantity,
        clearCart,
        getItems,
        getUniqueStores,
        getStoreItems,
        getStoreTotal,
        toggleCart,
        // Save for Later API
        saveForLater,
        moveToCart,
        removeSavedItem,
        toggleSavedItems,
        getSavedItems: () => [...savedItems]
    };
})();

// Initialize cart when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', Cart.init);
} else {
    Cart.init();
}