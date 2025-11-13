# Architecture Diagram - New Features

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                         (Frontend)                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  Home Page    │        │  Orders Page  │        │ Customer      │
│  (index.html) │        │  (Modal)      │        │ Service       │
│               │        │               │        │ (chat.html)   │
│  - Products   │        │  - Order List │        │               │
│  - Filters    │        │  - Cancel Btn │        │  - Chat UI    │
│  - Cart       │        │               │        │  - Help Modal │
└───────────────┘        └───────────────┘        └───────────────┘
        │                         │                         │
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND SERVICES                              │
│                      (JavaScript)                                   │
├─────────────────────────────────────────────────────────────────────┤
│  main.js                 │  chat.js                                 │
│  - Filter logic          │  - Chat management                       │
│  - Cart management       │  - Help modal                            │
│  - Order display         │  - Session handling                      │
│  - Cancel order          │                                          │
│                          │                                          │
│  apiService.js                                                      │
│  - HTTP requests                                                    │
│  - Streaming support                                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTP/REST API
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND API                                    │
│                      (FastAPI)                                      │
├─────────────────────────────────────────────────────────────────────┤
│  main.py                                                            │
│  - App initialization                                               │
│  - CORS configuration                                               │
│  - Router registration                                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  Products    │  │  Orders      │  │  Chat Agent  │
        │  Router      │  │  Router      │  │  (ADK)       │
        │              │  │              │  │              │
        │  GET /       │  │  POST /create│  │  POST /run   │
        │  POST /      │  │  GET /user   │  │  GET /session│
        │  PUT /       │  │  GET /track  │  │              │
        │  DELETE /    │  │  POST /cancel│  │              │
        └──────────────┘  └──────────────┘  └──────────────┘
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
│                      (SQLite Database)                              │
├─────────────────────────────────────────────────────────────────────┤
│  products.db                                                        │
│  ├── products        (product catalog)                              │
│  ├── orders          (order records)                                │
│  ├── payments        (payment transactions)                         │
│  ├── order_tracking  (delivery status)                              │
│  ├── sellers         (seller information)                           │
│  ├── wishlist        (user wishlists)                               │
│  ├── reviews         (product reviews)                              │
│  └── coupons         (discount coupons)                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Feature Flow Diagrams

### 1. Category & Filter Flow

```
User Action                Frontend                    Backend
─────────────────────────────────────────────────────────────────

[Select Category]
      │
      ├──> Load all products ──────> GET /products
      │                                    │
      │                                    ▼
      │                              [Return products]
      │                                    │
      ├──< Populate dropdowns <────────────┘
      │
[Select Price Range]
      │
[Select Badge]
      │
[Click Apply]
      │
      ├──> Filter products (client-side)
      │         │
      │         ├─ Filter by category
      │         ├─ Filter by price
      │         └─ Filter by badge
      │
      ├──> Update UI
      │
      └──> Show filtered results
```

### 2. Order Cancellation Flow

```
User Action                Frontend                    Backend
─────────────────────────────────────────────────────────────────

[Click My Orders]
      │
      ├──> Load orders from localStorage
      │
      └──> Display orders with cancel buttons
            (only for eligible orders)
      
[Click Cancel Order]
      │
      ├──> Show confirmation dialog
      │
[Confirm]
      │
      ├──> POST /orders/cancel/{id} ──────> Validate order
      │                                           │
      │                                           ├─ Check exists
      │                                           ├─ Check status
      │                                           │
      │                                           ▼
      │                                     Update status
      │                                           │
      │                                           ▼
      │                                     UPDATE orders
      │                                     SET status='Cancelled'
      │                                           │
      │    <────────── Return success ────────────┘
      │
      ├──> Update localStorage
      │
      ├──> Update UI
      │
      └──> Show success toast
```

### 3. Customer Service Chat Flow

```
User Action                Frontend                    Backend
─────────────────────────────────────────────────────────────────

[Click Customer Service]
      │
      ├──> Load chat.html
      │
      ├──> GET /sessions ──────────────> List sessions
      │                                        │
      │    <────────── Return sessions ────────┘
      │
      └──> Display chat interface

[Click Help Button]
      │
      └──> Show help modal
            (no backend call)

[Type Message]
      │
[Press Send]
      │
      ├──> POST /run_sse ──────────────> Process message
      │         │                              │
      │         │                              ├─ Parse intent
      │         │                              ├─ Call tools
      │         │                              ├─ Generate response
      │         │                              │
      │    <────┴──── Stream response ─────────┘
      │         (Server-Sent Events)
      │
      └──> Display response in chat
```

---

## Component Interaction Matrix

```
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│ Component    │ Filters  │ Cancel   │ Chat     │ Database │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│ index.html   │    ✓     │    ✓     │    -     │    -     │
│ chat.html    │    -     │    -     │    ✓     │    -     │
│ main.js      │    ✓     │    ✓     │    -     │    -     │
│ chat.js      │    -     │    -     │    ✓     │    -     │
│ apiService.js│    ✓     │    ✓     │    ✓     │    -     │
│ products.py  │    ✓     │    -     │    -     │    ✓     │
│ orders.py    │    -     │    ✓     │    -     │    ✓     │
│ main.py      │    ✓     │    ✓     │    ✓     │    -     │
│ products.db  │    ✓     │    ✓     │    ✓     │    ✓     │
└──────────────┴──────────┴──────────┴──────────┴──────────┘

Legend: ✓ = Direct interaction, - = No interaction
```

