/**
 * GlassRain Retailer Integration System
 * 
 * Handles integration with external retailer sites for the GlassRain platform.
 * This includes building shopping carts on retailer sites, tracking checkout events,
 * and redirecting users to complete purchases.
 */

const RetailerIntegration = (function() {
    // Store integration configurations
    const storeIntegrations = {
        // Home Depot integration
        1: {
            name: 'Home Depot',
            url: 'https://homedepot.com',
            cartBuilder: buildHomeDepotCart,
            trackingId: 'glassrain-homedepot'
        },
        // Lowe's integration
        2: {
            name: 'Lowe\'s',
            url: 'https://lowes.com',
            cartBuilder: buildLowesCart,
            trackingId: 'glassrain-lowes'
        },
        // Wayfair integration
        3: {
            name: 'Wayfair',
            url: 'https://wayfair.com',
            cartBuilder: buildWayfairCart,
            trackingId: 'glassrain-wayfair'
        },
        // IKEA integration
        4: {
            name: 'IKEA',
            url: 'https://ikea.com',
            cartBuilder: buildIkeaCart,
            trackingId: 'glassrain-ikea'
        },
        // West Elm integration
        5: {
            name: 'West Elm',
            url: 'https://westelm.com',
            cartBuilder: buildWestElmCart,
            trackingId: 'glassrain-westelm'
        },
        // Crate & Barrel integration
        6: {
            name: 'Crate & Barrel',
            url: 'https://crateandbarrel.com',
            cartBuilder: buildCrateAndBarrelCart,
            trackingId: 'glassrain-crateandbarrel'
        },
        // Menards integration
        1604: {
            name: 'Menards',
            url: 'https://menards.com',
            cartBuilder: buildMenardsCart,
            trackingId: 'glassrain-menards'
        },
        // Ace Hardware integration
        1605: {
            name: 'Ace Hardware',
            url: 'https://acehardware.com',
            cartBuilder: buildAceHardwareCart,
            trackingId: 'glassrain-acehardware'
        },
        // RONA integration
        1606: {
            name: 'RONA',
            url: 'https://rona.ca',
            cartBuilder: buildRonaCart,
            trackingId: 'glassrain-rona'
        },
        // Floor & Decor integration
        1607: {
            name: 'Floor & Decor',
            url: 'https://flooranddecor.com',
            cartBuilder: buildFloorAndDecorCart,
            trackingId: 'glassrain-flooranddecor'
        },
        // Build.com integration
        1608: {
            name: 'Build.com',
            url: 'https://build.com',
            cartBuilder: buildBuildDotComCart,
            trackingId: 'glassrain-buildcom'
        },
        // CB2 integration
        1613: {
            name: 'CB2',
            url: 'https://cb2.com',
            cartBuilder: buildCB2Cart,
            trackingId: 'glassrain-cb2'
        },
        // Restoration Hardware integration
        1614: {
            name: 'Restoration Hardware',
            url: 'https://restorationhardware.com',
            cartBuilder: buildRestorationHardwareCart,
            trackingId: 'glassrain-restorationhardware'
        },
        // Green Depot integration
        1615: {
            name: 'Green Depot',
            url: 'https://greendepot.com',
            cartBuilder: buildGreenDepotCart,
            trackingId: 'glassrain-greendepot'
        },
        // Habitat ReStore integration
        1616: {
            name: 'Habitat ReStore',
            url: 'https://habitat.org/restores',
            cartBuilder: buildHabitatReStoreCart,
            trackingId: 'glassrain-habitatrestore'
        },
        // Rejuvenation integration
        1617: {
            name: 'Rejuvenation',
            url: 'https://rejuvenation.com',
            cartBuilder: buildRejuvenationCart,
            trackingId: 'glassrain-rejuvenation'
        },
        // The Tile Shop integration
        1618: {
            name: 'The Tile Shop',
            url: 'https://tileshop.com',
            cartBuilder: buildTileShopCart,
            trackingId: 'glassrain-tileshop'
        },
        // Houzz integration
        1619: {
            name: 'Houzz',
            url: 'https://houzz.com',
            cartBuilder: buildHouzzCart,
            trackingId: 'glassrain-houzz'
        },
        // Overstock integration
        1620: {
            name: 'Overstock',
            url: 'https://overstock.com',
            cartBuilder: buildOverstockCart,
            trackingId: 'glassrain-overstock'
        },
        // Target integration
        1621: {
            name: 'Target',
            url: 'https://target.com',
            cartBuilder: buildTargetCart,
            trackingId: 'glassrain-target'
        },
        // Amazon Home integration
        1622: {
            name: 'Amazon Home',
            url: 'https://amazon.com',
            cartBuilder: buildAmazonCart,
            trackingId: 'glassrain-amazon'
        },
        // Costco integration
        1623: {
            name: 'Costco',
            url: 'https://costco.com',
            cartBuilder: buildCostcoCart,
            trackingId: 'glassrain-costco'
        }
    };
    
    // Redirect user to retailer checkout with cart items
    function redirectToStoreCheckout(storeId) {
        // Get store configuration
        const store = storeIntegrations[storeId];
        if (!store) {
            console.error(`No integration configured for store ID ${storeId}`);
            return;
        }
        
        // Get cart items for this store
        const items = Cart.getStoreItems(storeId);
        if (!items || items.length === 0) {
            console.error(`No items in cart for store ID ${storeId}`);
            return;
        }
        
        // Build cart URL for this store
        const cartUrl = store.cartBuilder(items, store);
        
        // Track checkout event
        trackCheckoutEvent(storeId, items, store);
        
        // Redirect to store
        window.open(cartUrl, '_blank');
    }
    
    // IKEA cart builder
    function buildIkeaCart(items, store) {
        // In a real implementation, this would build a URL with product parameters
        // that automatically adds items to the IKEA cart
        
        // Example: https://ikea.com/cart?items=123456,234567&quantities=1,2
        let url = `${store.url}/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `items=${productIds.join(',')}&quantities=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Home Depot cart builder
    function buildHomeDepotCart(items, store) {
        // Example: https://homedepot.com/mycart/recommend?ids=123456,234567&qtys=1,2
        let url = `${store.url}/mycart/recommend?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `ids=${productIds.join(',')}&qtys=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Lowe's cart builder
    function buildLowesCart(items, store) {
        // Example: https://lowes.com/cart?id=123456,234567&qty=1,2
        let url = `${store.url}/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `id=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Wayfair cart builder
    function buildWayfairCart(items, store) {
        // Example: https://wayfair.com/cart/add?sku=123456,234567&qty=1,2
        let url = `${store.url}/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `sku=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Amazon cart builder
    function buildAmazonCart(items, store) {
        // Example: https://amazon.com/gp/aws/cart/add.html?ASIN.1=123456&Quantity.1=1&ASIN.2=234567&Quantity.2=2
        let url = `${store.url}/gp/aws/cart/add.html?`;
        
        // Add product IDs and quantities
        let params = [];
        items.forEach((item, index) => {
            const productId = extractProductId(item.product_url);
            if (productId) {
                params.push(`ASIN.${index+1}=${productId}`);
                params.push(`Quantity.${index+1}=${item.quantity}`);
            }
        });
        
        url += params.join('&');
        
        // Add tracking parameters
        url += `&AssociateTag=${store.trackingId}`;
        
        return url;
    }

    // West Elm cart builder
    function buildWestElmCart(items, store) {
        // Example: https://westelm.com/shoppingcart/addItems.html?id=123456,234567&qty=1,2
        let url = `${store.url}/shoppingcart/addItems.html?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `id=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Crate & Barrel cart builder
    function buildCrateAndBarrelCart(items, store) {
        // Example: https://crateandbarrel.com/checkout/cart?skuId=123456,234567&quantity=1,2
        let url = `${store.url}/checkout/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `skuId=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Menards cart builder
    function buildMenardsCart(items, store) {
        // Example: https://menards.com/main/cart.html?items=123456,234567&qty=1,2
        let url = `${store.url}/main/cart.html?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `items=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Ace Hardware cart builder
    function buildAceHardwareCart(items, store) {
        // Example: https://acehardware.com/cart/add?productId=123456,234567&quantity=1,2
        let url = `${store.url}/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `productId=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // RONA cart builder
    function buildRonaCart(items, store) {
        // Example: https://rona.ca/cart/add?skuIds=123456,234567&quantities=1,2
        let url = `${store.url}/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `skuIds=${productIds.join(',')}&quantities=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Floor & Decor cart builder
    function buildFloorAndDecorCart(items, store) {
        // Example: https://flooranddecor.com/cart?sku=123456,234567&quantity=1,2
        let url = `${store.url}/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `sku=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Build.com cart builder
    function buildBuildDotComCart(items, store) {
        // Example: https://build.com/cart/add?sku=123456,234567&qty=1,2
        let url = `${store.url}/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `sku=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // CB2 cart builder
    function buildCB2Cart(items, store) {
        // Example: https://cb2.com/checkout/cart?itemId=123456,234567&quantity=1,2
        let url = `${store.url}/checkout/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `itemId=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Restoration Hardware cart builder
    function buildRestorationHardwareCart(items, store) {
        // Example: https://restorationhardware.com/checkout/cart.jsp?productId=123456,234567&quantity=1,2
        let url = `${store.url}/checkout/cart.jsp?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `productId=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Green Depot cart builder
    function buildGreenDepotCart(items, store) {
        // Example: https://greendepot.com/cart.php?a=add&pid=123456,234567&qty=1,2
        let url = `${store.url}/cart.php?a=add&`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `pid=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Habitat ReStore cart builder
    function buildHabitatReStoreCart(items, store) {
        // Example: https://habitat.org/restores/shop/cart?item=123456,234567&qty=1,2
        let url = `${store.url}/shop/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `item=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Rejuvenation cart builder
    function buildRejuvenationCart(items, store) {
        // Example: https://rejuvenation.com/shop/cart?sku=123456,234567&quantity=1,2
        let url = `${store.url}/shop/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `sku=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // The Tile Shop cart builder
    function buildTileShopCart(items, store) {
        // Example: https://tileshop.com/en/cart/add?id=123456,234567&quantity=1,2
        let url = `${store.url}/en/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `id=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Houzz cart builder
    function buildHouzzCart(items, store) {
        // Example: https://houzz.com/cart/add?productId=123456,234567&qty=1,2
        let url = `${store.url}/cart/add?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `productId=${productIds.join(',')}&qty=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Overstock cart builder
    function buildOverstockCart(items, store) {
        // Example: https://overstock.com/cart?productid=123456,234567&quantity=1,2
        let url = `${store.url}/cart?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `productid=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Target cart builder
    function buildTargetCart(items, store) {
        // Example: https://target.com/s?searchTerm=addtocart&tcin=123456,234567&quantity=1,2
        let url = `${store.url}/s?searchTerm=addtocart&`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `tcin=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }

    // Costco cart builder
    function buildCostcoCart(items, store) {
        // Example: https://costco.com/CheckoutCartDisplayView?productId=123456,234567&quantity=1,2
        let url = `${store.url}/CheckoutCartDisplayView?`;
        
        // Add product IDs and quantities
        const productIds = items.map(item => extractProductId(item.product_url)).filter(id => id);
        const quantities = items.map(item => item.quantity);
        
        if (productIds.length > 0) {
            url += `productId=${productIds.join(',')}&quantity=${quantities.join(',')}`;
        }
        
        // Add tracking parameters
        url += `&source=${store.trackingId}`;
        
        return url;
    }
    
    // Extract product ID from product URL
    function extractProductId(url) {
        if (!url) return null;
        
        try {
            // Extract product IDs based on retailer URL patterns
            
            // IKEA product ID: https://www.ikea.com/us/en/p/billy-bookcase-white-00263850/
            if (url.includes('ikea.com')) {
                const match = url.match(/p\/[\w-]+-(\d+)\/?$/);
                return match ? match[1] : null;
            }
            
            // Home Depot product ID: https://www.homedepot.com/p/example-led-ceiling-light/123456789
            if (url.includes('homedepot.com')) {
                const match = url.match(/\/p\/[\w-]+\/(\d+)\/?$/);
                return match ? match[1] : null;
            }
            
            // Lowe's product ID: https://www.lowes.com/pd/example-floor-lamp/9876543210
            if (url.includes('lowes.com')) {
                const match = url.match(/\/pd\/[\w-]+\/(\d+)\/?$/);
                return match ? match[1] : null;
            }
            
            // Wayfair product ID: https://www.wayfair.com/furniture/pdp/example-velvet-sofa.html
            if (url.includes('wayfair.com')) {
                const match = url.match(/pdp\/([\w-]+)\.html/);
                return match ? match[1] : null;
            }
            
            // Amazon product ID: https://www.amazon.com/example-coffee-table/dp/B0123456789
            if (url.includes('amazon.com')) {
                const match = url.match(/\/dp\/([A-Z0-9]+)/);
                return match ? match[1] : null;
            }

            // West Elm product ID: https://www.westelm.com/products/mid-century-desk-h1499/
            if (url.includes('westelm.com')) {
                const match = url.match(/\/products\/[\w-]+-([a-zA-Z0-9]+)\/?$/);
                return match ? match[1] : null;
            }

            // Crate & Barrel product ID: https://www.crateandbarrel.com/lounge-ii-sofa/s412371
            if (url.includes('crateandbarrel.com')) {
                const match = url.match(/\/([\w-]+)\/s(\d+)\/?$/);
                return match ? match[2] : null;
            }

            // Menards product ID: https://www.menards.com/main/p-1234567.htm
            if (url.includes('menards.com')) {
                const match = url.match(/p-(\d+)\.htm/);
                return match ? match[1] : null;
            }

            // Ace Hardware product ID: https://www.acehardware.com/p/12345
            if (url.includes('acehardware.com')) {
                const match = url.match(/\/p\/(\d+)/);
                return match ? match[1] : null;
            }

            // RONA product ID: https://www.rona.ca/en/product/example-product-12345678
            if (url.includes('rona.ca')) {
                const match = url.match(/product\/[\w-]+-(\d+)/);
                return match ? match[1] : null;
            }

            // Floor & Decor product ID: https://www.flooranddecor.com/tile-samples/example-ceramic-tile-123456.html
            if (url.includes('flooranddecor.com')) {
                const match = url.match(/[\w-]+-(\d+)\.html/);
                return match ? match[1] : null;
            }

            // Build.com product ID: https://www.build.com/product/detail/1234567
            if (url.includes('build.com')) {
                const match = url.match(/product\/detail\/(\d+)/);
                return match ? match[1] : null;
            }

            // CB2 product ID: https://www.cb2.com/product/detail/s12345
            if (url.includes('cb2.com')) {
                const match = url.match(/detail\/(s\d+)/);
                return match ? match[1] : null;
            }

            // Restoration Hardware product ID: https://rh.com/catalog/product/product.jsp?productId=prod12345
            if (url.includes('restorationhardware.com') || url.includes('rh.com')) {
                const match = url.match(/productId=prod(\d+)/);
                return match ? match[1] : null;
            }

            // Green Depot product ID: https://www.greendepot.com/products/example-product-12345
            if (url.includes('greendepot.com')) {
                const match = url.match(/products\/[\w-]+-(\d+)/);
                return match ? match[1] : null;
            }

            // Habitat ReStore product ID: https://www.habitat.org/restores/shop/item/12345
            if (url.includes('habitat.org/restores')) {
                const match = url.match(/item\/(\d+)/);
                return match ? match[1] : null;
            }

            // Rejuvenation product ID: https://www.rejuvenation.com/catalog/products/example-product/f1234
            if (url.includes('rejuvenation.com')) {
                const match = url.match(/products\/[\w-]+\/(f\d+)/);
                return match ? match[1] : null;
            }

            // The Tile Shop product ID: https://www.tileshop.com/product/123456.do
            if (url.includes('tileshop.com')) {
                const match = url.match(/product\/(\d+)\.do/);
                return match ? match[1] : null;
            }

            // Houzz product ID: https://www.houzz.com/products/example-product-prvw-prv12345
            if (url.includes('houzz.com')) {
                const match = url.match(/prvw-prv(\d+)/);
                return match ? match[1] : null;
            }

            // Overstock product ID: https://www.overstock.com/Home-Garden/example-product/12345678/product.html
            if (url.includes('overstock.com')) {
                const match = url.match(/\/(\d+)\/product\.html/);
                return match ? match[1] : null;
            }

            // Target product ID: https://www.target.com/p/example-product/-/A-12345678
            if (url.includes('target.com')) {
                const match = url.match(/\/A-(\d+)/);
                return match ? match[1] : null;
            }

            // Costco product ID: https://www.costco.com/example-product.product.1234567.html
            if (url.includes('costco.com')) {
                const match = url.match(/product\.(\d+)\.html/);
                return match ? match[1] : null;
            }
            
            // Fallback: use the last segment of the URL path
            const urlObj = new URL(url);
            const pathSegments = urlObj.pathname.split('/').filter(segment => segment.length > 0);
            return pathSegments[pathSegments.length - 1];
        } catch (e) {
            console.error('Error extracting product ID:', e);
            return null;
        }
    }
    
    // Track checkout event
    function trackCheckoutEvent(storeId, items, store) {
        // Prepare checkout data
        const checkoutData = {
            store_id: storeId,
            store_name: store.name,
            products: items.map(item => ({
                id: item.id,
                name: item.name,
                price: item.is_on_sale ? item.sale_price : item.price,
                quantity: item.quantity
            })),
            total_value: items.reduce((total, item) => {
                const price = item.is_on_sale ? item.sale_price : item.price;
                return total + (price * item.quantity);
            }, 0),
            timestamp: new Date().toISOString()
        };
        
        // Log checkout event
        console.log('Checkout event:', checkoutData);
        
        // Send checkout data to API if available
        try {
            fetch('/api/track_checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(checkoutData)
            }).catch(error => {
                console.log('Error tracking checkout event (this is normal if tracking endpoint is not implemented)');
            });
        } catch (e) {
            console.log('Error tracking checkout event:', e);
        }
    }
    
    // Public API
    return {
        redirectToStoreCheckout,
        extractProductId
    };
})();