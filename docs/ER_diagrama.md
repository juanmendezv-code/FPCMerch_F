# Modelo entidad-relación de FPCMerch

```mermaid
erDiagram
    USER ||--o{ ORDER : realiza
    USER ||--o| CART : conserva
    CATEGORY ||--o{ PRODUCT : agrupa
    PRODUCT ||--o{ PRODUCT_SIZE : ofrece
    CART ||--o{ CART_ITEM : contiene
    PRODUCT_SIZE ||--o{ CART_ITEM : selecciona
    ORDER ||--|{ ORDER_ITEM : incluye
    PRODUCT ||--o{ ORDER_ITEM : referencia

    USER {
        bigint id PK
        string email UK
        string first_name
        string last_name
        string telefono
        string ciudad
    }
    CATEGORY {
        bigint id PK
        string name UK
        string slug UK
        string icon
        smallint order
    }
    PRODUCT {
        bigint id PK
        string name
        string slug UK
        string sku UK
        decimal price
        bigint category_id FK
        boolean is_active
        boolean is_featured
    }
    PRODUCT_SIZE {
        bigint id PK
        bigint product_id FK
        string size
        int stock
    }
    CART {
        bigint id PK
        bigint user_id FK_UK
    }
    CART_ITEM {
        bigint id PK
        bigint cart_id FK
        bigint variant_id FK
        int quantity
    }
    ORDER {
        bigint id PK
        bigint user_id FK
        string number UK
        string status
        decimal subtotal
        decimal shipping_cost
        decimal total
    }
    ORDER_ITEM {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        string size
        int quantity
        decimal unit_price
    }
```

`Category` agrupa muchos `Product`; un `Product` tiene una o más variantes `ProductSize`. Cada usuario puede tener un carrito persistido con varias líneas; los visitantes guardan las variantes y cantidades en la sesión. `OrderItem` conserva el precio unitario al momento de comprar. La relación `OrderItem → Product` usa `PROTECT`, así un producto con historial no se elimina físicamente. `ContactMessage` es independiente y no guarda una referencia de usuario.