---

## Data Flow

### Filter Data Flow
```
Products DB → Backend API → Frontend → Filter Logic → Filtered View
     ↓                                      ↓
  [Read]                              [Client-side]
```

### Order Cancellation Data Flow
```
User Input → Frontend → Backend API → Database → Response
                            ↓            ↓
                      [Validate]    [Update]
```

### Chat Data Flow
```
User Message → Frontend → Backend API → AI Agent → Tools → Database
                              ↓           ↓          ↓
                         [Stream]    [Process]  [Execute]
                              ↓
                         Frontend ← Response
```

---

## File Structure

```
Los_codigos_782/
│
├── frontend/
│   ├── index.html                 [✓ Modified - Added filters]
│   ├── pages/
│   │   └── chat.html              [✓ Modified - Customer service]
│   ├── scripts/
│   │   ├── main.js                [✓ Modified - Filters & cancel]
│   │   └── chat.js                [✓ Modified - Help modal]
│   ├── services/
│   │   └── apiService.js          [Existing - Used by all]
│   └── styles/
│       ├── main.css               [✓ Modified - Filter styles]
│       └── chat.css               [✓ Modified - Help modal styles]
│
├── backend/
│   ├── main.py                    [Existing - No changes]
│   ├── routers/
│   │   ├── products.py            [Existing - No changes]
│   │   └── orders.py              [✓ Modified - Cancel endpoint]
│   ├── models/
│   │   └── data_models.py         [Existing - No changes]
│   ├── repos/
│   │   └── products_repo.py       [Existing - Has update_order_status]
│   └── services/
│       └── product_service.py     [Existing - No changes]
│
└── Documentation/
    ├── NEW_FEATURES.md            [✓ Created]
    ├── QUICK_START_GUIDE.md       [✓ Created]
    ├── IMPLEMENTATION_SUMMARY.md  [✓ Created]
    ├── ARCHITECTURE_DIAGRAM.md    [✓ Created - This file]
    └── FEATURES.md                [✓ Updated]
```

---

## API Endpoints

### Existing Endpoints (Used by new features)
```
GET    /products                    - Get all products (for filters)
POST   /products                    - Create product
PUT    /products                    - Update product
DELETE /products/{id}               - Delete product

POST   /orders/create               - Create order
GET    /orders/user/{user_id}       - Get user orders
GET    /orders/track/{order_id}     - Track order

POST   /run_sse                     - Chat with AI agent
GET    /apps/{agent}/users/{user}/sessions - List chat sessions
```

### New Endpoints
```
POST   /orders/cancel/{order_id}    - Cancel order [NEW]
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                      │
│  HTML5 │ CSS3 │ JavaScript ES6+ │ Font Awesome             │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                       │
│  FastAPI │ Pydantic │ Google ADK │ Uvicorn                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
│  SQLite │ aiosqlite │ SQL                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

```
Frontend                    Backend                     Database
────────                    ───────                     ────────
│                           │                           │
├─ Input validation        ├─ Request validation       ├─ Parameterized queries
├─ XSS prevention          ├─ Authentication (future)  ├─ Access control
├─ CSRF protection         ├─ Authorization checks     ├─ Data encryption
└─ Secure storage          └─ Rate limiting (future)   └─ Backup strategy
```

---

## Performance Optimization

```
Client-Side Filtering
─────────────────────
✓ No API calls for filters
✓ Instant results
✓ Reduced server load
✓ Better UX

Efficient Cancellation
──────────────────────
✓ Single API call
✓ Optimistic UI updates
✓ Error handling
✓ Toast notifications

Streaming Chat
──────────────
✓ Server-Sent Events
✓ Real-time responses
✓ Progressive rendering
✓ Better perceived performance
```

---

## Scalability Path

```
Current Architecture        Future Enhancements
────────────────────        ───────────────────
│                           │
├─ Client-side filtering    ├─ Server-side filtering with pagination
├─ SQLite database          ├─ PostgreSQL/MySQL
├─ Single server            ├─ Load balancer + multiple servers
├─ Local storage            ├─ Redis cache
└─ Synchronous operations   └─ Message queue (RabbitMQ/Kafka)
```

---

## Monitoring & Logging

```
Frontend Logging            Backend Logging             Database Logging
────────────────            ───────────────             ────────────────
│                           │                           │
├─ Console errors           ├─ Request logs             ├─ Query logs
├─ User actions             ├─ Error tracking           ├─ Performance metrics
├─ Performance metrics      ├─ API metrics              ├─ Connection pool
└─ Analytics events         └─ Security events          └─ Backup logs
```

---

This architecture diagram provides a comprehensive view of how all the new features integrate with the existing system. The design emphasizes:

1. **Separation of Concerns**: Clear boundaries between frontend, backend, and data layers
2. **Scalability**: Client-side filtering reduces server load
3. **Maintainability**: Modular design with clear responsibilities
4. **User Experience**: Fast, responsive interactions
5. **Security**: Input validation and error handling at all layers

**Last Updated**: January 2025
